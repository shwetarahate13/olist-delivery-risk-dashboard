# Olist Delivery Risk & Revenue Impact Dashboard

A Power BI dashboard analyzing **114,000+ orders** on the Olist Brazilian e-commerce marketplace (2016–2018) to answer one business question:

> **How much is late delivery actually costing Olist — in revenue and in customer satisfaction — and which sellers/regions are driving it?**

Built as a data/business analyst portfolio project. Source data: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/olistbr/brazilian-ecommerce) (Kaggle).

## The headline finding

| Metric | Value |
|---|---|
| Orders analyzed (delivered) | 96,478 |
| Late delivery rate | **6.8%** |
| Avg. delay when late | 10.6 days |
| Revenue tied to late-delivered orders | **R$ 1.15M (7.3% of total revenue)** |
| Avg. review score — on-time orders | **4.21 / 5** |
| Avg. review score — late orders | **2.27 / 5** |
| Worst-affected states | AL (20.6% late), MA (16.7%), SE (14.6%), PI (13.3%), CE (13.2%) |

**The takeaway:** late delivery isn't a minor operational hiccup — it nearly *halves* customer satisfaction scores and puts over a million reais of revenue at reputational risk, concentrated in a handful of states and sellers. That's a retention/logistics-investment case, not just a KPI to track.

## Who this dashboard is for

Framed as a tool for Olist's **Logistics & Seller Operations team**: which sellers to flag for review, which regions need carrier renegotiation, and what a 1-point reduction in late-delivery rate is worth in review-score recovery.

## Repo structure

```
data/                          Cleaned, analysis-ready CSVs (star schema — import these into Power BI)
  ├─ fact_order_items.csv      Grain: 1 row per item per order (price, freight, category, is_late)
  ├─ dim_orders.csv            Grain: 1 row per order (dates, delivery delay, status)
  ├─ fact_payments.csv         Grain: 1 row per payment record
  ├─ fact_reviews.csv          Grain: 1 row per review (score, response time)
  ├─ dim_customers.csv         Customer id, location
  ├─ dim_products.csv          Product id, category (English), dimensions
  ├─ dim_sellers.csv           Seller id, location
  ├─ dim_date.csv              Calendar table for time intelligence
  └─ seller_performance_summary.csv   Pre-aggregated: revenue, late rate, revenue-at-risk per seller
docs/
  ├─ data_model.md             Star schema + relationship diagram
  ├─ dax_measures.md           Every DAX measure, ready to paste into Power BI
  └─ build_guide.md            Page-by-page dashboard build checklist
screenshots/                   (add your exported dashboard screenshots here before sharing)
```

## How this was built

1. **Source data**: 9 raw Olist CSVs (orders, items, payments, reviews, customers, products, sellers).
2. **ETL (Python/pandas)**: parsed timestamps, computed `delay_vs_estimate_days` and `is_late` per order, translated product categories to English, joined reviews to delivery status, and pre-aggregated seller-level performance (`revenue_at_risk` = share of a seller's revenue sitting in late-delivered orders).
3. **Modeling (Power BI)**: star schema — `dim_orders` as the delivery-performance grain, `fact_order_items` for revenue/category analysis, connected through `order_id`; `dim_date` for time intelligence.
4. **DAX**: late-delivery rate, revenue-at-risk, review-score delta (late vs. on-time), MoM trend measures — see `docs/dax_measures.md`.

## Tools

Python (pandas) for ETL · Power BI Desktop for modeling, DAX, and visualization

## Next steps / how to reproduce

See `docs/build_guide.md` for the exact Power BI Desktop steps — import the `data/` CSVs, paste in the relationships from `docs/data_model.md`, add the measures from `docs/dax_measures.md`, and build the four pages in order.
