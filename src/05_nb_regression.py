"""
05_nb_regression.py
Negative-binomial GLM for facility count per county (Appendix A.1.3, Equation 2).

Spec:
    Y_i ~ NegBin(mu_i, alpha = 1.0)        (Poisson fallback if NB fails)
    log(mu_i) = beta_0 + sum_j beta_j * X_ij
                       + gamma_u * 1{util_type = u}      (IOU reference)
                       + delta_r * 1{region    = r}      (South reference)

Inputs
------
data/analytic/county_panel.parquet

Outputs
-------
Console: coefficient table sorted by p-value (Table A3 in paper).
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from paths import CTY_PANEL


NB_FEATURES = [
    # Size / demand
    "log_pop", "log_bldg",
    # Electricity
    "res_rate_usd_per_kwh_2020", "lcoe_mean_usd_per_mwh_2024",
    # Infrastructure / resource
    "log_bb", "log_water", "log_re",
    # Environment / equity
    "pm25_median_ugm3_2018_2022", "log_ghg",
    "energy_burden_pct_2020", "svi_pctile_2018",
    "black_pct_2020", "hispanic_pct_2020", "lmi_hh_pct_2020",
]


def add_logs(df: pd.DataFrame) -> pd.DataFrame:
    """Build log10-transformed covariates with floor=1 to handle zeros."""
    def log10p(x, floor=1):
        return np.log10(np.maximum(x.fillna(floor), floor))
    df["log_pop"]   = log10p(df["total_pop_count_2020"])
    df["log_bldg"]  = log10p(df["bldg_commercial_sqft_2020"])
    df["log_bb"]    = log10p(df["bb_total_conns_thousands_2024"])
    df["log_water"] = log10p(df["water_total_freshwater_mgalday_2015"])
    df["log_ghg"]   = log10p(df["ghg_grand_total_mt_2020"])
    df["log_re"]    = log10p(df["renewable_total_mwh_2020"])
    df["n_fac"]     = df["n_facilities_count"].fillna(0).astype(int)
    return df


def fit_nb(df: pd.DataFrame, outcome: str = "n_fac"):
    formula = (f"{outcome} ~ " + " + ".join(NB_FEATURES)
               + " + C(util_type_b, Treatment(reference='IOU'))"
               + " + C(region,      Treatment(reference='South'))")
    try:
        return smf.glm(formula, data=df,
                       family=sm.families.NegativeBinomial(alpha=1.0)).fit()
    except Exception:
        return smf.glm(formula, data=df, family=sm.families.Poisson()).fit()


def coefficient_table(model) -> pd.DataFrame:
    ci = model.conf_int()
    rows = []
    for name, b, p in zip(model.params.index,
                          model.params.values,
                          model.pvalues.values):
        if name == "Intercept": continue
        rows.append({
            "covariate": name,
            "beta":      b,
            "IRR":       np.exp(b),
            "CI_lo":     np.exp(ci.loc[name, 0]),
            "CI_hi":     np.exp(ci.loc[name, 1]),
            "p":         p,
        })
    return pd.DataFrame(rows).sort_values("p")


if __name__ == "__main__":
    panel = pd.read_parquet(CTY_PANEL)
    panel = add_logs(panel)
    df = panel.dropna(subset=NB_FEATURES + ["util_type_b", "region"]).copy()
    print(f"NB sample: N = {len(df):,} counties")
    print(f"  with at least 1 facility: {(df['n_fac'] >= 1).sum()}")

    model = fit_nb(df)
    print(f"\nNB fit: log-lik = {model.llf:.1f}, AIC = {model.aic:.1f}")

    tbl = coefficient_table(model)
    print("\nCoefficients sorted by p-value:")
    print(tbl.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
