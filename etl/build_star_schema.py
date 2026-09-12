import pandas as pd
import numpy as np

RAW = "/home/claude/olist/raw/"
OUT = "/home/claude/olist/powerbi_data/"

orders = pd.read_csv(RAW+"olist_orders_dataset.csv")
items = pd.read_csv(RAW+"olist_order_items_dataset.csv")
payments = pd.read_csv(RAW+"olist_order_payments_dataset.csv")
reviews = pd.read_csv(RAW+"olist_order_reviews_dataset.csv")
customers = pd.read_csv(RAW+"olist_customers_dataset.csv")
products = pd.read_csv(RAW+"olist_products_dataset.csv")
sellers = pd.read_csv(RAW+"olist_sellers_dataset.csv")
cat_translation = pd.read_csv(RAW+"product_category_name_translation.csv")

# ---- Clean orders: parse dates ----
date_cols = ["order_purchase_timestamp","order_approved_at","order_delivered_carrier_date",
             "order_delivered_customer_date","order_estimated_delivery_date"]
for c in date_cols:
    orders[c] = pd.to_datetime(orders[c], errors="coerce")

# Only keep orders that are "delivered" for delivery-performance analysis, but keep all for order volume/status
orders["delivery_days_actual"] = (orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]).dt.days
orders["delivery_days_estimated"] = (orders["order_estimated_delivery_date"] - orders["order_purchase_timestamp"]).dt.days
orders["delay_vs_estimate_days"] = (orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]).dt.days
orders["is_late"] = orders["delay_vs_estimate_days"] > 0
orders["is_delivered"] = orders["order_status"] == "delivered"
orders["purchase_date_key"] = orders["order_purchase_timestamp"].dt.date

# ---- Products: translate category to English ----
products = products.merge(cat_translation, on="product_category_name", how="left")
products["product_category_name_english"] = products["product_category_name_english"].fillna("unknown")
dim_products = products[["product_id","product_category_name_english","product_weight_g",
                          "product_length_cm","product_height_cm","product_width_cm"]].rename(
                          columns={"product_category_name_english":"product_category"})

# ---- Customers / Sellers dims ----
dim_customers = customers[["customer_id","customer_unique_id","customer_city","customer_state"]]
dim_sellers = sellers[["seller_id","seller_city","seller_state"]]

# ---- Fact: order items (grain = 1 row per item) ----
fact_items = items.merge(orders[["order_id","customer_id","order_status","order_purchase_timestamp",
                                  "is_late","is_delivered","delivery_days_actual","delay_vs_estimate_days"]],
                          on="order_id", how="left")
fact_items = fact_items.merge(dim_products, on="product_id", how="left")
fact_items["order_item_revenue"] = fact_items["price"] + fact_items["freight_value"]

# ---- Fact: payments (grain = 1 row per payment installment record) ----
fact_payments = payments.copy()

# ---- Fact: reviews ----
for c in ["review_creation_date","review_answer_timestamp"]:
    reviews[c] = pd.to_datetime(reviews[c], errors="coerce")
reviews["review_response_days"] = (reviews["review_answer_timestamp"] - reviews["review_creation_date"]).dt.days
fact_reviews = reviews[["review_id","order_id","review_score","review_response_days"]]

# ---- Dim: orders (order-level grain, for delivery analysis / order count measures) ----
dim_orders = orders[["order_id","customer_id","order_status","order_purchase_timestamp",
                      "order_approved_at","order_delivered_carrier_date","order_delivered_customer_date",
                      "order_estimated_delivery_date","delivery_days_actual","delivery_days_estimated",
                      "delay_vs_estimate_days","is_late","is_delivered"]]

# ---- Seller performance summary (core analysis table for the "delivery risk -> revenue" story) ----
order_seller = items[["order_id","seller_id","price","freight_value"]].merge(
    orders[["order_id","is_late","is_delivered","order_status"]], on="order_id", how="left")
order_seller_rev = order_seller.merge(fact_reviews[["order_id","review_score"]], on="order_id", how="left")

