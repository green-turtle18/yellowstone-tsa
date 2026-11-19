# Yellowstone elk and wolves: time-series analysis, 1984–2025

This project asks whether wolves, hunting, winter severity, bison and climate carry predictive information about northern Yellowstone elk growth. Annual observational models cannot establish a causal trophic cascade.

**Current status:** Person 1 questions Q1–Q7 and observation-error extension R are implemented and executed. Data corrections Q0 are partly complete. Final conclusions remain provisional pending the specific external inputs below.

- [Results and before/after comparison](reports/RESULTS.md)
- [Completion checklist, ready-to-send requests and handoffs](reports/HANDOFF.md)
- [Audited value/source changes](reports/tables/data_corrections.csv)
- [Yellowstone–Isle Royale comparison, awaiting Person 4](reports/tables/person4_comparison.csv)
- [References and source decisions](reports/REFERENCES.md)

## Reproduce

From the repository root, with Python and `requirements.txt` dependencies installed:

```sh
python3 scripts/run_all.py
```

This rebuilds the canonical flagged dataset, runs all analyses, generates the results summary, creates notebooks 03–05, executes notebooks 01–05, and runs numerical checks. Failures stop the run. It uses a lightweight plain-Python notebook runner, so no Jupyter server is required. The runner captures printed output, final expressions and open Matplotlib figures; these notebooks do not use magics or shell cells. Jupyter can also open and execute them normally.

To run stages individually:

```sh
python3 scripts/build_master_dataset.py
python3 scripts/analysis.py
python3 scripts/summarize_results.py
python3 scripts/run_notebooks.py
python3 -m unittest discover -s tests -v
```

`reports/run_manifest.json` records runtime versions, random seed and dataset hash. Original data and notebook outputs before this revision are in `reports/baseline/`.

## Data and corrections

Raw CSVs are preserved. `scripts/build_master_dataset.py` builds the legacy intermediate, then calls `scripts/build_master_flagged.py`, which applies `data/corrections/verified_overrides.csv` and writes the **canonical** `data/processed/yellowstone_master_ts_flagged.csv`. The unflagged `yellowstone_master_ts_final.csv` is a legacy intermediate; use the flagged file for analysis.

Every core variable has source and imputation flags. `count_whole_herd` identifies audited whole-herd elk observations; `Elk_Count_coverage_unresolved` separately identifies unresolved survey geography. An observation can be non-imputed yet unsuitable for a whole-herd analysis. Date/method differences also remain among whole-herd observations.

| Input | Timing used | Known limitation |
| --- | --- | --- |
| Elk | Winter year t | Surveys vary from December of t−1 to April of t; changing detection and methods |
| Northern-range wolves | December t−1; change per 10 wolves | Early gaps; range of wolf packs differs from whole-herd elk geography |
| Northern bison | Summer t−1; log difference | Repeated summer surveys differ; 2023 last-survey vs narrative-average sensitivity |
| NDVI | Summer t−1 | Polygon, sensor and harmonisation metadata needed |
| Precipitation / PDSI | **Calendar year** t−1 | Headers say TerraClimate Jan–Dec; earlier README/brief descriptions were inconsistent |
| Harvest | Season ending t, divided by elk t−1 | Publication/season timing and hunting-area changes need confirmation |
| Winter severity | Winter ending t | Nov–Apr / water-year components may extend beyond the elk count |

Verified corrections include historical whole-herd counts tabulated in the 2019 survey report, 2016–2019 and 2022–2025 elk, 2014 northern wolves and 2023 northern bison. Exact sources and alternatives are in the correction log. 2020–2021 whole-herd counts, the 2024 cross-report discrepancy, historical count provenance and 2025 climate are not silently resolved. Prior-year alignment means the missing 2025 climate endpoint is not used to explain the 2025 elk target.

## Analyses

| Notebook | Contents |
| --- | --- |
| 01 | Flagged-series EDA, ADF/KPSS, ACF/PACF, 1995 intervention description, ARMA diagnostics |
| 02 | Updated legacy six-driver regression, both-direction Granger, robustness, shared conditional prediction pipeline, VAR |
| 03 | Q1–Q4 and Q6: seven-driver models including severity, multiple-testing adjustment, predefined forecasts, winter interaction, hunting comparison |
| 04 | Q5 and R: mean/trend break search, CUSUM, growth-state Kalman model and density-dependent measurement-error model |
| 05 | Q7: GBM first passage, bootstrap intervals, 10,000-path checks, Gompertz comparison and bootstrap LR |

All numerical tables are in `reports/tables/`; figures are in `reports/figures/`, including new figures numbered 11–17. Shared functions live in `scripts/analysis.py`. New notebooks end with a plain-English explanation and the current results report.

## Interpretation safeguards

- No full-sample feature selection for rolling predictions. Transformation choices, scaling and station baselines are learned within each training window.
- No future interpolation of training outcomes. Only adjacent observed elk transitions enter training; exogenous gaps use past-only carries. Forecast models are compared on identical eligible years.
- Full-model evaluation is **conditional retrospective prediction**, not a validated operational forecast. Predictor publication dates and exposure windows are not fully established.
- ADF/KPSS results and all tested coefficients are reported, not only significant outcomes. Seven single-driver screens use Bonferroni ×7.
- Real-only, verified-coverage, pre-2016, wolf-level, MA(2) and alternative-survey checks are exported. Calendar gaps are never compressed for dynamic-error models.
- The state-space implementation puts covariates in latent growth, as specified by the brief's equation. Missing outcomes remain NaN on an annual grid. Its uncertainty band conditions on fitted parameters.
- Break selection includes zero breaks. The exact L2 dynamic-programming search is not a formal Bai–Perron significance test.
- GBM continuous first passage is checked with Brownian bridges; annual-only crossings are reported separately. Gompertz simulations use annual monitoring. LR inference uses a parametric bootstrap under a random walk.
- Threshold outputs are survey-count scenarios, not true abundance or extinction estimates. No ecological mechanism follows from coefficient signs alone.

## Inputs needed from collaborators

The detailed [handoff](reports/HANDOFF.md) specifies owners, exact files to send, return schemas and message drafts. The remaining essentials are survey records/metadata, the original Climate Engine polygon and export settings, Eberhardt et al.'s annual wolf-kill estimates, and Person 4's Isle Royale results. No collaborator messages were sent automatically.
