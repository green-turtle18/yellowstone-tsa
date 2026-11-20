# Part 2 · Vegetation, snow and river

The **bottom-up and water side** of the trophic-cascade debate. If wolves helped riverside willows by reducing elk browsing, the riverside should have greened relative to nearby slopes after 1995. If water limits willows instead, riverside greenness should track summer river flow more closely than elk numbers. Snowpack and river timing set that water, so they are analysed here too.

## Notebooks

| Notebook | Question | Methods |
|---|---|---|
| `12_snow_river.ipynb` | Have snowmelt and the river's spring peak moved earlier? Does the snowpack set the river's timing? Can monthly flow be forecast? How volatile is the river, and how extreme was the June 2022 flood? | Water-year features (centre of timing, peak date, 7-day low flow), Mann–Kendall with Hamed–Rao correction and Sen's slope, STL, degree-day snowmelt ODE, SARIMA with rolling-origin evaluation, AR/OU half-life, ARCH LM, GARCH/EGARCH, GEV and Gumbel return periods |
| `11_vegetation_riverside.ipynb` | Did riverside vegetation get greener than slopes after 1995? Does it track summer water or elk? Does spring green-up follow snowmelt? What did the 2022 flood do? | Riverside − slope paired NDVI difference, sensor-era check, intervention regression (step + ramp at 1995, HAC errors), Bayesian-information break search, STL, pooled regression on low flow, elk and bison, double-logistic green-up fits |

**Run 12 before 11**: notebook 12 writes `data/processed/river_annual_features.csv`, which notebook 11 reads.

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
│       └── ndvi_annual_peak_summer.csv
├── scripts/
│   └── build_severity_index.py   builds the two SNOTEL products above
├── notebooks/   11, 12
└── reports/
    ├── figures/   P2_*.png
    └── tables/    P2_*.csv
```

## How to run

From this folder:

```sh
python scripts/build_severity_index.py data/raw/snotel_northeast_entrance.csv data/raw/snotel_canyon.csv data/raw/snotel_parker_peak.csv
```

(only needed if a SNOTEL file changes), then open `notebooks/` and run **12 → 11**. Notebook 11 also reads Part 1's corrected master file from `../01_yellowstone_elk_wolves/data/processed/`, so keep the folders side by side.

## Data notes

- Climate Engine exports leave partial rows without placeholders, so only rows with every polygon filled are used.
- NDVI spans Landsat 5, 7 and 8; notebook 11 checks for a jump when Landsat 8 starts (April 2013).
- The last months of USGS flow are provisional.
- This river drains a large area, so notebook 12 tests the water side of the debate, not a wolf effect on stream channels.