seller_perf = order_seller_rev.groupby("seller_id").agg(
    total_orders=("order_id","nunique"),
    total_revenue=("price","sum"),
    total_freight=("freight_value","sum"),
    late_orders=("is_late","sum"),
    delivered_orders=("is_delivered","sum"),
    avg_review_score=("review_score","mean"),
).reset_index()
seller_perf["late_delivery_rate"] = (seller_perf["late_orders"] / seller_perf["delivered_orders"]).round(4)
seller_perf["revenue_at_risk"] = (seller_perf["late_orders"] / seller_perf["delivered_orders"] * seller_perf["total_revenue"]).round(2)
seller_perf = seller_perf.merge(dim_sellers, on="seller_id", how="left")

# ---- Date dimension ----
all_dates = pd.date_range(orders["order_purchase_timestamp"].min().normalize(),
                           orders["order_estimated_delivery_date"].max().normalize(), freq="D")
dim_date = pd.DataFrame({"date": all_dates})
dim_date["date_key"] = dim_date["date"].dt.date
dim_date["year"] = dim_date["date"].dt.year
dim_date["month"] = dim_date["date"].dt.month
dim_date["month_name"] = dim_date["date"].dt.strftime("%b")
dim_date["year_month"] = dim_date["date"].dt.strftime("%Y-%m")
dim_date["quarter"] = dim_date["date"].dt.quarter
dim_date["day_of_week"] = dim_date["date"].dt.day_name()
dim_date = dim_date.drop(columns=["date"])

# ---- Write outputs ----
fact_items.to_csv(OUT+"fact_order_items.csv", index=False)
dim_orders.to_csv(OUT+"dim_orders.csv", index=False)
fact_payments.to_csv(OUT+"fact_payments.csv", index=False)
fact_reviews.to_csv(OUT+"fact_reviews.csv", index=False)
dim_customers.to_csv(OUT+"dim_customers.csv", index=False)
dim_products.to_csv(OUT+"dim_products.csv", index=False)
dim_sellers.to_csv(OUT+"dim_sellers.csv", index=False)
seller_perf.to_csv(OUT+"seller_performance_summary.csv", index=False)
dim_date.to_csv(OUT+"dim_date.csv", index=False)

print("Rows written:")
for name, df in [("fact_order_items",fact_items), ("dim_orders",dim_orders), ("fact_payments",fact_payments),
                  ("fact_reviews",fact_reviews), ("dim_customers",dim_customers), ("dim_products",dim_products),
                  ("dim_sellers",dim_sellers), ("seller_performance_summary",seller_perf), ("dim_date",dim_date)]:
    print(f"  {name}: {len(df):,} rows")

# Key headline stats for README / presentation
delivered = orders[orders["is_delivered"]]
late_rate = delivered["is_late"].mean()
avg_delay = delivered.loc[delivered["is_late"], "delay_vs_estimate_days"].mean()
total_rev = fact_items["order_item_revenue"].sum()
late_order_ids = delivered.loc[delivered["is_late"], "order_id"]
rev_at_risk = fact_items[fact_items["order_id"].isin(late_order_ids)]["order_item_revenue"].sum()
late_review = fact_reviews.merge(orders[["order_id","is_late"]], on="order_id", how="left")
avg_score_late = late_review.loc[late_review["is_late"]==True, "review_score"].mean()
avg_score_ontime = late_review.loc[late_review["is_late"]==False, "review_score"].mean()

with open(OUT+"key_stats.txt","w") as f:
    f.write(f"Total delivered orders: {len(delivered):,}\n")
    f.write(f"Late delivery rate: {late_rate:.2%}\n")
    f.write(f"Avg delay when late: {avg_delay:.1f} days\n")
    f.write(f"Total revenue (price+freight): R$ {total_rev:,.2f}\n")
    f.write(f"Revenue tied to late-delivered orders: R$ {rev_at_risk:,.2f} ({rev_at_risk/total_rev:.1%})\n")
    f.write(f"Avg review score - late orders: {avg_score_late:.2f}\n")
    f.write(f"Avg review score - on-time orders: {avg_score_ontime:.2f}\n")
    top_late_states = orders.merge(dim_customers[["customer_id","customer_state"]], on="customer_id").groupby("customer_state")["is_late"].mean().sort_values(ascending=False).head(5)
    f.write("\nTop 5 states by late-delivery rate:\n")
    f.write(top_late_states.to_string())

print(open(OUT+"key_stats.txt").read())
