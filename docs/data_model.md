# Data Model — Star Schema

## Tables and grain

| Table | Type | Grain (1 row = ) | Key |
|---|---|---|---|
| `dim_orders` | Dimension (order-level facts) | one order | `order_id` |
| `fact_order_items` | Fact | one item within an order | `order_id` + `order_item_id` |
| `fact_payments` | Fact | one payment record | `order_id` + `payment_sequential` |
| `fact_reviews` | Fact | one review | `review_id` |
| `dim_customers` | Dimension | one customer | `customer_id` |
| `dim_products` | Dimension | one product | `product_id` |
| `dim_sellers` | Dimension | one seller | `seller_id` |
| `dim_date` | Dimension (calendar) | one calendar day | `date_key` |
| `seller_performance_summary` | Pre-aggregated summary | one seller | `seller_id` |

## Relationships to build in Power BI (Model view)

Go to **Model view** → drag from the "many" side to the "one" side for each:

1. `fact_order_items[order_id]` → `dim_orders[order_id]` — **Many-to-1**
2. `fact_order_items[product_id]` → `dim_products[product_id]` — **Many-to-1**
3. `fact_order_items[seller_id]` → `dim_sellers[seller_id]` — **Many-to-1**
4. `dim_orders[customer_id]` → `dim_customers[customer_id]` — **Many-to-1**
5. `fact_payments[order_id]` → `dim_orders[order_id]` — **Many-to-1**
6. `fact_reviews[order_id]` → `dim_orders[order_id]` — **Many-to-1**
7. `dim_orders[purchase_date_key]` → `dim_date[date_key]` — **Many-to-1** (mark `dim_date` as a **Date Table** via Modeling → Mark as Date Table)
8. `seller_performance_summary[seller_id]` → `dim_sellers[seller_id]` — **1-to-1**

All relationships are **single-direction** (filter flows from dimensions → facts) except none need bidirectional — keep it simple, this avoids ambiguous-filter warnings.

```
                dim_date
                    |
              dim_orders ── dim_customers
               /    |    \
   fact_order_items |   fact_reviews
       /    \        fact_payments
 dim_products dim_sellers ── seller_performance_summary
```

## Why this shape

- `dim_orders` carries the **delivery performance** fields (`is_late`, `delay_vs_estimate_days`) at the order grain — this is deliberate, since delivery is an order-level event, not an item-level one. Don't duplicate `is_late` onto `fact_order_items` beyond what's already there for convenience; filter through the relationship instead so it stays consistent.
- `seller_performance_summary` is a **pre-aggregated table**, not a raw fact — use it for the seller-ranking visuals (fast, simple) and use the live relationship path (`fact_order_items` → `dim_sellers`) when you need to slice seller revenue by category, date, or state.
