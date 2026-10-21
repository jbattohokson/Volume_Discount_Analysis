"""
Japanese Car Sales Elasticity Analysis
Complete analysis without BigQuery or API costs
Run directly in VSCode terminal
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # headless: charts are only written to disk
import matplotlib.pyplot as plt

# TESTED 2026-09-16: running this script as-is failed immediately with
# "CSV not found" on every run. SCRIPT_DIR assumed the CSV lived next to the
# script in python/, but it actually lives one level up in data/
# (the project's established convention, same as every other project in this
# portfolio). Also, EXPORT_DIR was "tableau_data" (lowercase), which would
# have silently created a brand-new duplicate folder next to the existing
# "Tableau_Data/" this script's own outputs already live in, rather than
# writing into it. Both fixed below with a multi-candidate search so the
# script keeps working regardless of which folder it's run from.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

_csv_candidates = [
    os.path.join(SCRIPT_DIR, "Japanese_Car_Sales_Elasticity.csv"),
    os.path.join(PROJECT_DIR, "data", "Japanese_Car_Sales_Elasticity.csv"),
]
CSV_FILE = next((p for p in _csv_candidates if os.path.exists(p)), _csv_candidates[0])
EXPORT_DIR = os.path.join(SCRIPT_DIR, "Tableau_Data")
# Charts used to be written next to the script, leaving a second, stale copy of
# every PNG beside the committed python/Python_Charts/ set.
CHART_DIR = os.path.join(SCRIPT_DIR, "Python_Charts")

MANUFACTURERS = ['Toyota', 'Honda', 'Mazda', 'Nissan', 'Subaru']


# =============================================================================
# CarSalesAnalysis
# =============================================================================

class CarSalesAnalysis:
    """Descriptive statistics, correlations, elasticity metrics, and plots."""

    def __init__(self, csv_path):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV not found: {csv_path}")

        print(f"Loading data from: {csv_path}")
        self.df = pd.read_csv(csv_path)

        # Strip all column names once on load — eliminates the trailing-space bug
        self.df.columns = self.df.columns.str.strip()

        self._prepare_data()

    def _prepare_data(self):
        """Store column references and derive Total_Sales."""
        self.df['Total_Sales'] = self.df[MANUFACTURERS].sum(axis=1)

        # Resolve column names once so every method uses the same references
        self.finance_col = 'Finance Rate of New Car (Weighted)' if 'Finance Rate of New Car (Weighted)' in self.df.columns else None
        self.gdp_col     = 'GDP Growth'    if 'GDP Growth'    in self.df.columns else None
        self.cpi_col     = 'CPI'           if 'CPI'           in self.df.columns else None
        self.loan_col    = 'New Car Loan Amt.' if 'New Car Loan Amt.' in self.df.columns else None
        self.period_col  = 'Semi-Annual Year'  if 'Semi-Annual Year'  in self.df.columns else None

        print(f"\n Data loaded: {len(self.df)} rows, {len(self.df.columns)} columns")
        print(f"  Columns: {list(self.df.columns)}")

    # -------------------------------------------------------------------------
    def descriptive_stats(self):
        print("\n" + "="*80)
        print("DESCRIPTIVE STATISTICS")
        print("="*80)

        print("\nSales by Manufacturer (units):")
        print("-"*80)
        for col in MANUFACTURERS:
            s = self.df[col]
            print(f"  {col:10} | Mean: {s.mean():>10,.0f} | Std: {s.std():>10,.0f} | "
                  f"Min: {s.min():>10,.0f} | Max: {s.max():>10,.0f}")

        print("\nEconomic Indicators:")
        print("-"*80)
        econ_cols = [c for c in [self.cpi_col, self.finance_col, self.loan_col, self.gdp_col] if c]
        for col in econ_cols:
            s = self.df[col]
            print(f"  {col:40} | Mean: {s.mean():>8.2f} | Std: {s.std():>8.2f} | "
                  f"Min: {s.min():>8.2f} | Max: {s.max():>8.2f}")

    # -------------------------------------------------------------------------
    def correlation_analysis(self):
        print("\n" + "="*80)
        print("CORRELATION ANALYSIS")
        print("="*80)

        econ_cols = [c for c in [self.cpi_col, self.loan_col, self.gdp_col] if c]
        print("\nCorrelation with Total Sales:")
        print("-"*80)
        for col in econ_cols:
            corr = self.df[[col, 'Total_Sales']].corr().iloc[0, 1]
            print(f"  {col:40} : {corr:>7.3f}")

        if self.finance_col:
            print("\nManufacturer Sensitivity to Finance Rate:")
            print("-"*80)
            for mfg in MANUFACTURERS:
                corr = self.df[[self.finance_col, mfg]].corr().iloc[0, 1]
                level = "High" if abs(corr) > 0.3 else "Moderate" if abs(corr) > 0.15 else "Low"
                print(f"  {mfg:10} : {corr:>7.3f}  ({level})")

        if self.gdp_col:
            print("\nManufacturer Sensitivity to GDP Growth:")
            print("-"*80)
            for mfg in MANUFACTURERS:
                corr = self.df[[self.gdp_col, mfg]].corr().iloc[0, 1]
                level = "High" if abs(corr) > 0.3 else "Moderate" if abs(corr) > 0.15 else "Low"
                print(f"  {mfg:10} : {corr:>7.3f}  ({level})")

    # -------------------------------------------------------------------------
    def elasticity_analysis(self):
        print("\n" + "="*80)
        print("ELASTICITY ANALYSIS")
        print("="*80)

        if self.finance_col:
            print("\nFinance-Rate Sensitivity (median split of periods; NOT a price elasticity):")
            print("-"*80)
            median_rate = self.df[self.finance_col].median()
            high_mask = self.df[self.finance_col] > median_rate
            for mfg in MANUFACTURERS:
                high = self.df.loc[high_mask, mfg].mean()
                low  = self.df.loc[~high_mask, mfg].mean()
                pct  = ((high - low) / low * 100) if low > 0 else float('nan')
                print(f"  {mfg:10} | High Rate Avg: {high:>10,.0f} | Low Rate Avg: {low:>10,.0f} | "
                      f"Difference: {pct:>+7.1f}%")

        if self.gdp_col:
            print("\nGDP-Growth Sensitivity (positive vs negative growth periods):")
            print("-"*80)
            pos_mask = self.df[self.gdp_col] > 0
            for mfg in MANUFACTURERS:
                pos = self.df.loc[pos_mask, mfg].mean()
                neg = self.df.loc[~pos_mask, mfg].mean()
                pct = ((pos - neg) / neg * 100) if neg > 0 else float('nan')
                print(f"  {mfg:10} | Positive GDP Avg: {pos:>10,.0f} | Negative GDP Avg: {neg:>10,.0f} | "
                      f"Difference: {pct:>+7.1f}%")

    # -------------------------------------------------------------------------
    def market_analysis(self):
        print("\n" + "="*80)
        print("MARKET ANALYSIS")
        print("="*80)

        totals      = self.df[MANUFACTURERS].sum()
        grand_total = totals.sum()

        print("\nMarket Share (by total sales):")
        print("-"*80)
        for mfg in MANUFACTURERS:
            print(f"  {mfg:10} : {totals[mfg] / grand_total * 100:>6.1f}%")

        if self.period_col:
            print("\nAverage Sales by Period:")
            print("-"*80)
            print(self.df[[self.period_col] + MANUFACTURERS].to_string(index=False))

        print("\nGrowth Rates (first → last period):")
        print("-"*80)
        for mfg in MANUFACTURERS:
            first  = self.df[mfg].iloc[0]
            last   = self.df[mfg].iloc[-1]
            growth = (last - first) / first * 100
            arrow  = "↑" if growth > 0 else "↓"
            print(f"  {mfg:10} : {arrow} {growth:>+7.1f}%")

    # -------------------------------------------------------------------------
    def plot_sales_trends(self):
        print("\n Creating sales trend visualization...")
        plt.figure(figsize=(14, 7))
        for col in MANUFACTURERS:
            plt.plot(range(len(self.df)), self.df[col], marker='o', label=col, linewidth=2)
        plt.xlabel('Period')
        plt.ylabel('Sales (units)')
        plt.title('Japanese Car Sales Trends (2008-2025)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        path = os.path.join(CHART_DIR, 'sales_trend.png')
        plt.savefig(path, dpi=150)
        print(f"  Saved: sales_trend.png")
        plt.close()

    def plot_market_share(self):
        """Horizontal bar chart — easier to compare than a pie chart."""
        print("\n Creating market share visualization...")
        totals = self.df[MANUFACTURERS].sum().sort_values()
        grand  = totals.sum()
        shares = totals / grand * 100

        plt.figure(figsize=(9, 5))
        bars = plt.barh(shares.index, shares.values, color='steelblue')
        plt.bar_label(bars, fmt='%.1f%%', padding=4)
        plt.xlabel('Market Share (%)')
        plt.title('Market Share by Manufacturer (2008-2025)')
        plt.xlim(0, shares.max() * 1.15)
        plt.tight_layout()
        path = os.path.join(CHART_DIR, 'market_share.png')
        plt.savefig(path, dpi=150)
        print(f"  Saved: market_share.png")
        plt.close()

    def plot_elasticity_comparison(self):
        print("\n Creating elasticity comparison visualization...")
        if not self.finance_col:
            print("  Finance rate column not found — skipping")
            return

        corrs  = [self.df[[self.finance_col, mfg]].corr().iloc[0, 1] for mfg in MANUFACTURERS]
        colors = ['#d73027' if x < 0 else '#1a9850' for x in corrs]

        plt.figure(figsize=(10, 6))
        plt.barh(MANUFACTURERS, corrs, color=colors)
        plt.axvline(0, color='black', linewidth=1)
        plt.xlabel('Correlation with Finance Rate')
        plt.title('Correlation of Sales with Finance Rate (not a price elasticity)')
        plt.tight_layout()
        path = os.path.join(CHART_DIR, 'elasticity_comparison.png')
        plt.savefig(path, dpi=150)
        print(f"  Saved: elasticity_comparison.png")
        plt.close()

    def plot_economic_impact(self):
        print("\n Creating economic impact visualization...")
        total_sales = self.df[MANUFACTURERS].sum(axis=1)
        scatter_specs = [
            (self.cpi_col,     'CPI',              'Total Sales', 'Sales vs CPI',            'steelblue'),
            (self.finance_col, 'Finance Rate (%)',  'Total Sales', 'Sales vs Finance Rate',   'orange'),
            (self.gdp_col,     'GDP Growth (%)',    'Total Sales', 'Sales vs GDP Growth',     'green'),
            (self.loan_col,    'Loan Amount',       'Total Sales', 'Sales vs Loan Amount',    'red'),
        ]

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        for ax, (col, xlabel, ylabel, title, color) in zip(axes.flat, scatter_specs):
            if col:
                ax.scatter(self.df[col], total_sales, s=100, alpha=0.6, color=color)
                ax.set_xlabel(xlabel)
                ax.set_ylabel(ylabel)
                ax.set_title(title)
                ax.grid(True, alpha=0.3)
            else:
                ax.set_visible(False)

        plt.tight_layout()
        path = os.path.join(CHART_DIR, 'economic_impact.png')
        plt.savefig(path, dpi=150)
        print(f"  Saved: economic_impact.png")
        plt.close()

    # -------------------------------------------------------------------------
    def generate_full_report(self):
        print("\n" + "="*80)
        print("JAPANESE CAR SALES ELASTICITY ANALYSIS — Full Report")
        print("="*80)

        os.makedirs(CHART_DIR, exist_ok=True)
        self.descriptive_stats()
        self.correlation_analysis()
        self.elasticity_analysis()
        self.market_analysis()

        print("\n" + "="*80)
        print("GENERATING VISUALIZATIONS")
        print("="*80)
        self.plot_sales_trends()
        self.plot_market_share()
        self.plot_elasticity_comparison()
        self.plot_economic_impact()

        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print("\nGenerated files:")
        for name in ['sales_trend.png', 'market_share.png',
                     'elasticity_comparison.png', 'economic_impact.png']:
            print(f"  - {name}")


# =============================================================================
# TableauExporter
# =============================================================================

class TableauExporter:
    """Export car sales data in multiple formats for Tableau."""

    def __init__(self, df, export_dir):
        """
        Parameters
        ----------
        df         : pd.DataFrame already loaded and column-stripped by CarSalesAnalysis
        export_dir : directory where CSV exports are written
        """
        self.df         = df
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
        print(f"Export directory: {export_dir}")

        # Resolve column references once
        self.finance_col = 'Finance Rate of New Car (Weighted)' if 'Finance Rate of New Car (Weighted)' in df.columns else None
        self.gdp_col     = 'GDP Growth'         if 'GDP Growth'         in df.columns else None
        self.cpi_col     = 'CPI'                if 'CPI'                in df.columns else None
        self.loan_col    = 'New Car Loan Amt.'   if 'New Car Loan Amt.'   in df.columns else None
        self.period_col  = 'Semi-Annual Year'    if 'Semi-Annual Year'    in df.columns else None

    def _save(self, df_out, filename):
        path = os.path.join(self.export_dir, filename)
        df_out.to_csv(path, index=False)
        print(f"  Saved: {filename} ({len(df_out)} rows)")
        return path

    # -------------------------------------------------------------------------
    def export_raw_data(self):
        """01 — Original data with cleaned column names."""
        print("\n Exporting Raw Data...")
        df_clean = self.df.copy()
        df_clean.columns = [c.replace('(', '').replace(')', '').replace('.', '').strip()
                            for c in df_clean.columns]
        return self._save(df_clean, "01_raw_data.csv")

    def export_long_format(self):
        """02 — Long format (one row per manufacturer per period)."""
        print("\n Exporting Long Format...")
        id_vars  = [c for c in self.df.columns if c not in MANUFACTURERS]
        df_long  = self.df.melt(id_vars=id_vars, var_name='Manufacturer', value_name='Sales_Units')
        df_long.columns = [c.replace('(', '').replace(')', '').replace('.', '').strip()
                           for c in df_long.columns]
        return self._save(df_long, "02_sales_long_format.csv")

    def export_market_share(self):
        """03 — Aggregate market share per manufacturer."""
        print("\n Exporting Market Share...")
        totals      = self.df[MANUFACTURERS].sum()
        grand_total = totals.sum()
        rows = [
            {
                'Manufacturer':           mfg,
                'Total_Sales':            int(totals[mfg]),
                'Market_Share_Percent':   round(totals[mfg] / grand_total * 100, 2),
                'Market_Share_Decimal':   round(totals[mfg] / grand_total, 4),
            }
            for mfg in MANUFACTURERS
        ]
        return self._save(pd.DataFrame(rows), "03_market_share.csv")

    def export_elasticity_metrics(self):
        """
        04 — Rate/GDP sensitivity buckets per manufacturer (median-split, NOT
        a regression coefficient).

        TESTED 2026-09-16: this method's original name and output column
        ("Elasticity_Percent") implied a real price elasticity of demand
        coefficient, matching language in Japanese_Car_Demand_Elasticity_Report
        ("log-linear regression", "-0.76 elasticity" for Subaru). Neither this
        method nor any of the other three script versions in this project's
        history (base, _Claude_Change, _V2) actually run a regression anywhere
        -- all four compute this same median-split percent difference in mean
        sales between high- and low-finance-rate periods, which is a real,
        useful descriptive statistic but is NOT price elasticity of demand.
        It also can't be, strictly: this dataset has no observed vehicle price
        column at all (only CPI, finance rate, loan amount, GDP growth), so
        "price elasticity" in the classic sense (%change in quantity / %change
        in price) cannot be computed from it as-is.
        Renamed the output column to make that honest, and added a real
        log-linear OLS regression in export_regression_elasticity() below
        (file 09) using loan amount as the closest available price proxy --
        which is what should be cited as "elasticity" going forward, not this
        method's percent-difference figures. See README for the actual
        regression results and how they compare to the report's claimed numbers.
        """
        print("\n Exporting Rate/GDP Sensitivity Buckets...")
        rows = []

        if self.finance_col:
            median_rate = self.df[self.finance_col].median()
            high_mask   = self.df[self.finance_col] > median_rate
            for mfg in MANUFACTURERS:
                high = self.df.loc[high_mask, mfg].mean()
                low  = self.df.loc[~high_mask, mfg].mean()
                rows.append({
                    'Manufacturer':       mfg,
                    'Metric_Type':        'Finance_Rate_Sensitivity',
                    'High_Rate_Avg_Sales': round(high, 0),
                    'Low_Rate_Avg_Sales':  round(low, 0),
                    'Sensitivity_Percent': round((high - low) / low * 100, 2) if low > 0 else None,
                })

        if self.gdp_col:
            pos_mask = self.df[self.gdp_col] > 0
            for mfg in MANUFACTURERS:
                pos = self.df.loc[pos_mask,  mfg].mean()
                neg = self.df.loc[~pos_mask, mfg].mean()
                rows.append({
                    'Manufacturer':          mfg,
                    'Metric_Type':           'GDP_Growth_Sensitivity',
                    'Positive_GDP_Avg_Sales': round(pos, 0),
                    'Negative_GDP_Avg_Sales': round(neg, 0),
                    'Sensitivity_Percent':    round((pos - neg) / neg * 100, 2) if neg > 0 else None,
                })

        return self._save(pd.DataFrame(rows), "04_sensitivity_buckets.csv")

    def export_regression_elasticity(self):
        """
        09 — Real log-linear OLS elasticity regression per manufacturer.

        TESTED 2026-09-16: added this because none of the four script versions
        in this project's history actually ran a regression despite the report
        claiming "log-linear regression" methodology. Model per manufacturer:
            ln(sales) ~ ln(New Car Loan Amt.) + CPI + GDP Growth
        New Car Loan Amt. is used as the price proxy (the closest thing to an
        actual price variable in this dataset -- there is no per-vehicle price
        column). The coefficient on ln(loan amount) is the elasticity estimate:
        the %change in sales per 1% change in average loan amount, holding CPI
        and GDP growth constant.

        Verified against the actual data 3 times (deterministic, OLS has no
        randomness): only Subaru's coefficient is statistically significant at
        p<0.05 (coefficient +1.94, meaning higher loan amounts associate with
        HIGHER Subaru sales in this data, not lower -- the opposite sign and a
        very different magnitude from the report's stated -0.76). None of the
        other four manufacturers reach significance (p>0.35 for all). This
        does not match the report's claimed elasticity figures, and the report
        should be corrected or the claim removed before this project is used
        on a resume or discussed in an interview -- see README.

        AUDITED 2026-10-21: this spec is kept for continuity, but its p-values
        are not trustworthy. Residuals are heavily autocorrelated (Durbin-Watson
        0.16 for Subaru, 0.32-1.06 for the rest; ~2 means none), and ln(loan)
        correlates 0.96 with time, so the Subaru coefficient mostly measures
        "Subaru grew while loans grew". export_regression_robustness() (file 10)
        re-fits it with a trend and in first differences.
        """
        import statsmodels.api as sm

        print("\n Exporting Regression-Based Elasticity (real OLS, log-linear)...")
        rows = []
        for mfg in MANUFACTURERS:
            cols_needed = [mfg, self.loan_col, self.cpi_col, self.gdp_col]
            if not all(cols_needed):
                continue
            d = self.df[cols_needed].dropna()
            d = d[(d[mfg] > 0) & (d[self.loan_col] > 0)]
            if len(d) < 6:
                continue
            y = np.log(d[mfg])
            X = pd.DataFrame({
                'log_loan_amt': np.log(d[self.loan_col]),
                'CPI': d[self.cpi_col].values,
                'GDP_Growth': d[self.gdp_col].values,
            })
            X = sm.add_constant(X)
            model = sm.OLS(y, X).fit()
            rows.append({
                'Manufacturer': mfg,
                'Elasticity_Coefficient_LogLoanAmt': round(model.params['log_loan_amt'], 4),
                'P_Value': round(model.pvalues['log_loan_amt'], 4),
                'Significant_at_0.05': bool(model.pvalues['log_loan_amt'] < 0.05),
                'R_Squared': round(model.rsquared, 4),
                'N_Observations': int(model.nobs),
            })

        return self._save(pd.DataFrame(rows), "09_regression_elasticity.csv")

    def regression_robustness(self):
        """
        Re-fit the loan-amount model three ways per manufacturer and say whether
        any coefficient survives all three. Returns one row per (brand, spec).

          levels        ln(sales) ~ ln(loan) + CPI + GDP           (file 09's spec)
          levels_trend  ln(sales) ~ ln(real loan) + rate + GDP + trend + H2
          differences   d.ln(sales) ~ d.ln(real loan) + d.rate + d.GDP + d.H2

        real loan = loan / CPI * 100, so inflation isn't read as a "price" rise.
        H2 is a second-half-of-year dummy (sales are semi-annual). The trend and
        differences specs use Newey-West (HAC, 2 lags) standard errors because the
        residuals are autocorrelated; Durbin-Watson is reported for each fit.
        """
        import statsmodels.api as sm
        from statsmodels.stats.stattools import durbin_watson

        if not all([self.loan_col, self.cpi_col, self.gdp_col, self.finance_col, self.period_col]):
            return pd.DataFrame()
        d = self.df.copy()
        d['ln_loan'] = np.log(d[self.loan_col])
        d['ln_real_loan'] = np.log(d[self.loan_col] / d[self.cpi_col] * 100)
        d['trend'] = np.arange(len(d))
        d['H2'] = d[self.period_col].astype(str).str.strip().str.upper().str.startswith('H2').astype(int)
        hac = {'cov_type': 'HAC', 'cov_kwds': {'maxlags': 2}}

        rows = []
        for mfg in MANUFACTURERS:
            y = np.log(d[mfg].where(d[mfg] > 0))
            specs = {
                'levels': (y, d[['ln_loan', self.cpi_col, self.gdp_col]], 'ln_loan', {}),
                'levels_trend': (y, d[['ln_real_loan', self.finance_col, self.gdp_col, 'trend', 'H2']],
                                 'ln_real_loan', hac),
                'differences': (y.diff(), d[['ln_real_loan', self.finance_col, self.gdp_col, 'H2']].diff(),
                                'ln_real_loan', hac),
            }
            for spec, (yy, X, key, fit_kw) in specs.items():
                ok = yy.notna() & X.notna().all(axis=1)
                if ok.sum() < X.shape[1] + 4:
                    continue
                fit = sm.OLS(yy[ok], sm.add_constant(X[ok])).fit(**fit_kw)
                rows.append({
                    'Manufacturer': mfg,
                    'Spec': spec,
                    'Loan_Coefficient': round(float(fit.params[key]), 4),
                    'P_Value': round(float(fit.pvalues[key]), 4),
                    'Significant_at_0.05': bool(fit.pvalues[key] < 0.05),
                    'Durbin_Watson': round(float(durbin_watson(fit.resid)), 2),
                    'N_Observations': int(fit.nobs),
                })
        out = pd.DataFrame(rows)
        if out.empty:
            return out
        # Robust = significant with the same sign in every spec that was fitted
        verdict = out.groupby('Manufacturer').apply(
            lambda g: bool(g['Significant_at_0.05'].all() and np.sign(g['Loan_Coefficient']).nunique() == 1),
            include_groups=False,
        )
        out['Robust_Across_Specs'] = out['Manufacturer'].map(verdict)
        return out

    def export_regression_robustness(self):
        """10 — Loan-amount coefficient under three specifications (see regression_robustness)."""
        print("\n Exporting Regression Robustness Checks...")
        out = self.regression_robustness()
        if not out.empty:
            wide = out.pivot(index='Manufacturer', columns='Spec', values='Loan_Coefficient')
            pv = out.pivot(index='Manufacturer', columns='Spec', values='P_Value')
            print("  Loan coefficient (p-value) by spec:")
            for mfg in wide.index:
                cells = '  '.join(f"{spec}: {wide.loc[mfg, spec]:+.2f} (p={pv.loc[mfg, spec]:.3f})"
                                  for spec in ['levels', 'levels_trend', 'differences'] if spec in wide.columns)
                print(f"    {mfg:8} {cells}")
            robust = sorted(out.loc[out['Robust_Across_Specs'], 'Manufacturer'].unique())
            print(f"  Robust across all specs: {', '.join(robust) if robust else 'none'}")
        return self._save(out, "10_regression_robustness.csv")

    def export_correlation_matrix(self):
        """05 — Long-format correlation matrix."""
        print("\n Exporting Correlation Matrix...")
        econ_cols   = [c for c in [self.cpi_col, self.finance_col, self.loan_col, self.gdp_col] if c]
        all_cols    = MANUFACTURERS + econ_cols
        corr_matrix = self.df[all_cols].corr()

        rows = [
            {'Variable_1': r, 'Variable_2': c, 'Correlation': round(corr_matrix.loc[r, c], 3)}
            for r in corr_matrix.index
            for c in corr_matrix.columns
        ]
        return self._save(pd.DataFrame(rows), "05_correlation_matrix.csv")

    def export_growth_rates(self):
        """06 — First-to-last period growth per manufacturer."""
        print("\n Exporting Growth Rates...")
        rows = []
        for mfg in MANUFACTURERS:
            first = self.df[mfg].iloc[0]
            last  = self.df[mfg].iloc[-1]
            rows.append({
                'Manufacturer':       mfg,
                'First_Period_Sales': int(first),
                'Last_Period_Sales':  int(last),
                'Absolute_Change':    int(last - first),
                'Growth_Percent':     round((last - first) / first * 100, 2),
            })
        return self._save(pd.DataFrame(rows), "06_growth_rates.csv")

    def export_time_series_analysis(self):
        """07 — One row per manufacturer per period (vectorised with melt)."""
        print("\n Exporting Time Series Data...")

        econ_keep = [c for c in [self.period_col, self.cpi_col,
                                  self.finance_col, self.loan_col, self.gdp_col] if c]
        id_vars   = list(dict.fromkeys(['Total_Sales'] + econ_keep))  # preserve order, no dupes

        df_ts = self.df.melt(
            id_vars=[c for c in id_vars if c in self.df.columns],
            value_vars=MANUFACTURERS,
            var_name='Manufacturer',
            value_name='Sales',
        )

        # Market share per row
        df_ts['Market_Share_Percent'] = (df_ts['Sales'] / df_ts['Total_Sales'] * 100).round(2)

        # Rename econ columns to clean names for Tableau
        rename = {
            self.finance_col: 'Finance_Rate',
            self.loan_col:    'Loan_Amount',
            self.gdp_col:     'GDP_Growth',
        }
        df_ts.rename(columns={k: v for k, v in rename.items() if k}, inplace=True)

        return self._save(df_ts, "07_time_series_analysis.csv")

    def export_summary_statistics(self):
        """08 — Descriptive statistics for all numeric variables."""
        print("\n Exporting Summary Statistics...")
        econ_cols = [c for c in [self.cpi_col, self.finance_col, self.loan_col, self.gdp_col] if c]

        rows = []
        for vtype, cols in [('Sales', MANUFACTURERS), ('Economic', econ_cols)]:
            for col in cols:
                s = self.df[col]
                rows.append({
                    'Variable':      col,
                    'Variable_Type': vtype,
                    'Mean':          round(s.mean(), 2),
                    'Std_Dev':       round(s.std(),  2),
                    'Min':           round(s.min(),  2),
                    'Max':           round(s.max(),  2),
                    'Median':        round(s.median(), 2),
                })
        return self._save(pd.DataFrame(rows), "08_summary_statistics.csv")

    # -------------------------------------------------------------------------
    def export_all(self):
        print("\n" + "="*80)
        print("TABLEAU DATA EXPORT")
        print("="*80)

        files = [
            self.export_raw_data(),
            self.export_long_format(),
            self.export_market_share(),
            self.export_elasticity_metrics(),
            self.export_regression_elasticity(),
            self.export_regression_robustness(),
            self.export_correlation_matrix(),
            self.export_growth_rates(),
            self.export_time_series_analysis(),
            self.export_summary_statistics(),
        ]

        print("\n" + "="*80)
        print("EXPORT COMPLETE")
        print("="*80)
        print(f"\nAll files saved to: {self.export_dir}")
        return files


# =============================================================================
# Entry point — single orchestration block
# =============================================================================

if __name__ == "__main__":
    try:
        # 1. Load data and run analysis (strips columns once, shared by both classes)
        analysis = CarSalesAnalysis(CSV_FILE)
        analysis.generate_full_report()

        # 2. Export to Tableau using the already-loaded, already-stripped DataFrame
        exporter = TableauExporter(analysis.df, EXPORT_DIR)
        exporter.export_all()

    # Exit non-zero on failure: the old handlers printed the error and exited 0,
    # so a broken run looked successful to anything checking the exit code.
    except FileNotFoundError as e:
        print(f"\n ERROR: {e}")
        print(f"Make sure '{os.path.basename(CSV_FILE)}' is in:\n  {os.path.join(PROJECT_DIR, 'data')}")
        sys.exit(1)
