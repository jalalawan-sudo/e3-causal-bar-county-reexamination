"""
04_host_vs_nonhost.py
Welch t-tests on host vs non-host counties across environmental, equity,
infrastructure, and rate indicators (Appendix A.1.4, Equation 3 + Table A4).

Notes
-----
- Welch's t-test compares MEANS under unequal variances and unequal sample sizes.
- Reported percent-difference uses MEDIANS (the visual quantity in the boxplots).
- For heavily skewed indicators (broadband, freshwater, GHG) we log-transform
  and report the ratio of geometric means.

Inputs
------
data/analytic/county_panel.parquet

Outputs
-------
Console table mirroring Table A4 in the paper.
"""
import numpy as np
import pandas as pd
from scipy import stats
from paths import CTY_PANEL


INDICATORS = [
    # (label, column, log_transform?)
    ("PM2.5 (ug/m3)",            "pm25_median_ugm3_2018_2022",          False),
    ("Black share (%)",          "black_pct_2020",                       False),
    ("Hispanic share (%)",       "hispanic_pct_2020",                    False),
    ("Energy burden (fraction)", "energy_burden_pct_2020",               False),
    ("SVI (0-1)",                "svi_pctile_2018",                      False),
    ("GHG total (Mt CO2e)",      "ghg_grand_total_mt_2020",              True),
    ("Broadband total (000s)",   "bb_total_conns_thousands_2024",        True),
    ("Freshwater (MGD)",         "water_total_freshwater_mgalday_2015",  True),
    ("Residential rate ($/kWh)", "res_rate_usd_per_kwh_2020",            False),
    ("LMI household share (%)",  "lmi_hh_pct_2020",                      False),
]


def welch_test(host: np.ndarray, non: np.ndarray, log: bool = False) -> dict:
    """Welch t-stat, Welch-Satterthwaite df, two-sided p, and percent / ratio effect."""
    if log:
        host_ = np.log10(host[host > 0]); non_ = np.log10(non[non > 0])
    else:
        host_, non_ = host, non
    t, p = stats.ttest_ind(host_, non_, equal_var=False)
    s1, s2 = host_.var(ddof=1), non_.var(ddof=1)
    n1, n2 = len(host_), len(non_)
    df_w   = (s1/n1 + s2/n2)**2 / ((s1/n1)**2/(n1-1) + (s2/n2)**2/(n2-1))
    medh, medn = np.median(host), np.median(non)
    if log:
        effect = ("ratio_geomean", 10 ** (host_.mean() - non_.mean()))
    elif medn != 0:
        effect = ("pct_diff_median", (medh - medn) / abs(medn) * 100)
    else:
        effect = ("pct_diff_median", np.nan)
    return dict(t=t, df=df_w, p=p, n_h=n1, n_nh=n2,
                med_h=medh, med_nh=medn, effect=effect)


def run_all(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, col, log in INDICATORS:
        sub = panel[[col, "has_data_center_flag_01"]].dropna()
        h  = sub.loc[sub["has_data_center_flag_01"] == 1, col].values
        nh = sub.loc[sub["has_data_center_flag_01"] == 0, col].values
        r = welch_test(h, nh, log=log)
        r["indicator"] = label
        rows.append(r)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    panel = pd.read_parquet(CTY_PANEL)
    out = run_all(panel)
    print(out[["indicator", "n_h", "n_nh", "med_h", "med_nh",
               "effect", "t", "df", "p"]].to_string(index=False))
