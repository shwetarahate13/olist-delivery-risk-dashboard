# DAX Measures

Create a dedicated measure table first (Model view → New Table → paste `Measures = { }`), then add every measure below to it so they're not scattered inside physical tables.

## Core volume & revenue

```dax
Total Orders = DISTINCTCOUNT(dim_orders[order_id])

Total Revenue = SUM(fact_order_items[order_item_revenue])

Total Freight = SUM(fact_order_items[freight_value])

Avg Order Value =
DIVIDE([Total Revenue], [Total Orders])
```

## Delivery performance (the core story)

```dax
Delivered Orders =
CALCULATE(
    DISTINCTCOUNT(dim_orders[order_id]),
    dim_orders[is_delivered] = TRUE
)

Late Orders =
CALCULATE(
    DISTINCTCOUNT(dim_orders[order_id]),
    dim_orders[is_delivered] = TRUE,
    dim_orders[is_late] = TRUE
)

Late Delivery Rate =
DIVIDE([Late Orders], [Delivered Orders])

Avg Delay Days (Late Orders) =
CALCULATE(
    AVERAGE(dim_orders[delay_vs_estimate_days]),
    dim_orders[is_late] = TRUE
)
```

## Revenue at risk

```dax
Revenue - Late Orders =
CALCULATE(
    [Total Revenue],
    dim_orders[is_late] = TRUE
)

Revenue at Risk % =
DIVIDE([Revenue - Late Orders], [Total Revenue])
```

## Customer satisfaction impact

```dax
Avg Review Score = AVERAGE(fact_reviews[review_score])

Avg Review Score - Late =
CALCULATE(
    [Avg Review Score],
    dim_orders[is_late] = TRUE
)

Avg Review Score - On Time =
CALCULATE(
    [Avg Review Score],
    dim_orders[is_late] = FALSE
)

Review Score Delta (Late vs On-Time) =
[Avg Review Score - Late] - [Avg Review Score - On Time]
```

## Time intelligence (requires `dim_date` marked as Date Table)

```dax
Revenue MoM % =
VAR CurrentRev = [Total Revenue]
VAR PriorRev =
    CALCULATE([Total Revenue], DATEADD(dim_date[date_key], -1, MONTH))
RETURN
    DIVIDE(CurrentRev - PriorRev, PriorRev)

Late Rate Trailing 3M =
CALCULATE(
    [Late Delivery Rate],
    DATESINPERIOD(dim_date[date_key], MAX(dim_date[date_key]), -3, MONTH)
)
```

## Seller ranking (used with `seller_performance_summary`)

```dax
Seller Revenue at Risk = SUM(seller_performance_summary[revenue_at_risk])

Seller Late Rate = AVERAGE(seller_performance_summary[late_delivery_rate])

Sellers Flagged (Late Rate > 15%) =
CALCULATE(
    DISTINCTCOUNT(seller_performance_summary[seller_id]),
    seller_performance_summary[late_delivery_rate] > 0.15
)
```

## What-if parameter (for the "what would we save" slide)

Add via **Modeling → New Parameter → Numeric range**, name it `Target Late Rate Reduction`, range 0–100%, increment 5.

```dax
Projected Recovered Revenue =
VAR CurrentAtRisk = [Revenue - Late Orders]
VAR ReductionPct = SELECTEDVALUE('Target Late Rate Reduction'[Target Late Rate Reduction Value], 0)
RETURN
    CurrentAtRisk * ReductionPct
```

Use this on a card with a slicer for the parameter — it's the single best "so what" visual for a BA interview: *"if we cut the late rate by X%, we recover this much revenue exposure."*
