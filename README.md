# Volume Discount Analysis: Japanese Auto Sales vs. Financing Conditions (2008-2025)

**Business question:** how did US sales volume change for five Japanese automakers (Toyota, Honda, Mazda, Nissan, Subaru) from 2008 to 2025, and does any brand's volume move with financing conditions?

## Key findings

- **Subaru nearly tripled its US sales:** +170.8% from H1 2008 to H1 2025, the fastest growth of the five. Mazda grew 37.3% and Toyota 2.4%, while Nissan (-1.1%) and Honda (-6.2%) shrank.
- **Toyota is the volume leader** with 37.3% of the five brands' combined sales.
- **Only Subaru's sales track financing conditions.** A log-linear regression of sales on average new-car loan amount is statistically significant for Subaru alone (coefficient +1.94, p = 0.01). Subaru's volume rises with loan size, which fits a buyer base that finances higher-trim cars. None of the other four brands reach significance at p < 0.05.

## Data honesty

The dataset has no per-vehicle price column, so this project does **not** measure price elasticity of demand. Loan amount is used as the closest available stand-in for what buyers spend, and the regression above is reported as a financing relationship, not a price elasticity. An earlier written report in this repo presented median-split percent differences as "elasticities" (for example -0.76 for Subaru). No version of the code produces those figures, so that report has been removed. The project page (`Volume_Discount_Analysis.html`) lays out what extra data would be needed to measure true price elasticity.

## Pipeline

**`japanese_car_elasticity_analysis.py`**: loads 17 years of semi-annual sales, price-proxy, CPI, financing-rate, and GDP-growth data for Toyota, Honda, Mazda, Nissan, and Subaru; computes descriptive statistics, correlations, sensitivity buckets, growth rates, and the loan-amount regression above; produces 4 charts and 9 Tableau-ready CSVs (was 8 — added `09_regression_elasticity.csv`).

```bash
pip install -r requirements.txt
python "python/japanese_car_elasticity_analysis.py"
```

## Tools

Python (pandas, NumPy, statsmodels, matplotlib, seaborn), Tableau Public.

## Dashboard

Tableau workbook: `tableau/Japanese_Car_Demand_Elasticity_Analysis.twbx`, with PDF exports in `tableau/`. Note: one chart in `JPCE_Tableau_Dashboard_2.pdf` labels the median-split finance-rate comparison "Avg. Elasticity Percent". It is a percent difference in average sales between high- and low-rate periods, not an elasticity.

## Bugs found and fixed while testing this pipeline (2026-09-16)

1. **The script could not run from a fresh clone.** It looked for the CSV in its own folder (`python/`) instead of `data/`, and used a lowercase `tableau_data` export path that would have created a duplicate folder next to the existing `Tableau_Data/`. Fixed with a multi-candidate path search.
2. **No version of the code ever implemented the regression methodology the old written report claimed.** A real log-linear regression was added (`09_regression_elasticity.csv`), and the old report was removed. See Data honesty above.

## Repo hygiene note

Four script versions (base, `_Claude_Change`, `_V2`, `_V3`) were consolidated into one file, `japanese_car_elasticity_analysis.py`, based on `_V3` plus the regression fix above.
