# Tableau Build Guide: Olist Delivery Risk & Revenue Impact

Same business question as the Power BI version: **how much is late delivery costing Olist in revenue and customer satisfaction, and which states and sellers drive it?**

Use **Tableau Public** (free, works on Mac): https://public.tableau.com/app/discover. Publishing there also gives you a live link for your portfolio and resume. The Olist data is public, so nothing sensitive is exposed.

## 1. Connect the data

Use the single flat file `data/olist_tableau_flat.csv` (112,650 rows, one row per item in an order).

1. Open Tableau Public → **Connect → Text file** → pick `olist_tableau_flat.csv`.
2. In the Data Source tab, check types: `order_purchase_date` should be **Date**; `is_delivered` and `is_late` should be **Boolean**; `customer_state` should be a **dimension** (string). Fix any that are wrong by clicking the small icon above the column name.
3. Right-click `customer_state` → **Geographic Role → State/Province**. If the map later shows "unknown" marks, click the "unknown" badge → Edit Locations → set country to Brazil. If it still fails, use a ranked bar chart instead of a map (it is just as readable).

**Important grain rule:** each order can have several rows (one per item). Never use plain `COUNT` for orders; always use `COUNTD([order_id])`. The formulas below already handle this.

## 2. Calculated fields

Create each via Analysis → Create Calculated Field.

```
Orders
COUNTD([order_id])

Delivered Orders
COUNTD(IF [is_delivered] THEN [order_id] END)

Late Orders
COUNTD(IF [is_delivered] AND [is_late] THEN [order_id] END)

Late Delivery Rate
[Late Orders] / [Delivered Orders]

Total Revenue
SUM([item_revenue])

Revenue - Late Orders
SUM(IF [is_late] THEN [item_revenue] END)

Revenue at Risk %
[Revenue - Late Orders] / [Total Revenue]

Avg Delay Days (Late)
AVG(IF [is_late] THEN [delay_vs_estimate_days] END)

Avg Review Score
AVG(IF [order_item_id] = 1 THEN [review_score] END)

Avg Review - Late
AVG(IF [order_item_id] = 1 AND [is_late] THEN [review_score] END)

Avg Review - On Time
AVG(IF [order_item_id] = 1 AND [is_delivered] AND NOT [is_late] THEN [review_score] END)

Review Score Delta
[Avg Review - Late] - [Avg Review - On Time]
```

Why `order_item_id = 1`: a review belongs to the order, not the item. Counting only the first item row of each order stops multi-item orders from being weighted more heavily.

### Seller flagging (level-of-detail fields)

```
Seller Delivered Orders
{ FIXED [seller_id] : COUNTD(IF [is_delivered] THEN [order_id] END) }

Seller Late Orders
{ FIXED [seller_id] : COUNTD(IF [is_delivered] AND [is_late] THEN [order_id] END) }

Seller Late Rate
[Seller Late Orders] / [Seller Delivered Orders]

Seller Flag
IF [Seller Delivered Orders] >= 30 AND [Seller Late Rate] > 0.15
THEN "Flagged" ELSE "OK" END
```

The `>= 30` minimum matters. Without it, a seller with 1 late order out of 2 shows a 50% late rate and floods your flagged list with tiny sellers. Say this in your presentation; it shows analytical judgment.

### What-if parameter

1. Create Parameter → name `Target Late Rate Reduction`, type Float, range 0 to 1, step 0.05, display as percentage. Right-click it → **Show Parameter**.
2. Calculated field:

```
Projected Recovered Revenue
[Revenue - Late Orders] * [Target Late Rate Reduction]
```

Be honest about what this is: a simple scenario multiplier that assumes revenue exposure shrinks in proportion to the late-order reduction. Label the card "Illustrative scenario" so nobody mistakes it for a forecast.

## 3. Sheets to build

| Sheet | Build |
|---|---|
| KPI Revenue | `Total Revenue` as text |
| KPI Orders | `Orders` as text |
| KPI Late Rate | `Late Delivery Rate` as text, format as % |
| KPI Rev at Risk | `Revenue at Risk %` as text |
| KPI Review Gap | `Avg Review - On Time` and `Avg Review - Late` side by side as text (shows ~4.2 vs ~2.3) |
| Monthly Trend | Columns: `order_purchase_date` (MONTH, continuous). Rows: `Total Revenue`; add `Late Delivery Rate` as a dual axis line |
| State Map | `customer_state` on Detail, `Late Delivery Rate` on Color (red scale), `Late Orders` on Size |
| State Ranking | Rows: `customer_state`. Columns: `Late Delivery Rate`. Sort descending. Add `Revenue - Late Orders` as a label |
| Category Risk | Rows: `product_category`. Columns: `Late Delivery Rate`. Filter to Top 10 by `Late Delivery Rate` (and exclude "unknown") |
| Review Compare | Bars of `Avg Review - Late` vs `Avg Review - On Time` for the top 5 states |
| Seller Scatter | Columns: `Seller Late Rate`. Rows: `Avg Review Score`. Detail: `seller_id`. Size: `Total Revenue`. Color: `Seller Flag`. Filter `Seller Delivered Orders >= 30` |
| Seller Table | Rows: `seller_id`, `seller_city`. Columns: Measure Names (Seller Delivered Orders, Seller Late Rate, Avg Review Score, Revenue - Late Orders). Filter to `Seller Flag = Flagged`, sort by `Revenue - Late Orders` |
| Scenario Card | `Projected Recovered Revenue` as large text |

## 4. Dashboards

Dashboard → New Dashboard → set size **Automatic** or Fixed 1400 x 900. Drag sheets in, use horizontal and vertical containers to align.

1. **Executive Overview:** five KPI sheets across the top, Monthly Trend below, Review Gap highlighted. Add a Year filter (`order_purchase_date`) applied to all sheets.
2. **Delivery Risk Deep Dive:** State Map + State Ranking + Category Risk + Review Compare. Turn on "Use as Filter" on the map so clicking a state filters the rest.
3. **Seller Performance:** Seller Scatter + Seller Table + a count of flagged sellers.
4. **What-If / Recommendation:** Scenario Card + the parameter control + a text box with your 2 to 3 sentence recommendation (for example: prioritize carrier renegotiation in AL, MA and SE, where late rates run about 13 to 21%).

Use one color for risk (red or orange) and one for healthy (blue or teal) on every sheet.

## 5. Publish and add to GitHub

- File → **Save to Tableau Public** → sign in → name it. Copy the public link.
- Export PNGs: Dashboard → Export Image, save into `screenshots/`.
- Put the Tableau Public link at the top of your README.
- Save the `.twbx` file (File → Save As) into the repo as well.

## 6. Validate your numbers

These should match (small differences in the review average, around 4.2 vs 4.21, come from averaging per order vs per review):

- Late delivery rate about **6.8%**
- Revenue on late orders about **7.3%** of total (about R$1.15M)
- Avg review: about **4.2 on time** vs about **2.3 late**
- Worst states by late rate: AL, MA, SE, PI, CE

If your numbers differ, the usual cause is using `COUNT` instead of `COUNTD` on `order_id`.
