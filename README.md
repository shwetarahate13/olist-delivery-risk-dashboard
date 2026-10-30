# Olist Delivery Risk & Revenue Impact Dashboard

An analytics project on the **Olist Brazilian e-commerce marketplace** (about 99K orders, 2016 to 2018) that answers one business question:

> **How much is late delivery costing Olist in revenue and customer satisfaction, and which states and sellers are driving it?**

Built as a data/business analyst portfolio project with **Python (pandas)** for data preparation and **Tableau** for the dashboards. A Power BI build guide is included as an alternative.

**Live dashboard:** [View on Tableau Public](PASTE-YOUR-TABLEAU-PUBLIC-LINK-HERE)

![Executive Overview](screenshots/01-executive-overview.png)

## Key findings

| Metric | Value |
|---|---|
| Delivered orders analyzed | 96,478 |
| Late delivery rate | **6.8%** |
| Average delay when late | 10.6 days |
| Revenue on late-delivered orders | **about R$1.15M (7.3% of total revenue)** |
| Average review score, on-time orders | **about 4.2 / 5** |
| Average review score, late orders | **about 2.3 / 5** |
| Worst states by late rate | AL (about 21%), MA (17%), SE (15%), PI (13%), CE (13%) |

**Takeaway:** late delivery is more than an operations metric. It nearly halves customer satisfaction and puts over a million reais of revenue at risk, concentrated in a handful of north-eastern states and a short list of sellers. That makes it a targeted logistics and seller-management problem, not a company-wide one.

## Who this is for

Framed as a decision tool for Olist's **Logistics and Seller Operations team**: which regions need carrier attention, which sellers to review first, and what reducing late deliveries would be worth.

## What's in the dashboard

The Tableau workbook has **13 sheets arranged into 4 dashboards**.

| Dashboard | Question it answers | Sheets |
|---|---|---|
| 1. Executive Overview | How big is the problem? | 5 KPI cards (Revenue, Orders, Late Rate, Revenue at Risk, Review Gap) and Monthly Trend |
| 2. Delivery Risk Deep Dive | Where is it happening? | State Map, State Ranking, Category Risk, Review Compare |
| 3. Seller Performance | Who is causing it? | Seller Scatter, Seller Table |
| 4. What-If / Recommendation | What is fixing it worth? | Scenario Card with an adjustable reduction slider |

A one-page summary of every sheet is in `docs/tableau_13_sheets.xlsx`.

## Repository structure

```
data/
  olist_tableau_flat.csv            Single pre-joined table used by the Tableau workbook (112,650 rows)
  fact_order_items.csv              Star-schema tables used by the Power BI version
  dim_orders.csv, dim_customers.csv, dim_products.csv, dim_sellers.csv,
  dim_date.csv, fact_payments.csv, fact_reviews.csv, seller_performance_summary.csv
docs/
  tableau_guide.md                  Calculated fields, sheets and dashboard layouts for Tableau
  tableau_13_sheets.xlsx            Summary of all 13 sheets and which dashboard each belongs to
  data_model.md, dax_measures.md, build_guide.md, presentation_outline.md   Power BI version
etl/
  build_star_schema.py              Python script that builds the cleaned tables from the raw Olist files
screenshots/                        Exported dashboard images
```

## Method

1. **Source data:** the public [Brazilian E-Commerce Dataset by Olist](https://www.kaggle.com/olistbr/brazilian-ecommerce) from Kaggle (orders, items, reviews, customers, sellers, products, category translations).
2. **Data preparation (pandas):** parsed timestamps, computed `delay_vs_estimate_days` and an `is_late` flag per order, translated product categories to English, attached review scores, and built a flat item-level table for Tableau.
3. **Analysis (Tableau):** calculated fields for late rate, revenue at risk, review score gap, and seller-level late rates using level-of-detail expressions. A parameter drives the what-if scenario.

### Design decisions worth knowing

- **Order vs item grain:** the flat table has one row per order item, so orders are always counted with `COUNTD(order_id)`, and review scores are counted once per order (first item row) so multi-item orders aren't over-weighted.
- **Seller flagging:** a seller is flagged when late rate is above 15% **and** they have at least 30 delivered orders. The minimum prevents tiny sellers (for example 1 late order out of 2) from dominating the list.
- **Scenario card:** the what-if figure is an illustration. It assumes revenue at risk shrinks in proportion to the late-order reduction. It is not a forecast.

## Data notes: missing values

About 2.2% of rows have no delivery date, and about 0.8% have no review score. These are expected, not errors:

- Orders that were shipped, canceled, invoiced or still processing have no delivery date, so delivery time and delay are blank.
- Some customers never left a review.
- 1,603 rows have the category `unknown` because the source data had no category for those products.

Blanks are left as they are rather than filled in, so no delivery times or review scores are invented. Late-delivery metrics only use delivered orders.

## How to reproduce

**Tableau**
1. Download `data/olist_tableau_flat.csv`.
2. Open Tableau Public (free, works on Mac) and connect to the file as a Text file.
3. Follow `docs/tableau_guide.md` to create the calculated fields, the 13 sheets and the 4 dashboards.

**Power BI (alternative)**
1. Import the star-schema CSVs from `data/`.
2. Follow `docs/data_model.md`, `docs/dax_measures.md` and `docs/build_guide.md`.

**Rebuild the data from raw files**
1. Download the raw Olist CSVs from Kaggle into a local `raw/` folder.
2. Edit the paths at the top of `etl/build_star_schema.py`.
3. Run `python3 build_star_schema.py`.

## Tools

Python (pandas) · Tableau Public · Power BI Desktop (alternative build) · Git and GitHub

## Author

**Shweta Rahate**, B.Tech CSE (Data Science and Analytics), Ramdeobaba University, Nagpur
GitHub: [shwetarahate13](https://github.com/shwetarahate13)
