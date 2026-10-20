# Japanese Car Sales Price Elasticity Analysis (2008-2025)

**Business question:** how does vehicle price affect US demand for five major Japanese automakers, and does price sensitivity differ by brand?

## Important correction — read this before using this project's numbers anywhere

`docs/Japanese_Car_Demand_Elasticity_Report` claims a log-linear regression methodology and a specific figure ("Subaru: lowest price sensitivity, -0.76 elasticity"). **Testing this project on 2026-09-16 found that number is not reproducible.** None of the four Python script versions in this project's history (including the one previously shipped as final) ever actually ran a regression — all four compute the same median-split percent difference in average sales between high- and low-finance-rate periods, and call that "elasticity." That is a real, honest descriptive statistic, but it is not price elasticity of demand, and it does not produce -0.76 for Subaru or anything close to it.

I added a real log-linear OLS regression (`export_regression_elasticity()`, file `09_regression_elasticity.csv`) using new car loan amount as the price proxy — there is no actual per-vehicle price column in this dataset, so loan amount is the closest available stand-in. Verified 3 times (OLS is deterministic, so this is really a code-correctness check, not a randomness check): **only Subaru's coefficient is statistically significant (p=0.0104), and it's +1.94 — the opposite sign of the report's claim, not -0.76.** None of the other four manufacturers reach significance at p<0.05.

**Do not use the "-0.76 Subaru elasticity" figure on a resume, in a cover letter, or in an interview** — it fails the zero-fabrication standard this portfolio should be held to, since it isn't produced by any version of the actual code. The honest headline from what the code actually shows: of the five brands, only Subaru's sales show a statistically significant relationship with financing conditions in this dataset, and demand rises (not falls) with loan amount — plausibly because Subaru's buyer base skews toward financed, feature-loaded trims rather than because higher prices increase demand. That's a real, interesting, defensible finding. The old -0.76 claim is not.

## Pipeline

**`japanese_car_elasticity_analysis.py`** — loads 17 years of semi-annual sales, price-proxy, CPI, financing-rate, and GDP-growth data for Toyota, Honda, Mazda, Nissan, and Subaru; computes descriptive statistics, correlations, sensitivity buckets, and the real regression-based elasticity above; produces 4 charts and 9 Tableau-ready CSVs (was 8 — added `09_regression_elasticity.csv`).

```bash
pip install -r requirements.txt
python "python/japanese_car_elasticity_analysis.py"
```

## Tools

Python (pandas, NumPy, statsmodels, matplotlib, seaborn), Tableau Public.

## Dashboard

*(Add the public.tableau.com link for `Japanese_Car_Demand_Elasticity_Analysis`. Before publishing, update any dashboard text/tooltips that cite the old -0.76 figure — check `tableau/Japanese_Car_Demand_Elasticity_Analysis.twbx` for a calculated field or text box referencing it.)*

## Bugs found and fixed while testing this pipeline (2026-09-16)

1. **The script could not run from a fresh clone.** It looked for the CSV in its own folder (`python/`) instead of `data/`, and used a lowercase `tableau_data` export path that would have created a duplicate folder next to the existing `Tableau_Data/`. Fixed with a multi-candidate path search.
2. **No version of the code ever implemented the regression methodology the written report claims.** See the correction above — this is the most consequential fix in this project.

## Repo hygiene note

Four script versions (base, `_Claude_Change`, `_V2`, `_V3`) were consolidated into one file, `japanese_car_elasticity_analysis.py`, based on `_V3` plus the regression fix above.
