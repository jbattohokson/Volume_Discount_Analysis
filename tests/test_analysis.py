"""Tests for the regression and sensitivity logic.

Run: python -m pytest tests/
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "python"))
import japanese_car_elasticity_analysis as jca  # noqa: E402

DATA = ROOT / "data" / "Japanese_Car_Sales_Elasticity.csv"


def exporter_for(df, tmp_path):
    return jca.TableauExporter(df, str(tmp_path))


@pytest.fixture
def real_df():
    df = pd.read_csv(DATA)
    df.columns = df.columns.str.strip()
    df['Total_Sales'] = df[jca.MANUFACTURERS].sum(axis=1)
    return df


def synthetic(n=40, elasticity=-1.2, seed=0):
    """Sales built from a known loan elasticity, plus a trend in loans and noise."""
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    cpi = 130 + 1.2 * t
    loan = 25000 * np.exp(0.01 * t + rng.normal(0, 0.05, n))
    df = pd.DataFrame({
        'Semi-Annual Year': [f"H{1 + i % 2} {2008 + i // 2}" for i in t],
        'CPI': cpi,
        'Finance Rate of New Car (Weighted)': 5 + rng.normal(0, 0.5, n),
        'New Car Loan Amt.': loan,
        'GDP Growth': rng.normal(2, 1, n),
    })
    real = loan / cpi * 100
    for i, m in enumerate(jca.MANUFACTURERS):
        df[m] = np.exp(12 + i * 0.1 + elasticity * np.log(real) + 0.01 * t + rng.normal(0, 0.01, n))
    df['Total_Sales'] = df[jca.MANUFACTURERS].sum(axis=1)
    return df


def test_robustness_recovers_a_planted_elasticity(tmp_path):
    out = exporter_for(synthetic(), tmp_path).regression_robustness()
    for spec in ('levels_trend', 'differences'):
        coefs = out.loc[out.Spec == spec, 'Loan_Coefficient']
        assert coefs.between(-1.4, -1.0).all(), (spec, coefs.tolist())
    # Trend + differences agree on sign and significance -> flagged robust
    trend_diff = out[out.Spec != 'levels']
    assert trend_diff['Significant_at_0.05'].all()


def test_robustness_on_real_data_finds_nothing_robust(real_df, tmp_path):
    out = exporter_for(real_df, tmp_path).regression_robustness()
    assert len(out) == 15
    assert not out['Robust_Across_Specs'].any()
    sub = out[out.Manufacturer == 'Subaru'].set_index('Spec')
    # The headline +1.94 from the old spec, and its sign flip once trend is controlled
    assert sub.loc['levels', 'Loan_Coefficient'] == pytest.approx(1.9438, abs=1e-3)
    assert sub.loc['levels', 'Durbin_Watson'] < 0.5
    assert sub.loc['levels_trend', 'Loan_Coefficient'] < 0
    assert not sub.loc['differences', 'Significant_at_0.05']


def test_levels_spec_matches_file_09(real_df, tmp_path):
    exp = exporter_for(real_df, tmp_path)
    nine = pd.read_csv(exp.export_regression_elasticity()).set_index('Manufacturer')
    rob = exp.regression_robustness().query("Spec == 'levels'").set_index('Manufacturer')
    pd.testing.assert_series_equal(nine['Elasticity_Coefficient_LogLoanAmt'], rob['Loan_Coefficient'],
                                   check_names=False)


def test_zero_sales_period_is_skipped_not_crashed(tmp_path):
    df = synthetic()
    df.loc[5, 'Subaru'] = 0  # log(0) would be -inf
    out = exporter_for(df, tmp_path).regression_robustness()
    sub = out[out.Manufacturer == 'Subaru'].set_index('Spec')
    assert sub.loc['levels', 'N_Observations'] == len(df) - 1
    assert np.isfinite(out['Loan_Coefficient']).all()


def test_missing_columns_return_empty(tmp_path):
    df = synthetic().drop(columns=['New Car Loan Amt.'])
    assert exporter_for(df, tmp_path).regression_robustness().empty


def test_sensitivity_buckets_on_known_split(tmp_path):
    df = synthetic(n=4)
    df['Finance Rate of New Car (Weighted)'] = [1, 2, 3, 4]
    df['Toyota'] = [100, 100, 150, 150]
    out = pd.read_csv(exporter_for(df, tmp_path).export_elasticity_metrics())
    row = out[(out.Manufacturer == 'Toyota') & (out.Metric_Type == 'Finance_Rate_Sensitivity')].iloc[0]
    assert row['Sensitivity_Percent'] == pytest.approx(50.0)


def test_growth_rates_match_page(real_df, tmp_path):
    out = pd.read_csv(exporter_for(real_df, tmp_path).export_growth_rates()).set_index('Manufacturer')
    assert out.loc['Toyota', 'Growth_Percent'] == pytest.approx(2.35, abs=0.01)
    assert out.loc['Subaru', 'Growth_Percent'] == pytest.approx(170.84, abs=0.01)
