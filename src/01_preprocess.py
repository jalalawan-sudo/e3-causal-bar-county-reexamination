"""
01_preprocess.py
Load and clean source datasets; produce single analytic facility and county panels.

Inputs
------
data/facilities/Table1_Facility.csv             FracTracker, 1,506 U.S. data center facilities
data/county_panel/Table2_County_AnalyticSlice.csv  3,236 U.S. counties (50 states + DC + PR)
data/county_panel/county_pm25_annual.csv        EPA Air Quality System PM2.5 medians (2018-2022)
data/county_panel/county_solar_wind_2023.csv    NREL 2023 hourly capacity factors (annualized)

Outputs
-------
data/analytic/facility_clean.parquet            Cleaned facility table with bucketed statuses
data/analytic/county_panel.parquet              Merged county panel with PM2.5, CF, region, util type
"""
import pandas as pd
import numpy as np
from paths import (FACILITY_CSV, COUNTY_CSV, PM25_CSV, SOLAR_WIND_CSV,
                   FAC_CLEAN, CTY_PANEL, TOP5_OPERATORS)


# ----------------------------- Status buckets ----------------------------- #
def bucket_status(s: str) -> str:
    """Collapse free-text status into the five canonical buckets used in figures."""
    s = str(s).lower()
    if "operat" in s:                  return "Operating"
    if "constr" in s or "under" in s:  return "UnderConstruction"
    if "susp" in s:                    return "Suspended"
    if "cancel" in s:                  return "Cancelled"
    return "Proposed"


# --------------------------- Utility-type buckets ------------------------- #
def bucket_utility(s) -> str:
    s = str(s).lower()
    if "investor" in s or "iou" in s:   return "IOU"
    if "cooper"   in s or "coop" in s:  return "Coop"
    if "munic"    in s:                 return "Muni"
    if "fed"      in s:                 return "Federal"
    return "Other"


# --------------------------- Census 4-region map -------------------------- #
CENSUS_REGION = {
    **{s: "NE"    for s in ["ME","NH","VT","MA","RI","CT","NY","NJ","PA"]},
    **{s: "MW"    for s in ["OH","IN","IL","MI","WI","MN","IA","MO",
                            "ND","SD","NE","KS"]},
    **{s: "South" for s in ["DE","MD","DC","VA","WV","NC","SC","GA","FL",
                            "KY","TN","AL","MS","AR","LA","OK","TX","PR"]},
    **{s: "West"  for s in ["MT","ID","WY","CO","NM","AZ","UT","NV",
                            "WA","OR","CA","AK","HI"]},
}


# --------------------------- Facility cleaning ---------------------------- #
def load_facilities() -> pd.DataFrame:
    fac = pd.read_csv(FACILITY_CSV, low_memory=False)
    fac["status_b"]    = fac["status_text"].apply(bucket_status)
    fac["operator_grp"] = fac["operator_text"].where(
        fac["operator_text"].isin(TOP5_OPERATORS), "Other")
    fac["county_geoid_text"] = pd.to_numeric(
        fac["county_geoid_text"], errors="coerce")
    return fac


# ---------------------------- County cleaning ----------------------------- #
def load_county_panel() -> pd.DataFrame:
    cty = pd.read_csv(COUNTY_CSV, low_memory=False,
                      dtype={"county_geoid_text": str})
    pm  = pd.read_csv(PM25_CSV, dtype={"county_geoid_text": str})
    sw  = pd.read_csv(SOLAR_WIND_CSV, dtype={"county_geoid_text": str})

    panel = (cty
             .merge(pm, on="county_geoid_text", how="left")
             .merge(sw, on="county_geoid_text", how="left"))
    panel["region"]      = panel["state_abbr_text"].map(CENSUS_REGION)
    panel["util_type_b"] = panel["mode_util_type_text_2020"].apply(bucket_utility)
    return panel


if __name__ == "__main__":
    fac = load_facilities()
    cty = load_county_panel()
    fac.to_parquet(FAC_CLEAN)
    cty.to_parquet(CTY_PANEL)
    print(f"Cleaned facilities: {len(fac):,}  -> {FAC_CLEAN.name}")
    print(f"County panel:       {len(cty):,}  -> {CTY_PANEL.name}")
    print(f"  hosts:    {int(cty['has_data_center_flag_01'].sum())}")
    print(f"  non-host: {int((cty['has_data_center_flag_01']==0).sum())}")
