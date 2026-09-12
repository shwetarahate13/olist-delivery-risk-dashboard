# Presentation Outline & Talking Points

~6–8 minutes. One slide per dashboard page, plus a title and closing slide.

## Slide 1 — Title
"Olist Delivery Risk & Revenue Impact" — your name, "Power BI + Python (pandas) ETL", dataset source and size (114K+ orders, 2016–2018).

## Slide 2 — The Business Question
"Olist's logistics team wants to know: is late delivery actually hurting the business, or is it just an operational metric we track for its own sake? I set out to quantify it in revenue and satisfaction terms."

## Slide 3 — Executive Overview (screenshot)
Talking points:
- "6.8% of delivered orders arrive late — sounds small, but it's tied to R$1.15M, or 7.3% of total revenue."
- "The bigger hit is satisfaction: review scores fall from 4.21 to 2.27 — nearly half — when an order is late."
- Point at the revenue/late-rate line chart if they move together over time.

## Slide 4 — Delivery Risk Deep Dive (screenshot)
Talking points:
- "The problem isn't evenly spread — states like Alagoas and Maranhão see late rates 2–3x the national average."
- "That's a logistics-partner problem in specific regions, not a company-wide one — which changes the fix from 'improve everything' to 'renegotiate these 3 carrier contracts.'"

## Slide 5 — Seller Performance (screenshot)
Talking points:
- "This scatter plot is the core diagnostic: sellers in the bottom-right — high late rate, high revenue — are the ones costing the most in risk."
- "I flagged sellers above 15% late rate for review; that's a short, actionable list, not "all 3,000 sellers.""

## Slide 6 — What-If / Recommendation (screenshot)
Talking points:
- "If Olist cut the late-delivery rate by even 30% in the flagged states, that recovers roughly [read the card value at 30%] in at-risk revenue."
- "My recommendation: prioritize the 3 worst states and the sellers flagged above, rather than a blanket logistics overhaul."

## Slide 7 — How It Was Built
- Briefly mention: Python/pandas for ETL and feature engineering (delay calculation, seller aggregation), Power BI star schema, DAX for the what-if parameter.
- This is the moment to mention you designed the data model yourself, not just dragged in one flat CSV — that's what separates this from a tutorial project.

## Slide 8 — Closing
- One line on what you'd do with more time/data (e.g., "add carrier-level data to isolate whether delay is a seller-fulfillment issue or a shipping-partner issue").
- Link to the GitHub repo.

## Anticipate these interview questions
- **"Why star schema instead of one flat table?"** → performance at scale, avoids repeating dimension attributes millions of times, standard BI modeling practice.
- **"Why pandas for ETL instead of Power Query?"** → needed row-level date-delta calculations and a seller-level aggregation before modeling; Power Query can do it too, but pandas was faster to iterate and testable.
- **"How would you validate the revenue-at-risk number?"** → cross-check against a simpler manual SUMIFS in Excel on a data sample; sanity-check it's not double-counting order items.
