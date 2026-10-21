# Japanese Automaker US Demand Analysis (2008–2025)

*(Repo name: `Volume_Discount_Analysis`. The project inside is a demand and price-sensitivity study of five Japanese automakers.)*

## The problem

How does price affect US demand for Toyota, Honda, Nissan, Subaru and Mazda, and does price sensitivity differ by brand? A pricing or incentive team would want that answer before deciding where discounts actually move volume.

## What the data can and can't answer

The dataset (`data/Japanese_Car_Sales_Elasticity.csv`) has 35 half-year periods (H1 2008 to H1 2025) of unit sales per brand, plus CPI, the weighted new-car finance rate, the average new-car loan amount and GDP growth. **It has no vehicle prices.** So it can show growth, share, and how sales moved with financing and the economy, but **it cannot measure price elasticity**. That conclusion is the main finding, and the robustness checks below are what support it.

## Findings

1. **Subaru is the growth story.** Sales rose 170.8% from H1 2008 to H1 2025, and its share of the five-brand group went from 4.8% to 11.8%. Mazda grew 37.3%, Toyota 2.3%; Nissan (−1.1%) and Honda (−6.2%) ended below where they started.
2. **2020 hit Nissan hardest.** H1 2020 vs H1 2019: Nissan −39.9%, Honda −23.8%, Subaru −21.2%, Toyota −16.8%, Mazda −7.0%. By H1 2025 Nissan was still about 30% below H1 2019, and its decline started after 2017. It's a brand problem, not just a macro one.
3. **Financing rates don't line up the way you'd expect.** Splitting periods at the median finance rate, four of five brands sold *more* in high-rate periods (Subaru +25.2%). Rates and sales both rose over time, so this comparison picks up the long-run trend, not a rate effect.
4. **No price-proxy coefficient is robust.** Using loan amount as the closest available price proxy:

   | Brand | Levels (original) | + trend, H2 dummy, real loan (HAC) | Half-year changes (HAC) |
   |---|---|---|---|
   | Toyota | +0.18 (p=0.61) | −0.90 (p=0.04) | −0.26 (p=0.73) |
   | Honda | −0.03 (p=0.94) | −1.18 (p=0.02) | −1.51 (p=0.11) |
   | Mazda | −0.23 (p=0.40) | −1.52 (p<0.001) | −0.18 (p=0.77) |
   | Nissan | −0.55 (p=0.35) | −2.81 (p=0.001) | −2.12 (p=0.015) |
   | Subaru | **+1.94 (p=0.01)** | −1.74 (p=0.04) | −0.42 (p=0.52) |

   The original spec's one "significant" result, Subaru +1.94, is an artifact. Its residuals are heavily autocorrelated (Durbin-Watson 0.16; 2 means none), so the p-value is invalid. The coefficient flips sign once a time trend is added and isn't significant in half-year changes. No brand's coefficient keeps the same sign and significance across all three specs. Loan amounts move almost in lockstep with time (r = 0.96 nominal, 0.88 after inflation), so this data can't separate price from long-run growth.

## Recommendations

- **Don't set discount policy from this data.** Nothing here supports a brand-level price elasticity.
- **To measure elasticity:** join an average transaction price series per brand and half-year, then fit `ln(sales) ~ ln(price) + finance rate + GDP + trend + H2` per brand with HAC errors. Split pre- and post-2020, because 2021–22 supply shortages capped sales regardless of demand.
- **Nissan's post-2017 slide** is worth a brand-level look (product cycle, fleet mix, incentives), since the macro variables don't explain it.

## Run it

```bash
pip install -r requirements.txt
python python/japanese_car_elasticity_analysis.py   # charts -> python/Python_Charts/, CSVs -> python/Tableau_Data/
python -m pytest tests/
```

Outputs: 4 charts and 10 Tableau-ready CSVs. `09_regression_elasticity.csv` is the original levels spec; `10_regression_robustness.csv` holds the three-spec comparison above.

## Tools

Python (pandas, NumPy, statsmodels, matplotlib), Tableau Public, pytest.

## Dashboard

Tableau workbook and PDFs are in `tableau/`. *(Public Tableau link still to be added. Before publishing, check the `.twbx` for any text that cites the old −0.76 Subaru figure.)*

## Correction notice

`docs/Japanese_Car_Demand_Elasticity_Report` (PDF/DOCX) claims a log-linear regression and a "Subaru −0.76 elasticity". No version of the code ever produced that number, and the data has no price column to produce it from. **Don't cite −0.76, and don't cite the +1.94 either** (see finding 4). The HTML page, `Volume_Discount_Analysis.html`, is the current write-up.

## Audit log

**2026-10-21 audit and rebuild**
- Added `regression_robustness()` (file 10): the loan model refit with a trend, a half-year dummy, CPI-deflated loans and Newey-West errors, and again in first differences, with Durbin-Watson reported for each fit. It showed the Subaru result was spurious; the README previously called it "a real, interesting, defensible finding".
- Console and chart labels no longer call the median-split comparison or the rate correlation an "elasticity" or "price sensitivity".
- Charts were written to `python/` while committed copies lived in `python/Python_Charts/`, leaving two diverging sets. Charts now go to `Python_Charts/` only, and the stale duplicates were removed.
- A failed run used to print `ERROR` and exit 0. It now exits non-zero.
- Removed the blanket `warnings.filterwarnings('ignore')`, which hid pandas/statsmodels warnings.
- Page fix: Toyota growth is +2.3%, not +2.4% (1,058,767 / 1,034,500). Added the robustness result to the page.
- Tests added (`tests/test_analysis.py`): recovery of a planted elasticity on synthetic data, the real-data result (nothing robust), parity with file 09, a zero-sales period, missing columns, and the median-split math.

**2026-09-16**
1. The script couldn't run from a fresh clone: it looked for the CSV in `python/` rather than `data/`, and exported to a lowercase `tableau_data` folder. Fixed.
2. No version of the code implemented the regression the written report claims. A real OLS was added (file 09).

Four script versions (base, `_Claude_Change`, `_V2`, `_V3`) were consolidated into one file.
