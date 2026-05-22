"""
02_mw_imputation.py
MW imputation via log-log OLS on floor area with status fixed effects.

Spec (Appendix A.1.2, Equation 1):
    log10(MW)_i = beta_0 + beta_1 * log10(sqft)_i + alpha_status + epsilon_i
    alpha_status: 3-level fixed effect (Operating reference; UnderConstruction, Pipeline)

Trained on the 329 facilities reporting both nameplate MW and floor area.

Inputs
------
data/analytic/facility_clean.parquet            from 01_preprocess.py

Outputs
-------
data/analytic/facility_imputed.parquet          adds mw_imputed and mw_source columns
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from paths import FAC_CLEAN, FAC_IMPUTED


def fit_imputation_model(fac: pd.DataFrame):
    """Fit log-log OLS with status FE on facilities reporting both MW and sqft."""
    train = fac.dropna(subset=["mw_numeric_mw", "sqft_numeric_sqft"]).copy()
    train = train[(train["mw_numeric_mw"] > 0) & (train["sqft_numeric_sqft"] > 0)]
    train["log_mw"]   = np.log10(train["mw_numeric_mw"])
    train["log_sqft"] = np.log10(train["sqft_numeric_sqft"])

    model = smf.ols(
        "log_mw ~ log_sqft + C(status_b, Treatment(reference='Operating'))",
        data=train).fit()
    return model, train


def impute_mw(fac: pd.DataFrame, model) -> pd.DataFrame:
    """For rows with sqft but no MW, predict MW from the fitted model."""
    needs = (fac["mw_numeric_mw"].isna()
             & fac["sqft_numeric_sqft"].notna()
             & (fac["sqft_numeric_sqft"] > 0))
    pred = fac.loc[needs].copy()
    pred["log_sqft"] = np.log10(pred["sqft_numeric_sqft"])
    pred["mw_pred"]  = 10 ** model.predict(pred)

    fac["mw_imputed"] = fac["mw_numeric_mw"].copy()
    fac.loc[needs, "mw_imputed"] = pred["mw_pred"]
    fac["mw_source"] = np.where(fac["mw_numeric_mw"].notna(), "reported", "imputed")
    fac.loc[fac["mw_imputed"].isna(), "mw_source"] = "missing"
    return fac


if __name__ == "__main__":
    fac = pd.read_parquet(FAC_CLEAN)
    model, train = fit_imputation_model(fac)
    print(f"Imputation OLS trained on N={int(model.nobs)} facilities")
    print(f"  R^2 = {model.rsquared:.4f}  (adj {model.rsquared_adj:.4f})")
    print(f"  log_sqft slope = {model.params['log_sqft']:+.4f}  "
          f"95% CI [{model.conf_int().loc['log_sqft', 0]:.4f}, "
          f"{model.conf_int().loc['log_sqft', 1]:.4f}]")

    fac = impute_mw(fac, model)
    fac.to_parquet(FAC_IMPUTED)

    op = fac[fac["status_b"] == "Operating"]
    print(f"\nOperating capacity:")
    print(f"  reported only  : N={int(op['mw_numeric_mw'].notna().sum())}, "
          f"sum = {op['mw_numeric_mw'].sum()/1000:.2f} GW")
    print(f"  after imputation: N={int(op['mw_imputed'].notna().sum())}, "
          f"sum = {op['mw_imputed'].sum()/1000:.2f} GW")
