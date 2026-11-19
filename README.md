# Yellowstone Trophic Cascade: A Time-Series Analysis (1984–2025)

## 📌 Project Overview
This project uses time-series methods to revisit one of the best-known debates in modern ecology: **the Yellowstone trophic cascade.**

The classic narrative holds that reintroducing gray wolves to Yellowstone National Park in 1995 triggered a "top-down" cascade: wolves reduced the large Northern Yellowstone elk herd, which eased browsing pressure and let willows and aspens recover.

Many ecologists argue this is an oversimplification. They point to "bottom-up" and competing factors — drought, harsh winters, human hunting outside the park, and forage competition from a fast-growing bison herd — as major drivers of the elk decline.

Using the **Box–Jenkins methodology with exogenous regressors (ARIMAX)** on 42 years of annual data (1984–2025), we test **which factors carry predictive information for northern Yellowstone elk counts** — predator pressure (wolves), climate (precipitation, drought), vegetation (NDVI) or competition (bison) — and whether the evidence is *consistent with* a wolf-driven cascade.

> **Scope note.** Time-series models can show whether a variable helps *predict* elk counts beyond what the elk's own history already explains (Granger causality, ARIMAX). They cannot by themselves prove *causation*. With 42 annual observations, results are indicative, and we report them with that caveat.

---

## ❓ Research Questions
1. Is there a structural change in northern Yellowstone elk counts around the 1995 wolf reintroduction?
2. Do wolf numbers carry predictive information for elk counts beyond the elk's own past and climate?
3. How do wolves compare with bison, drought and precipitation as predictors of elk counts?
4. Does summer vegetation greenness (NDVI) change in a way consistent with reduced elk browsing?

---

## 📊 Datasets & Sources
All series are annual and restricted to the **Northern Range** of Yellowstone (except where noted) for spatial consistency.

| Variable | Role | Span | Source |
|---|---|---|---|
| **Elk count** | Target ($Y_t$) | 1984–2025 | Northern Yellowstone Cooperative Wildlife Working Group winter counts, as compiled in MacNulty et al. (2016) (1984–2015); Montana FWP Hunting District 313 counts (2016–2025) |
| **Wolves (northern range)** | Exogenous ($X_1$) | 1995–2025 | NPS Yellowstone Wolf Project annual reports. Zero before 1995 (pre-reintroduction). Park-wide totals kept as an alternative series. |
| **Summer NDVI** | Exogenous ($X_2$) | 1984–2025 | Climate Engine (Landsat), June–August mean |
| **Annual precipitation** | Exogenous ($X_3$) | 1984–2025 | TerraClimate via Climate Engine, water year (Oct–Sep) |
| **Palmer Drought Severity Index** | Exogenous ($X_4$) | 1984–2025 | TerraClimate via Climate Engine, water year (Oct–Sep) |
| **Bison (northern herd)** | Exogenous ($X_5$) | 1984–2025 | NPS *Yellowstone Bison Population Status Report* (Oct 2023) for 1984–2022; recent news and conservation estimates for 2024–2025 |

### Data quality and imputation
Every value in the processed dataset carries a `*_source` column recording how it was obtained (`count`, `count_hd313`, `interpolated`, `backfilled`, `carried_forward`, `estimate`, `structural_zero`) and a 0/1 `*_imputed` flag. Built by `scripts/build_master_dataset.py`.

| Variable | Real values | Filled values |
|---|---|---|
| Elk | 32 | 10 (6 interpolated, 2 backfilled, 2 carried forward) |
| Wolves (northern range) | 25 + 11 structural zeros | 6 interpolated (1996–2000, 2014) |
| Bison | 40 | 2 (2023 carried forward, 2025 estimate) |
| NDVI | 42 | 0 |
| Precipitation, PDSI | 41 | 1 each (2025 carried forward, pending re-download) |

**Known issues to resolve before modelling**
- [ ] **Elk splice at 2016.** Confirm whether MT FWP Hunting District 313 counts cover the whole northern herd (inside and outside the park) like the 1984–2015 working-group counts. If not, replace 2016–2025 with whole-herd counts.
- [ ] **Elk 1998 = 1999 (11,748).** Verify against MacNulty et al. (2016).
- [ ] **Bison 2023.** Verify against the NPS bison report.
- [ ] **Precipitation and PDSI 2025.** Re-download water year 2025 from TerraClimate.
- [ ] **NDVI sensor changes.** A 1984–2025 Landsat series spans Landsat 5, 7 and 8; check for artificial jumps at sensor transitions.

