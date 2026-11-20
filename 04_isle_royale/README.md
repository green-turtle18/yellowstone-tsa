# Person 4 — Isle Royale wolves and moose

The clean comparison for the Yellowstone project. Isle Royale has no hunting, no bison and almost no migration, so if wolves
matter for their prey, it should show here. The same time-series methods are run as on Yellowstone, followed by predator–prey
equations and a stochastic extinction simulation.

Everything in this folder was built from the Person 4 brief and does not depend on any other folder in the repo.

## Folder layout

```text
04_isle_royale/
├── data/
│   ├── raw/                     source files, never edited by hand
│   │   ├── isle_royale_project_1959_2019.csv   project counts (June 2019 file, via R package dsem)
│   │   ├── isle_royale_nps_1980_2026.csv       NPS counts (extends the series to 2026)
│   │   ├── isle_royale_climate_marss.csv       NE Minnesota climate 1959–2011 (R package MARSS)
│   │   └── isle_royale_kill_rates_TO_FILL.csv  kill rates + moose CIs from the annual reports (to fill)
│   └── processed/
│       └── isle_royale_annual.csv              master file: _source / _imputed / Period / Main_sample
├── scripts/
│   ├── build_isle_royale_annual.py   builds the master file from data/raw
│   └── tsa_spec.py                   shared model settings (Person 1 imports this for Yellowstone)
├── notebooks/
│   ├── 08_isle_royale_ts.ipynb          Q0–Q5: stationarity, ARIMAX, VAR/Granger, cointegration, forecasts, cycle
│   ├── 09_isle_royale_ode.ipynb         Q6: Lotka–Volterra, Rosenzweig–MacArthur, prey- vs ratio-dependent kill rates
│   └── 10_isle_royale_stochastic.ipynb  Q7: extinction simulation (10,000 runs from 1990)
├── reports/
│   ├── figures/   IR_*.png
│   └── tables/    IR_*.csv, IR_Q6_params.json, IR_comparison_column.csv
└── docs/
    └── model_settings.md   the settings, written out, plus the code Person 1 runs on Yellowstone
```

## How to run (Google Colab)

1. Put the whole `04_isle_royale` folder on Google Drive, or upload it to the Colab session.
2. In a Colab cell:
   ```python
   from google.colab import drive; drive.mount("/content/drive")
   %cd "/content/drive/MyDrive/<path>/04_isle_royale/notebooks"
   ```
   Then open and run each notebook from that folder. The notebooks find `data/`, `scripts/` and `reports/` from it.
3. Run in order: **08 → 09 → 10**. Notebook 10 reads `reports/tables/IR_Q6_params.json`, which 09 writes.
4. Rebuild the data only if a raw file changes: `!python ../scripts/build_isle_royale_annual.py`.

Colab already has numpy, pandas, scipy, statsmodels and matplotlib. Notebook 09's ODE fits take under a minute.

## Data decisions

| Decision | Why |
|---|---|
| Project series is primary for 1959–2019; NPS only for 2020+ | The project series covers all years from 1959 and is the one used in the literature |
| Moose disagree between sources before 2003 (median 9 %, up to 50 % in 1996–97) | The project series looks like the revised reconstruction; NPS kept the original aerial estimates. Q1 is re-run on NPS as a robustness check. Full list: `reports/tables/isle_royale_source_disagreements.csv` |
| 2021 and 2025 interpolated (no survey) | Flagged `_imputed = 1`; outside the main sample anyway |
| Main sample 1959–2015 | From the brief; 2016–2026 (near-extinction, reintroduction) treated separately |
| Period labels: parvo_crash 1980–82, near_extinction 2012–18, reintroduction 2019, post_reintroduction 2020+ | The 2018 winter count (2 wolves) came before the Sept 2018 translocations, so 2019 is the first count with released wolves |
| Climate only to 2011 | Models with climate use 1960–2011 |

## Still to do

- [ ] **Kill rates:** the annual reports show yearly kill rates only as a figure. Fill `data/raw/isle_royale_kill_rates_TO_FILL.csv`
      (moose per wolf per month), rerun the build script, and notebook 09 section 1 runs the direct prey- vs ratio-dependent test.
- [ ] **Comparison table:** Person 1 runs the code in `docs/model_settings.md` on Yellowstone and sends `YS_comparison_column.csv`.
- [ ] Confirm the references in the brief (year and journal) before citing.
