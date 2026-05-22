"""
07_figures.py
Generate all 13 paper figures. Each function writes a single PNG to figures/.

Conventions
-----------
- 300 dpi PNG, Times New Roman, no inline figure titles (details live in captions).
- 5-panel host vs non-host figure uses the common subset for visual consistency.
- US choropleth / bubble map uses U.S. Census 2023 cartographic boundary (20m).

Inputs
------
data/analytic/facility_imputed.parquet
data/analytic/county_panel.parquet

Outputs
-------
figures/v7_fig_mw_sqft_methods.png
figures/v7_fig_operating_map.png
figures/v7_fig_top20_status_stack.png
figures/v7_fig_top20_states.png
figures/v7_fig_pareto.png
figures/v7_fig_state_county.png
figures/v7_fig_solar_cf_pct.png
figures/v7_fig_wind_cf_pct.png
figures/v7_fig_hostvs_main.png
figures/v7_fig_ghg.png
figures/v7_fig_broadband_water.png
figures/v7_fig_e3_vs_sepa.png
figures/v7_fig_iso_scores.png
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from paths import FAC_IMPUTED, CTY_PANEL, FIG_DIR, OP_COLORS, TOP5_OPERATORS

plt.rcParams.update({
    "figure.dpi":      130,
    "savefig.dpi":     300,
    "font.family":     "Times New Roman",
    "font.size":       10,
    "axes.titlesize":  11,
    "axes.spines.top": False, "axes.spines.right": False,
})


# ----------------- Figure 1: MW vs sqft scatter ----------------- #
def fig_mw_sqft_methods(fac: pd.DataFrame, out: str) -> None:
    """Scatter of nameplate MW vs floor area, colored by operator, log-log fit overlaid."""
    ...


# ----------------- Figure 2: US operating bubble map ------------ #
def fig_operating_map(fac: pd.DataFrame, states_shp: gpd.GeoDataFrame,
                      out: str) -> None:
    """Lower-48 county bubbles sized by imputed MW; colored by top operator at county."""
    ...


# ----------------- Figure 3: Top 20 states stacked by status ---- #
def fig_top20_status_stack(fac: pd.DataFrame, out: str) -> None:
    """Horizontal stacked bars: Operating / UnderConstruction / Proposed / Suspended / Cancelled."""
    ...


# ----------------- Figure 4: Top 20 states plain bars ----------- #
def fig_top20_states(fac: pd.DataFrame, out: str) -> None:
    ...


# ----------------- Figure 5: County Pareto curve ---------------- #
def fig_pareto(fac: pd.DataFrame, out: str) -> None:
    """Cumulative share of announced MW vs county rank; mark 50/80/90% thresholds."""
    ...


# ----------------- Figure 6: Top 5 states by top 5 counties ----- #
def fig_state_county(fac: pd.DataFrame, out: str) -> None:
    ...


# ----------------- Figures 7-8: Solar / wind CF vs DC capacity --- #
def fig_renewable_cf(panel: pd.DataFrame, resource: str, out: str) -> None:
    """resource in {'solar', 'wind'}. CF in % on x-axis, announced DC MW on y."""
    ...


# ----------------- Figure 9: Host vs non-host 5-panel ----------- #
def fig_hostvs_main(panel: pd.DataFrame, out: str) -> None:
    """PM2.5 / Black / Hispanic / Energy burden / SVI box-and-whisker, common subset."""
    ...


# ----------------- Figure 10: GHG host vs non-host -------------- #
def fig_ghg(panel: pd.DataFrame, out: str) -> None:
    ...


# ----------------- Figure 11: Broadband + freshwater ------------ #
def fig_broadband_water(panel: pd.DataFrame, out: str) -> None:
    ...


# ----------------- Figure 12: E3 (n=38) vs SEPA (n=77) ---------- #
def fig_e3_vs_sepa(scored_tariffs: pd.DataFrame, out: str) -> None:
    ...


# ----------------- Figure 13: ISO-level mean scores ------------- #
def fig_iso_scores(scored_tariffs: pd.DataFrame, out: str) -> None:
    ...


if __name__ == "__main__":
    fac   = pd.read_parquet(FAC_IMPUTED)
    panel = pd.read_parquet(CTY_PANEL)
    states = gpd.read_file(
        "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_state_20m.zip")

    fig_mw_sqft_methods   (fac,   FIG_DIR / "v7_fig_mw_sqft_methods.png")
    fig_operating_map     (fac, states, FIG_DIR / "v7_fig_operating_map.png")
    fig_top20_status_stack(fac,   FIG_DIR / "v7_fig_top20_status_stack.png")
    fig_top20_states      (fac,   FIG_DIR / "v7_fig_top20_states.png")
    fig_pareto            (fac,   FIG_DIR / "v7_fig_pareto.png")
    fig_state_county      (fac,   FIG_DIR / "v7_fig_state_county.png")
    fig_renewable_cf      (panel, "solar", FIG_DIR / "v7_fig_solar_cf_pct.png")
    fig_renewable_cf      (panel, "wind",  FIG_DIR / "v7_fig_wind_cf_pct.png")
    fig_hostvs_main       (panel, FIG_DIR / "v7_fig_hostvs_main.png")
    fig_ghg               (panel, FIG_DIR / "v7_fig_ghg.png")
    fig_broadband_water   (panel, FIG_DIR / "v7_fig_broadband_water.png")
    # fig_e3_vs_sepa / fig_iso_scores read scored tariffs from 06_tariff_scoring.py output