Imputed values are excluded when scoring forecast accuracy, and key models are re-fit without them as a robustness check.

---

## 🗂️ Repository Structure

```text
├── data/
│   ├── raw/                  # Original, unmodified source files (CSVs, PDFs). Never edited by hand.
│   └── processed/            # Built datasets, e.g. yellowstone_master_ts_flagged.csv
├── notebooks/                # Jupyter notebooks: EDA, stationarity, Granger causality, ARIMAX
├── reports/
│   └── figures/              # Generated plots (ACF/PACF, residual diagnostics, forecasts)
├── scripts/                  # Data-building scripts (build_master_dataset.py)
├── README.md
├── requirements.txt
└── .gitignore
```

---

## ⚙️ Methodology & Project Phases

### Phase 0: Data Preparation
- [x] Assemble master annual dataset (1984–2025).
- [x] Add `*_source` and `*_imputed` columns for every variable.
- [ ] Resolve the known issues listed above.

### Phase 1: Exploratory Data Analysis & Stationarity
- [x] Initial ADF tests and log-differencing of elk counts ($d=1$) on the v1 dataset.
- [ ] Re-run on the flagged dataset: plots of all series with imputed points marked.
- [ ] ADF (and KPSS as a cross-check) on each series in levels and first differences.
- [ ] ACF and PACF of the differenced elk series to identify candidate AR and MA orders.
- [ ] Structural-break check at 1995 (Chow test or intervention dummy).

### Phase 2: Preliminary Regression & Granger Causality
- [x] Baseline trend regressions (linear, polynomial, splines) on the v1 dataset.
- [x] Pairwise Granger causality on the v1 dataset (bison flagged as a possible 1-year leading indicator).
- [ ] Re-run Granger tests on **stationary (differenced)** series of the flagged dataset.
- [ ] Test both directions (e.g. bison → elk and elk → bison).
- [ ] Report lag choice and p-values for every pair, not only significant ones.

### Phase 3: ARIMAX Modelling
- [ ] Fit a baseline ARIMA on elk counts (no exogenous variables).
- [ ] Build candidate ARIMAX models adding exogenous variables one at a time and in combination (wolves, bison, NDVI, precipitation, PDSI), with lags of 0–1 years.
- [ ] **Standardise** exogenous variables (z-scores) so coefficients are comparable.
- [ ] Rank candidates by AIC and BIC; prefer the simpler model when scores are close.
- [ ] Report coefficients with standard errors and confidence intervals.

### Phase 4: Diagnostic Checking & Evaluation
- [ ] Residual plot, residual ACF and QQ plot for each final model.
- [ ] Ljung–Box test on residuals (up to lag 10, given n = 42).
- [ ] **Rolling-origin evaluation:** refit each year from 2010 and forecast one year ahead; score with MAE and RMSE on real (non-imputed) counts only.
- [ ] Compare ARIMAX against the baseline ARIMA and a naive forecast (next year = this year).
- [ ] Robustness check: re-fit key models excluding imputed years.

### Phase 5: Exploratory Extension (optional)
- [ ] Shallow decision tree (max depth 2–3) on standardised exogenous variables, presented as exploratory only — n = 42 is too small for firm thresholds.

### Phase 6: Interpretation
- [ ] Answer each research question, stating what the evidence supports and what it cannot establish.
- [ ] Compare findings with the published debate (e.g. Ripple & Beschta; MacNulty et al.; Hobbs et al.).

---

## 📚 Key References
- MacNulty, D. R., et al. (2016). Elk counts compiled for the northern Yellowstone herd.
- Northern Yellowstone Cooperative Wildlife Working Group, annual winter elk counts.
- National Park Service, Yellowstone Wolf Project annual reports (1995–2025).
- National Park Service (2023). *Yellowstone Bison Population Status Report.*
- Abatzoglou, J. T., et al. (2018). TerraClimate, a high-resolution global dataset of monthly climate. *Scientific Data.*