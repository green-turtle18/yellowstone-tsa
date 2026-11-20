# Person 1: completion status and handoff

Prepared 19 November 2026. No messages have been sent to collaborators.

## What is implemented

| Brief item | Delivered | Remaining dependency |
| --- | --- | --- |
| Q0 data correction | Canonical builder, audited override CSV, value/source change log; verified whole-herd elk corrections including 2016–2019 and 2022–2025; northern wolves 2014; northern bison 2023 | Historical audit, 2020–2021 whole-herd counts, survey reconciliation, climate metadata |
| Notebooks 01–02 | Updated and executed on corrected flagged data; original outputs preserved; same-method before/after results | Rerun after outstanding data fixes |
| Q1 drivers | Every single driver, full model, CIs/p-values/n/years, stationarity, Bonferroni, diagnostics, common-sample IC, sensitivity checks | Final input certification |
| Q2 feedback | VAR(1), VAR(2) sensitivity, both Granger directions, lag criteria, 10-wolf impulse responses | Final input certification |
| Q3 predictions | Naive, drift, wolf-only, full conditional models; common-year MAE/RMSE/MAPE; fold-specific transforms and station baselines | Survey/publication dates needed for genuine real-time validation |
| Q4 winters | Separate pre/post slopes and centred interaction, diagnostics | Survey-date-compatible exposure window |
| Q5 breaks | Exact dynamic-programming L2 search for 0–3 breaks, BIC, trend-break RSS, CUSUM | No formal Bai–Perron confidence set claimed |
| Q6 hunting | Standardised wolf/harvest model, VIF, incremental and partial R² | Completed: Table 1 transcription and late-hunt reconciliation; age/coverage limitations documented |
| Q7 viability | GBM formula, parameter bootstrap, 10,000-path annual/bridge checks, Gompertz fit and simulation, bootstrap LR | Probabilities remain count-index scenarios, not true-population risk |
| R survey error | Growth-state Kalman model, missing annual observations, process/observation SDs, smoothed bands, density-dependent SARIMAX | Sightability or survey-error calibration for stronger inference |
| Person 4 comparison | Yellowstone column and explicit metric definitions in CSV | Person 4's Isle Royale column |

## 1. Data owner / person who assembled the ecological series

**Send:** `reports/tables/data_corrections.csv`, `data/corrections/verified_overrides.csv`, the corrected `data/processed/yellowstone_master_ts_flagged.csv`, and this checklist.

**Ask them to return:** one CSV with `winter_year, survey_date, total_whole_herd, inside_park, outside_park, survey_method, surveyed_area, source_url, page_or_table, quality_note`. Missing counts must remain missing, not copied from another year.

Priority items:

- **2020 and 2021:** confirm if a whole-herd survey exists. The repo's 2020 value is copied; 2021 is HD313 only. Do not replace with statewide district statistics.
- **2024 discrepancy:** the 2024 report explicitly states 5,597. The 2025 report says 7,226 is 24.5% higher than 2024, implying a different base. Obtain the underlying survey record; do not solve this by back-calculating a count. Current code uses the explicitly reported 5,597.
- **Method/date harmonisation:** 2016 fixed-wing trend count is 4,912, versus a later helicopter count of about 7,510. Winter 2023 fixed-wing count is 5,976 (16 December 2022), versus 6,651 in March 2023. Both alternatives are tested. Choose a consistent series with a documented policy, not whichever makes the wolf effect stronger.
- **1984–2003:** audit the original digitised/compiled counts, especially identical 1998/1999 values and years labelled interpolated despite numeric entries in raw CSV. The cited 2016 MacNulty paper is Yellowstone Science, not PLOS ONE. The 2019 survey table supplied exact replacements for 2004–2013 and 2015; its unreliable 2014 count was deliberately not promoted to a valid observation.
- **Bison:** current 2023 value is 3,616, the last listed 2023 summer survey, consistent with using the last 2022 survey (4,507). The same NPS report gives a narrative average of 3,819 that differs from Appendix A1; it is included as a sensitivity. Confirm one aggregation rule for all years.
- **Wolves:** 2014's 42 is now observed rather than interpolated. Check other early northern-range gaps and spatial alignment with whole-herd elk. Numerical equality to an interpolation does not make provenance interchangeable.

**Ready-to-send request:**

> Please review the attached correction log and return the survey metadata CSV above, prioritising 2020–2021 whole-herd counts and the 2024 discrepancy. Please identify missing/unreliable surveys explicitly and distinguish fixed-wing trend counts from helicopter classifications. We have implemented both 2016 and 2023 alternatives, but need a defensible consistent count/date policy before finalising the analysis.

## 2. Climate / GIS data owner

