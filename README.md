# Which Japanese automakers can raise prices without losing buyers?
### The data ranks them.

> **[Live Report](https://jbattohokson.github.io/Volume_Discount_Analysis/Volume_Discount_Analysis.html)** | [GitHub Repo](https://github.com/jbattohokson/Volume_Discount_Analysis)

---

## Executive Summary

Price elasticity tells a pricing team exactly what a brand can get away with. A brand with low elasticity can raise prices with minimal volume loss. A brand with high elasticity bleeds buyers the moment it does. This analysis measures that number for Toyota, Honda, Nissan, Subaru, and Mazda across 17 years of US sales data (2008–2025), using CPI, finance rates, and GDP growth as controls in a log-linear OLS model.

The results are not equal. Subaru's elasticity of −0.76 means a 3% price increase costs roughly 2.3% of volume — approximately 5,800 units on its current base. Nissan's elasticity of −1.45 means the same 3% increase costs 4.35% of volume — roughly 22,600 units. That difference is a strategic moat. GDP growth and financing rates are not background noise here; they are active demand drivers, and Nissan and Mazda face compounding exposure when both pressures rise simultaneously.

---

## Tools & Technologies

| Tool | Purpose |
|------|---------|
| Python (pandas, NumPy, Matplotlib, statsmodels) | Log-linear OLS regression, elasticity estimation, visualization |
| SQL | Data warehouse queries and aggregation |
| Tableau | Elasticity ranking visualization, brand volume trend charts |
| FRED (CPI, GDP, finance rates) | Macroeconomic control variables |

---

## Price Elasticity by Brand, Ranked Least to Most Sensitive

Elasticity measures percentage volume loss per 1% price increase. Closer to zero means stronger pricing power.

| Brand | Elasticity | 2008–2025 Growth | Strategic Position |
|-------|-----------|-----------------|-------------------|
| Subaru | −0.76 | +170.8% | Premium niche — pricing power |
| Honda | −0.98 | −6.2% | Mid-market — margin via brand loyalty |
| Toyota | −1.12 | +2.4% | Market leader — balanced pricing |
| Mazda | −1.23 | +37.3% | Specialty — growth despite sensitivity |
| Nissan | −1.45 | −1.1% | Value segment — volume trap |

A 3% price increase on Subaru's line loses approximately 5,800 units annually. The same increase on Nissan's line loses approximately 22,600 units. Whether the per-unit margin gain outweighs the volume loss is a breakeven calculation — but these elasticities define the range of acceptable price moves for each brand.

---

## Findings: What the data shows — and one interpretation by decision area

### Subaru's brand positioning is a quantifiable pricing moat
Subaru's −0.76 elasticity is the lowest in the analysis — buyers are the least responsive to price changes. Combined with +170.8% volume growth from 2008 to 2025, this is not a niche outcome: Subaru built genuine brand equity in specific segments that insulates it from competitive pricing pressure. A rough estimate puts the net revenue impact of a 3% price increase as positive — approximately $266M in additional revenue on the retained volume base versus ~$209M in lost volume revenue — before cost considerations. Volume discounting would erode exactly the brand equity creating that advantage.

### Nissan is in a high-sensitivity, low-growth position
Nissan's −1.45 elasticity is the highest in the analysis, and volume declined 1.1% from 2008 to 2025 while competitors grew. High price sensitivity combined with flat-to-declining volume is the signature of a brand competing primarily on price in a segment where that strategy has a ceiling. A 3% price increase on Nissan's line puts approximately $633M in revenue at risk (using an estimated $28K average transaction value) — a per-unit margin gain would need to be extraordinarily high to offset that loss. The path out is product differentiation toward a premium position, not a price cut that accelerates margin erosion.

### A rate-hiking cycle hits Nissan and Mazda hardest
Financing rates are a significant demand driver across all five brands — interest rate changes function as an effective price increase without any manufacturer action. The brands with the highest price sensitivity are also the most exposed when rates rise: their buyers are already price-conscious before financing costs are applied. A 100 basis point rate increase should trigger a Nissan and Mazda volume forecast revision before it triggers a price adjustment.

### GDP growth is a usable leading indicator for annual volume planning
Sales across all five manufacturers are pro-cyclical, growing during expansions and contracting during recessions. The 2008–2009 financial crisis, 2020 pandemic disruption, and 2022–2025 supply chain volatility are all visible in the trend data. A one-page sensitivity model mapping GDP scenarios to brand-level volume changes — using the elasticity coefficients from this analysis as inputs — gives planning teams a defensible range for inventory and production targets with no new data collection required.

---

## Recommendations: Recommended next steps by stakeholder

### Build a breakeven pricing table per brand
For each brand, what price increase is exactly offset by volume loss? The elasticity coefficients make this one calculation. Subaru's breakeven price increase is materially higher than Nissan's — the output is a max price increase before revenue turns negative, per brand.

### Target Honda's −0.98 as the repositioning benchmark for Nissan
Compressing Nissan's elasticity from −1.45 toward Honda's −0.98 requires product differentiation that reduces buyer price sensitivity — EV investment and technology-led models are the primary mechanism. The gap of 0.47 elasticity points translates to recovering ~13,000+ units of volume buffer on a 3% price move.

### Run rate-sensitivity scenarios quarterly
Map 50 bp and 100 bp rate increases to brand-level volume impact using the financing rate correlations in this analysis. Flag Nissan and Mazda for volume forecast revision in rising-rate environments. This is achievable as a one-page scenario table added to the quarterly demand forecast.

### Time Subaru price increases to new model launches
Subaru has pricing authority its competitors lack. Price increases tied to new launches reinforce the premium position rather than triggering price-comparison behavior. Avoid discount programs that pull Subaru into price competition with Nissan and Mazda.

---

## Model Specification and Data Scope

### Log-linear OLS price elasticity model

A log-linear specification allows direct coefficient interpretation as elasticities, controlling for GDP, financing rates, gas prices, disposable income, unemployment, and USD/JPY exchange rate simultaneously.

```
ln(Sales) = b0 + b1*ln(Price) + b2*ln(GasPrice) + b3*InterestRate 
          + b4*ln(Income) + b5*Unemployment + b6*ln(ExchangeRate) + e
```

Constant elasticity is assumed across the full 2008–2025 period. Elasticity likely shifted after 2020 due to supply chain constraints and inventory-driven pricing. A follow-on model splitting pre- and post-2020 would test whether elasticities are stable or regime-dependent.

| Dimension | Value |
|-----------|-------|
| Analysis period | 2008 to 2025 (17 years, semi-annual observations) |
| Manufacturers | Toyota, Honda, Nissan, Subaru, Mazda |
| Sales data | GoodCarBadCar.net — annual US sales by manufacturer |
| Economic controls | CPI, finance rates, GDP growth, loan availability, disposable income, USD/JPY (FRED) |
| Modeling | Python — Statsmodels OLS |
| Visualization | Matplotlib, Seaborn, Tableau Public |
