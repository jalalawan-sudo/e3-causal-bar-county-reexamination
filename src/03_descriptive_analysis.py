"""
03_descriptive_analysis.py
Descriptive statistics for the build-out:
  - Top-N states by facility count, broken out by pipeline status
  - Operating GW by state after imputation (top-15 table)
  - County-level Pareto curve over announced MW
  - Cluster summary (top hubs: Loudoun, Maricopa, Fulton, etc.)

Inputs
------
data/analytic/facility_imputed.parquet

Outputs
-------
Console tables; figures are produced in 07_figures.py.
"""
import pandas as pd
import numpy as np
from paths import FAC_IMPUTED


def top_states_by_status(fac: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    xt = pd.crosstab(fac["state_code_text"], fac["status_b"])
    xt["total"] = xt.sum(axis=1)
    return xt.sort_values("total", ascending=False).head(n)


def operating_gw_by_state(fac: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    op = fac[(fac["status_b"] == "Operating") & (fac["mw_imputed"] > 0)]
    by_st = (op.groupby("state_code_text")
               .agg(n_op=("facility_name_text", "count"),
                    gw=("mw_imputed", lambda x: x.sum() / 1000))
               .reset_index()
               .sort_values("gw", ascending=False))
    by_st["share_pct"] = by_st["gw"] / by_st["gw"].sum() * 100
    return by_st.head(n)


def county_pareto(fac: pd.DataFrame) -> pd.DataFrame:
    """Cumulative share of announced MW vs county rank, across all statuses."""
    by_co = (fac.dropna(subset=["mw_imputed"])
                .groupby("county_geoid_text")["mw_imputed"]
                .sum().sort_values(ascending=False))
    cum = by_co.cumsum() / by_co.sum() * 100
    return cum.to_frame(name="cum_share_pct")


def cluster_summary(fac: pd.DataFrame) -> pd.DataFrame:
    op = fac[(fac["status_b"] == "Operating") & (fac["mw_imputed"] > 0)]
    agg = (op.groupby("county_geoid_text")
             .agg(state=("state_code_text", "first"),
                  county=("county_name_text", "first"),
                  n_fac=("facility_name_text", "count"),
                  gw=("mw_imputed", lambda x: x.sum() / 1000))
             .reset_index()
             .sort_values("gw", ascending=False))
    return agg.head(15)


if __name__ == "__main__":
    fac = pd.read_parquet(FAC_IMPUTED)

    print("\n=== Top 20 states by facility count, stacked by status ===")
    print(top_states_by_status(fac).to_string())

    print("\n=== Top 15 states by operating GW (post-imputation) ===")
    print(operating_gw_by_state(fac).to_string(index=False))

    print("\n=== County Pareto (top 10 + key thresholds) ===")
    p = county_pareto(fac)
    print(p.head(10))
    thresh = [50, 80, 90]
    for t in thresh:
        rank = (p["cum_share_pct"] >= t).idxmax()
        rk_pos = int((p["cum_share_pct"] < t).sum()) + 1
        print(f"  Counties needed for {t}% of MW: {rk_pos}")

    print("\n=== Top 15 county clusters (operating, post-imputation) ===")
    print(cluster_summary(fac).to_string(index=False))
