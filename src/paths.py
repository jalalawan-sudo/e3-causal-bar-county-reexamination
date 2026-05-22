"""
00_paths.py
Single source of truth for filesystem paths used across the pipeline.
Import this in every other script.
"""
from pathlib import Path

ROOT     = Path(__file__).resolve().parent.parent
DATA     = ROOT / "data"
FAC_DIR  = DATA / "facilities"
CTY_DIR  = DATA / "county_panel"
TAR_DIR  = DATA / "tariffs"
ANL_DIR  = DATA / "analytic"
FIG_DIR  = ROOT / "figures"

# Inputs
FACILITY_CSV     = FAC_DIR / "Table1_Facility.csv"
COUNTY_CSV       = CTY_DIR / "Table2_County_AnalyticSlice.csv"
PM25_CSV         = CTY_DIR / "county_pm25_annual.csv"
SOLAR_WIND_CSV   = CTY_DIR / "county_solar_wind_2023.csv"
TARIFF_SCORE_XLS = TAR_DIR / "Large_Load_Tariffs_Scoring_v2.xlsx"
DELTA_XLS        = TAR_DIR / "DELTa_2026-03-31-Public-Update_JA.xlsx"

# Intermediates
FAC_CLEAN        = ANL_DIR / "facility_clean.parquet"
FAC_IMPUTED      = ANL_DIR / "facility_imputed.parquet"
CTY_PANEL        = ANL_DIR / "county_panel.parquet"

ANL_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

TOP5_OPERATORS = ["Amazon (AWS)", "Microsoft", "Google", "Meta", "QTS"]
OP_COLORS = {
    "Amazon (AWS)": "#FF7F00", "Microsoft": "#0E7C66", "Google": "#D62728",
    "Meta": "#6A3D9A", "QTS": "#FFCC00", "Other": "#9CA3AF",
}
