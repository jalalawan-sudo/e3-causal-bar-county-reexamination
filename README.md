# The Causal Bar E3 Did Not Clear
### A County-Level Re-Examination of Data Centers and Rates

**Author:** Jalal Awan, Ph.D. — Independent Researcher  · [jonesawan.com](https://www.jonesawan.com)  · [Google Scholar](https://scholar.google.com/citations?user=0A3_DZUAAAAJ&hl=en)

This repository contains the public-data pipeline, statistical analysis, and figures used in the response paper to E3's May 2026 whitepaper *Understanding the Drivers of Rising Electricity Rates and the Role of Data Centers* (funded by the Data Center Coalition). The paper finds that E3's central claim, that there is no historical evidence of cost-shifting from data centers to residential or small-commercial ratepayers, is **undetermined** rather than supported on the assembled evidence, and that the unit of analysis (state-level) cannot detect the cost shift it purports to rule out.

---

## Why this exists

The historical association between large-load growth and stable residential rates documented in earlier literature (Wiser et al., 2025) is real. The question is whether it survives the structural cost re-pricing of 2022–2026 (transformer prices up 89%, conductor up 152%, utility long-term debt at 5–6% against rate-base embedded at 3–4%) and the EPRI-projected 17% share of total U.S. electricity demand by 2030. The data assembled here, at the county and feeder level rather than the state level, suggests it does not.

---

## Datasets used

All datasets are public. Full names, sources, and direct hyperlinks below; per-row schemas live in `data/<subfolder>/`.

| Dataset (full name) | File | Source |
|---|---|---|
| FracTracker Alliance U.S. Data Center Database (January 2026 snapshot, 1,506 facilities) | `data/facilities/Table1_Facility.csv` | [fractracker.org](https://www.fractracker.org/) |
| U.S. County Analytic Slice (NREL SLOPE + ACS + DOE LEAD + FCC + USGS + CDC, 3,236 counties) | `data/county_panel/Table2_County_AnalyticSlice.csv` | NREL [SLOPE](https://maps.nrel.gov/slope/), Census [ACS](https://www.census.gov/programs-surveys/acs), DOE [LEAD](https://www.energy.gov/scep/slsc/lead-tool), FCC [Form 477](https://www.fcc.gov/general/broadband-deployment-data-fcc-form-477), USGS [Water Use 2015](https://www.usgs.gov/mission-areas/water-resources/science/water-use-united-states), CDC [SVI 2018](https://www.atsdr.cdc.gov/placeandhealth/svi/index.html) |
| EPA Air Quality System County PM2.5 Medians (2018–2022) | `data/county_panel/county_pm25_annual.csv` | [EPA AQS](https://www.epa.gov/aqs) |
| NREL 2023 County Solar UPV (Fixed-Tilt) and 100m Onshore Wind Annual Capacity Factors | `data/county_panel/county_solar_wind_2023.csv` | [NREL ReV 2023](https://www.nrel.gov/gis/renewable-energy-potential.html) |
| SEPA and NCCETC DELTa: Database of Emerging Large Load Tariffs (March 31, 2026 update, 77 tariffs across 36 states) | `data/tariffs/DELTa_2026-03-31-Public-Update_JA.xlsx` | [SEPA Large Load Tariffs Database](https://sepapower.org/large-load-tariffs-database/) |
| Large-Load Tariffs Customer-Protection Scoring (E3 n=38 + SEPA n=77, scored against PJM benchmark rubric) | `data/tariffs/Large_Load_Tariffs_Scoring_v2.xlsx` | Author-built, anchored on Halcyon (2026) PJM benchmark |
| E3 (2026) Source Whitepaper | `data/source_paper/Understanding-the-Drivers-of-Rising-Electricity-Rates-and-the-Role-of-Data-Centers_E3-2026.pdf` | [E3 publications](https://www.ethree.com/publications/) |
| EIA Form 861 / 861M Retail Electricity (state-level rates, sales, residential disconnections, 2024) | (state panel referenced indirectly via `Table2_County_AnalyticSlice.csv`) | [EIA-861](https://www.eia.gov/electricity/data/eia861/) |

The full paper (`paper/Awan_DataCenter_E3_Response_*.docx`) and the EPRI 2024 and LBNL Shehabi 2024 cross-check references are cited inline; both upstream PDFs are publicly available at [EPRI](https://www.epri.com/research/products/3002028905) and [LBNL](https://eta.lbl.gov/publications/2024-united-states-data-center).

---

## Repository layout

```
e3-causal-bar-county-reexamination/
├── README.md
├── LICENSE
├── requirements.txt
├── data/
│   ├── facilities/             FracTracker Jan 2026 (1 file)
│   ├── county_panel/           NREL SLOPE + EPA + NREL ReV merged county-level (3 files)
│   ├── tariffs/                SEPA / NCCETC DELTa + author scoring (2 files)
│   ├── source_paper/           E3 (2026) PDF for reference
│   └── analytic/               (produced) cleaned parquet outputs from src/01–02
├── src/
│   ├── paths.py                single source of truth for filesystem paths
│   ├── 01_preprocess.py        load and clean source data
│   ├── 02_mw_imputation.py     log-log OLS with status fixed effects (Eq. 1)
│   ├── 03_descriptive_analysis.py
│   ├── 04_host_vs_nonhost.py   Welch t-tests, 10 indicators (Table A4)
│   ├── 05_nb_regression.py     negative-binomial GLM with FE (Eq. 2, Table A3)
│   ├── 06_tariff_scoring.py    PJM-benchmarked rubric (Eq. 5)
│   ├── 07_figures.py           all 13 paper figures
│   └── run_all.py              pipeline driver
├── figures/                    (produced) PNGs at 300 dpi
└── paper/                      final .docx of the paper
```

---

## Workflow

```
                              ┌────────────────────────────────────────┐
        Raw public datasets ──▶│  01_preprocess.py                      │
                              │  bucket statuses; merge PM2.5 + CF;     │
                              │  assign Census region + utility-type FE │
                              └──────────────────┬─────────────────────┘
                                                 ▼
                              ┌────────────────────────────────────────┐
                              │  02_mw_imputation.py                   │
                              │  log10(MW) = β0 + β1 log10(sqft) + αs  │
                              │  R² = 0.7545 (with status FE)          │
                              └──────────────────┬─────────────────────┘
                                                 ▼
        ┌──────────────────────────────┬─────────┴────────────┬──────────────────────────┐
        ▼                              ▼                      ▼                          ▼
┌─────────────────┐         ┌──────────────────────┐ ┌───────────────────┐    ┌──────────────────────┐
│ 03_descriptive  │         │ 04_host_vs_nonhost   │ │ 05_nb_regression  │    │ 06_tariff_scoring    │
│ top-N states,   │         │ Welch tests (10      │ │ NB GLM with util- │    │ rubric vs SEPA n=77; │
│ Pareto curve    │         │ indicators)          │ │ type & region FE  │    │ ISO-level summary    │
└────────┬────────┘         └──────────┬───────────┘ └────────┬──────────┘    └──────────┬───────────┘
         └────────────────────────────┬┴──────────────────────┴────────────────────────┬─┘
                                      ▼                                                ▼
                                                  07_figures.py
                                          (13 PNGs at 300 dpi, no inline titles)
```

---

## Reproducing the analysis

```bash
git clone https://github.com/jalalawan-sudo/e3-causal-bar-county-reexamination.git
cd e3-causal-bar-county-reexamination
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/run_all.py
```

The full pipeline runs in roughly two minutes on a laptop. The `data/analytic/` cache and `figures/` directory are produced from scratch on each run; nothing is committed there.

---

## Headline findings

1. **State-level cannot detect the cost shift it purports to rule out.** The top 30 U.S. counties hold 50 percent of all announced data center MW, and 487 of 3,236 counties carry every operational and in-progress build. Cost recovery happens at the utility service territory, not the state.

2. **The historical "load growth lowers rates" association is a selection effect at the county level.** Data centers concentrate in counties that already had below-average residential rates and below-average rate-of-increase, before the data centers arrived.

3. **Hosting counties carry systematically heavier environmental and equity burden.** PM2.5 +9% (p < 1e-29), GHG 2.3x, freshwater 3.5x, broadband 5.9x, Black population share 4.3x non-host medians (all p < 0.001 except SVI). Marginal load lands on already-stressed baselines.

4. **The tariff catalogue scores poorly when scored, not counted.** Full SEPA / NCCETC universe (n=77) mean Customer Protection Score is 1.94 of 5; 51% of tariffs score 0 or 1. PJM averages 2.26, CAISO 0.64 (weakest ISO). E3 reports only 38 of these 77 without explaining the selection.

---

## Statistical specifications

| # | Method | Where in paper | Where in code |
|---|---|---|---|
| 1 | OLS, log-log, status fixed effects | Appendix A.1.2, Equation 1 | `src/02_mw_imputation.py` |
| 2 | Negative binomial GLM, utility-type and region FE | Appendix A.1.3, Equation 2, Table A3 | `src/05_nb_regression.py` |
| 3 | Welch's t-test (unequal variances) | Appendix A.1.4, Equation 3, Table A4 | `src/04_host_vs_nonhost.py` |
| 4 | Spearman rank correlation | Appendix A.1.5, Equation 4 | `src/03_descriptive_analysis.py` |
| 5 | Customer Protection Score rubric | Appendix A.1.6, Equation 5, Table 4 | `src/06_tariff_scoring.py` |

---

## Citation

> Awan, J. (May 2026). *The Causal Bar E3 Did Not Clear: A County-Level Re-Examination of Data Centers and Rates.* Working draft. Available at jonesawan.com.

BibTeX:
```bibtex
@misc{awan2026e3reexamination,
  title  = {The Causal Bar E3 Did Not Clear: A County-Level Re-Examination of Data Centers and Rates},
  author = {Awan, Jalal},
  year   = {2026},
  month  = {may},
  note   = {Working draft. https://github.com/jalalawan-sudo/e3-causal-bar-county-reexamination}
}
```

---

## License

Code: MIT. Data: each source dataset retains its original license (FracTracker, EPA, NREL, USGS, Census, FCC, DOE, CDC, SEPA / NCCETC). See `LICENSE`.

---

## Contact

Questions, errata, or methodology challenges welcome. Open an issue or reach the author through [jonesawan.com](https://www.jonesawan.com).
