# Power BI Build Guide

Follow in order. Should take ~2–3 hours end to end.

## 1. Import data

Power BI Desktop → **Get Data → Text/CSV** → import all 9 files from `/data`. Use **Transform Data** to check each table's types (dates should auto-detect; if `order_purchase_timestamp` etc. import as text, set type to Date/Time in Power Query).

## 2. Build the model

Model view → create every relationship listed in `docs/data_model.md`. Mark `dim_date` as a Date Table (Modeling ribbon → Mark as Date Table → pick `date_key`).

## 3. Add measures

Create a blank `Measures` table (Enter Data → no columns, name it `Measures`), then paste in every DAX measure from `docs/dax_measures.md` (Modeling → New Measure, or paste directly in the formula bar).

## 4. Page 1 — Executive Overview

**Purpose:** the 10-second headline for a stakeholder walking by.

- 4 KPI cards across the top: `Total Revenue`, `Total Orders`, `Late Delivery Rate`, `Revenue at Risk %`
- Line chart: `Total Revenue` by month (`dim_date[year_month]` on axis)
- Line chart (secondary, same page): `Late Delivery Rate` by month — visually align the two to hint at the correlation
- Card: `Review Score Delta (Late vs On-Time)` — make this large and colored red/orange; it's your strongest single number
- Slicer: `dim_date[year]`

## 5. Page 2 — Delivery Risk Deep Dive

**Purpose:** where is the problem, geographically and by category.

- Map visual (filled/bubble map): `Late Delivery Rate` by `dim_customers[customer_state]`
- Bar chart: Top 10 product categories by `Late Delivery Rate`
- Clustered bar: `Avg Review Score - Late` vs `Avg Review Score - On Time`, broken down by top 5 states
- Table: state, late orders, late rate, revenue at risk — sorted descending by revenue at risk

## 6. Page 3 — Seller Performance

**Purpose:** who to flag, using `seller_performance_summary`.

- Table/matrix: seller_id, seller_city, total_orders, late_delivery_rate, avg_review_score, revenue_at_risk — sorted by revenue_at_risk descending, conditional formatting (red scale) on `late_delivery_rate`
- Card: `Sellers Flagged (Late Rate > 15%)`
- Scatter chart: X = `late_delivery_rate`, Y = `avg_review_score`, size = `total_revenue`, one dot per seller — this single chart tells the whole story visually (bottom-right cluster = high risk, high revenue)

## 7. Page 4 — What-If / Business Case

**Purpose:** the slide that gets you hired — turning analysis into a recommendation.

- Add the `Target Late Rate Reduction` parameter as a slider
- Big card: `Projected Recovered Revenue`
- Short static text box: 2–3 sentence recommendation (e.g., "Prioritize carrier renegotiation in AL, MA, SE — these 3 states account for X% of late deliveries but only Y% of revenue, making them high-leverage fixes.")

## 8. Polish before exporting

- Consistent color: use one accent color for "late/risk" (red/orange) and one neutral for "on-time/healthy" (blue/green) across every page
- Add a title text box per page
- File → Export → PDF (for the presentation) and export each page as PNG for `screenshots/` in the repo
- Save as `.pbix`, add it to the repo root (Git LFS recommended if it exceeds 25MB — GitHub blocks files over 100MB outright)

## 9. For your presentation

Use the exported PNGs / PDF pages in this order: Executive Overview → Delivery Risk Deep Dive → Seller Performance → What-If. See `docs/presentation_outline.md` for talking points per slide.