**Send:** `data/raw/precipitation_std_year.csv`, `data/raw/drought_std_year.csv`, `data/raw/Vegetation_summer_months.csv`, and the requirement below.

**Need back:** the Climate Engine saved query or polygon GeoJSON, TerraClimate dataset/version, units, spatial reducer, temporal reducer, date window, missing-pixel rules, and the same settings used for the original exports. The files say **TerraClimate, Jan–Dec at Polygon 1**. The brief's NOAA and water-year descriptions are inconsistent with those headers.

- Re-export 2025 using that same polygon and calendar-year convention. If the intended project convention is a water year, re-export the entire historical series consistently; do not splice a water-year endpoint onto calendar-year history.
- Provide NDVI sensor/collection, cloud mask, compositing and harmonisation settings. Annual aggregate values alone cannot establish that Landsat transitions are artificial or ecological.
- Provide survey dates before deciding whether winter severity should end at the count date. Current Nov–Apr / water-year components include information after some winter surveys.

The 2025 climate fill does **not** enter a 2025 target with lag-one climate; it matters for completing Q0 and later prediction years. No substitute geography was invented.

**Ready-to-send request:**

> Please send the original Climate Engine polygon/saved query and export settings for precipitation, PDSI and NDVI. The existing climate headers indicate Jan–Dec TerraClimate. Please provide the matching 2025 export and NDVI sensor/harmonisation metadata, so we can preserve a consistent historical series.

## 3. Q6 literature and removals — completed

The user supplied Eberhardt et al. (2007), DOI 10.2193/2005-770. Table 1 (printed p.598 / PDF p.5) supplies 1996–2004 total estimated wolf kills, the separately retained 0.26 adjustment, and hunting removals. All hunting values match the existing late-hunt column, not fall-plus-late totals; winter labels match all nine rows. No source-access request remains.

**Send:** `supplements/q6_removals/q6_completion_handoff.zip`. Main table: `reports/tables/q6_removals_comparison.csv`. The earlier `q6_removals_pending.csv` is a historical placeholder only; do not use it for current results. Remaining caveats: no annual confidence intervals supplied, estimated fall components in 1998–2004, and headcounts do not quantify age-specific demographic effects.

## 4. Person 4 — Isle Royale comparison

**Send:** `scripts/analysis.py`, `reports/tables/person4_comparison.csv`, `reports/tables/q1_robustness.csv`, `reports/tables/q2_lag_selection.csv`, `reports/tables/q3_scores.csv`, and `reports/run_manifest.json`.

**Ask back:** the filled Isle Royale column, source series/flags, years and sample sizes, model coefficients/CIs, both VAR(1) Granger p-values, drift and wolf-only MAE on identical eligible years, GBM log-drift and sample SD, and any deviations from the specification.

Shared specifications:

1. Annual target `log(prey_t)-log(prey_(t-1))`. Wolves regressor `(wolves_(t-1)-wolves_(t-2))/10`. ARIMA on growth with order (0,0,0), constant, Gaussian errors. Report the per-10-wolf effect and also standardised effect if absolute wolf scales differ greatly.
2. VAR uses **contemporary** annual growth and wolf changes, so its built-in lag creates the lead relationship. Prespecify lag 1 and report lag-2 sensitivity and AIC/BIC. Yellowstone post-reintroduction system starts 1997; use an ecologically defensible Isle Royale window, label it, and consider a matched-period sensitivity.
3. Rolling origin 2011–2025 where data permit. No full-sample feature selection/scaling. Exclude imputed target and previous prey count; retain calendar gaps. Train from observed adjacent prey transitions. Score drift and wolves-only on identical years. Report MAE gain as `100*(1-MAE_wolf/MAE_drift)`. Confirm predictor release dates; otherwise label retrospective.
4. GBM parameters from adjacent observed annual log changes: mean and SD with ddof=1. Never treat a multi-year gap as one annual change. Report selection sensitivity. Absolute thresholds 2,000/4,000 are Yellowstone-specific, not automatic Isle Royale thresholds.
5. Do not merge raw coefficients across mismatched prey geographies, count protocols or time windows without stating those differences.

**Ready-to-send request:**

> The Yellowstone side and reproducible model specifications are attached. Please run the matching Isle Royale wolf-only model, two-way VAR(1), matched-year rolling evaluation, and GBM calibration. Fill the Isle_Royale column, return n/years and provenance, and note any departures. Blank comparison cells are intentional pending your results.

## Finalisation after handoffs

Add verified records to `data/corrections/verified_overrides.csv`; update missing/source flags where necessary; rerun `python3 scripts/run_all.py`; review changed coefficients and forecast eligibility; then fill the comparison and write final conclusions. No need to request approval for routine reruns or code corrections. Optional decision-tree and Diebold–Mariano extensions are omitted: neither resolves the current data-quality limitations.
