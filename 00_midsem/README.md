# Mid-semester submission (archived)

This folder is the mid-semester version of the project, kept unchanged so the original submission can still be checked.

**It has been superseded.** The elk and wolf analysis continues in `../01_yellowstone_elk_wolves/`, which has corrected data (whole-herd elk counts, audited corrections in `data/corrections/`) and updated versions of notebooks 01 and 02.

## Contents

| Path | What it is |
|---|---|
| `notebooks/01_eda_stationarity_arma.ipynb` | Exploratory plots, ADF tests, ACF/PACF and ARMA identification on the first dataset |
| `notebooks/02_arimax_granger_forecast.ipynb` | Granger tests, ARIMAX and forecasts on the first dataset |
| `data/raw/` | Source files as downloaded for the midsem (elk, wolves, bison, NDVI, precipitation, drought, hunting harvest, bison report) |
| `data/processed/yellowstone_master_ts_final.csv`, `yellowstone_master_ts_flagged.csv` | Midsem master datasets. **Do not use for new work**; use Part 1's corrected file instead. |
| `scripts/build_master_dataset.py`, `build_master_flagged.py` | Scripts that built the midsem master datasets |
| `reports/figures/` | Midsem figures and tables (01–07) |

The notebooks find `data/` from this folder, so open `notebooks/` here to rerun them.
