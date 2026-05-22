"""
06_tariff_scoring.py
Score 77 SEPA / NCCETC DELTa large-load tariffs against a quantitative
PJM-benchmarked customer-protection rubric (Appendix A.1.6, Equation 5).

Rubric (5-point max)
    ContractPts(term) = 2 if term >= 10 yr, 1 if 5-9 yr, 0 otherwise
    MinBillPts(pct)   = 2 if pct  >= 80%,  1 if 50-79%, 0 otherwise
    CIACPts(yes/no)   = 1 if CIAC = 'Yes',                0 otherwise
    Score = ContractPts + MinBillPts + CIACPts

Inputs
------
data/tariffs/Large_Load_Tariffs_Scoring_v2.xlsx     scored output for 38 (E3) + 77 (SEPA) tariffs
data/tariffs/DELTa_2026-03-31-Public-Update_JA.xlsx raw SEPA / NCCETC DELTa database

Outputs
-------
Console: ISO-level summary mirroring Figure 13.
"""
import pandas as pd
from paths import TARIFF_SCORE_XLS


def score_term(years) -> int:
    if pd.isna(years): return 0
    y = float(years)
    if y >= 10: return 2
    if y >= 5:  return 1
    return 0


def score_minbill(pct) -> int:
    if pd.isna(pct): return 0
    p = float(pct)
    if p >= 0.80: return 2
    if p >= 0.50: return 1
    return 0


def score_ciac(val) -> int:
    return 1 if str(val).strip().lower() in ("yes", "y", "true", "1") else 0


def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["pts_term"]    = df["contract_term_years"].apply(score_term)
    df["pts_minbill"] = df["min_bill_pct"].apply(score_minbill)
    df["pts_ciac"]    = df["ciac_yes_no"].apply(score_ciac)
    df["score"]       = df["pts_term"] + df["pts_minbill"] + df["pts_ciac"]
    df["top_tier"]    = (df["score"] >= 4).astype(int)
    return df


def iso_summary(df: pd.DataFrame) -> pd.DataFrame:
    out = (df.groupby("iso_or_rto")
             .agg(n=("score", "count"),
                  mean_score=("score", "mean"),
                  share_top_tier=("top_tier", "mean"),
                  share_low=("score", lambda x: (x <= 1).mean()))
             .reset_index()
             .sort_values("mean_score", ascending=False))
    return out


if __name__ == "__main__":
    # Sheet selected per actual workbook layout
    df = pd.read_excel(TARIFF_SCORE_XLS, sheet_name="TURN DELTA Full Analysis")
    df = compute_scores(df)
    print(f"\n77-tariff universe summary:")
    print(f"  mean score = {df['score'].mean():.2f} / 5")
    print(f"  share scoring 0 or 1 = {(df['score']<=1).mean()*100:.1f}%")

    print("\nISO-level mean Customer Protection Score (sorted desc):")
    print(iso_summary(df).to_string(index=False, float_format=lambda x: f"{x:.3f}"))
