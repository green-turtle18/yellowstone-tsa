# Part 2 · Vegetation, snow and river

The **bottom-up and water side** of the trophic-cascade debate. If wolves helped riverside willows by reducing elk browsing, the riverside should have greened relative to nearby slopes after 1995. If water limits willows instead, riverside greenness should track summer river flow more closely than elk numbers. Snowpack and river timing set that water, so they are analysed here too.

## Notebooks

| Notebook | Question | Methods |
|---|---|---|
| `07_eda_snow_river_vegetation.ipynb` | What do the river, snow and vegetation data look like before any modelling? | Completeness, summary statistics, distributions, time plots, smoothing, STL, ADF/KPSS stationarity (levels and differences), ACF/PACF, ARMA identification, agreement between snow stations, correlations in levels and differences |
| `12_snow_river.ipynb` | Have snowmelt and the river's spring peak moved earlier? Does the snowpack set the river's timing? **Has the river's seasonal pattern changed** compared with what a model fitted on 1911–1979 expects? **Can late-summer water be forecast in May?** How volatile is the river, and how extreme was the June 2022 flood? | Water-year features (centre of timing, peak date, 7-day low flow), Mann–Kendall with Hamed–Rao correction and Sen's slope, STL, VAR Granger causality (snow → river), degree-day snowmelt ODE, SARIMA chosen by BIC among models with white-noise residuals, rolling-origin evaluation, **long-horizon counterfactual SARIMA forecast** (fit 1911–1979, compare 1980–2026 month by month with binomial tests), **SARIMAX with the 1 May snowpack** (end-of-April forecasts of July–September flow, 1985–2026, scored against SARIMA and climatology), AR/OU half-life, ARCH LM, GARCH/EGARCH, GEV and Gumbel return periods |
| `11_vegetation_riverside.ipynb` | Did riverside vegetation get greener than slopes after 1995? Do streamside and hillside greenness track summer water, elk or bison? **Does an early spring (earlier river centre of timing) leave the plants less green?** **Does the May forecast of summer water anticipate greenness?** Does spring green-up follow snowmelt? What did the 2022 flood do? | Riverside − slope paired NDVI difference, sensor-era check, intervention regression (step + ramp at 1995, HAC errors), Bayesian-information break search, STL, first-difference pooled regressions (streamside, hillside and the gap) on low flow, elk, bison and centre of timing with year-clustered errors, per-stream levels models with trend and AR(1) errors as the white-residual check, Granger causality (pairwise and four-variable VAR), double-logistic green-up fits |

**Run order: 07 → 12 → 11.** Notebook 07 is exploratory and writes nothing the others need; notebook 12 writes `data/processed/river_annual_features.csv` and `data/processed/summer_flow_forecasts.csv` (the end-of-April forecasts of July–September flow), which notebook 11 reads.

Every regression and time-series model (intervention, water vs elk, spring timing, snow → river, VAR, SARIMA, SARIMAX, degree-day, GARCH) has a **residual check**: Ljung–Box for autocorrelation and ARCH LM for changing variance (Portmanteau for VARs), with the results tabled in `reports/tables/` and fixes applied where a model failed.

## Why the SARIMA model is there

The SARIMA model of monthly flow answers two questions, both in notebook 12, section 5:

1. **Has the river's seasonal pattern changed?** A model fitted only on water years 1911–1979 forecasts what 1980–2026 would look like if nothing had changed. Since 2000, April–May flow is about 30% above that forecast and July–September 20–26% below it (binomial tests p < 0.01); a fit on 1911–1949 gives the same direction.
2. **Can late-summer water be forecast in May?** Adding the 1 May snowpack (SARIMAX) cuts the error of end-of-April forecasts of July–September flow from about 42% (SARIMA) and 44% (climatology) to 25%, with correlation 0.67. Notebook 11 then shows that this May forecast anticipates summer greenness on both streamside and hillside plots.

Tables: `P2_sarima_counterfactual.csv`, `P2_sarimax_identification.csv`, `P2_summer_flow_forecast_scores.csv`, `P2_may_forecast_vs_greenness*.csv`. Figures: `P2_14_sarima_counterfactual.png`, `P2_15_summer_flow_forecasts.png`.

## Folder layout

```text
02_vegetation_snow_river/
├── data/
│   ├── raw/
│   │   ├── snotel_northeast_entrance.csv, snotel_canyon.csv, snotel_parker_peak.csv   daily SNOTEL (NRCS)
│   │   ├── usgs_06191500_daily_flow.txt        daily flow, Yellowstone River at Corwin Springs (USGS)
│   │   ├── ndvi_lamar_sodabutte.csv            Landsat NDVI, Lamar / Soda Butte riverside and slope polygons (Climate Engine)
│   │   └── ndvi_blacktail.csv                  Landsat NDVI, Blacktail riverside and slope polygons (Climate Engine)
│   └── processed/
│       ├── winter_severity_index.csv           one row per winter (used by Part 1)
│       ├── monthly_temperature.csv             monthly mean air temperature (used by Part 3)
│       ├── river_annual_features.csv           one row per water year (written by notebook 12)
│       ├── summer_flow_forecasts.csv           May forecasts of July–Sep flow, 1985–2026 (written by notebook 12)
│       └── ndvi_annual_peak_summer.csv
├── scripts/
│   └── build_severity_index.py   builds the two SNOTEL products above
├── notebooks/   07, 11, 12
└── reports/
    ├── figures/   P2_*.png
    └── tables/    P2_*.csv
```

## How to run

From this folder:

```sh
python scripts/build_severity_index.py data/raw/snotel_northeast_entrance.csv data/raw/snotel_canyon.csv data/raw/snotel_parker_peak.csv
```

(only needed if a SNOTEL file changes), then open `notebooks/` and run **07 → 12 → 11**. Notebook 11 also reads Part 1's corrected master file from `../01_yellowstone_elk_wolves/data/processed/`, so keep the folders side by side.

## Data notes

- Climate Engine exports leave partial rows without placeholders, so only rows with every polygon filled are used.
- NDVI spans Landsat 5, 7 and 8; notebook 11 checks for a jump when Landsat 8 starts (April 2013).
- The last months of USGS flow are provisional.
- This river drains a large area, so notebook 12 tests the water side of the debate, not a wolf effect on stream channels.
