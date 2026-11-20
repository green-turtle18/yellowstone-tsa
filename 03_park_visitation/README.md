# Part 3 · Park visitation

**Status:** complete. Did bringing wolves back change how people use Yellowstone, and how do
visitors respond to climate and shocks? Monthly recreation visits 1979–2025 (NPS IRMA), modelled
with SARIMA, exponential smoothing (ETS / Holt–Winters), intervention analysis and VAR.

```
03_park_visitation/
├── data/raw/            IRMA exports as downloaded, IRMA notes (PDF), wolf counts (from Part 1)
├── data/processed/      clean monthly visits, entrance traffic, temperature + winter severity (from Part 2)
├── scripts/             build_visitation_data.py, q4_rolling_forecasts.py
├── notebooks/           13_visitation_eda_sarima.ipynb, 14_visitation_interventions.ipynb
└── reports/             part3_report.md, ai_usage_report.md, figures/, tables/
```

The written report is [`reports/part3_report.md`](reports/part3_report.md); the AI usage declaration
required by the course is [`reports/ai_usage_report.md`](reports/ai_usage_report.md).

## How to run

Run everything from this folder (`03_park_visitation/`).

1. `python scripts/build_visitation_data.py` — builds `data/processed/yell_visits_monthly.csv` and
   `yell_traffic_by_entrance.csv` from the raw IRMA exports, with checks.
2. Run `notebooks/13_visitation_eda_sarima.ipynb` — writes the SARIMA and ETS specifications.
3. `python scripts/q4_rolling_forecasts.py` — rolling-origin forecasts, 5 models × 192 origins
   (~6 min). Kept outside the notebook because it is slow.
4. Run notebook 13 again (it loads the forecasts from step 3), then
   `notebooks/14_visitation_interventions.ipynb`.

Packages: `pip install -r requirements.txt` (pandas, numpy, scipy, statsmodels, matplotlib, pymannkendall, ruptures, openpyxl).

## Data

| File | Source | Used for |
|---|---|---|
| `data/raw/yell_visits_monthly_irma.xlsx` (+ `.csv` copy) | IRMA → Park Reports → YELL → Recreation Visitors By Month | all questions |
| `data/raw/yell_visits_annual_irma.xlsx` | IRMA → Annual Park Recreation Visits | yearly cross-check (all years match exactly) |
| `data/raw/yell_traffic_counts_by_entrance_irma.xlsx` | IRMA → Traffic Counts by Location | Q1, Q5 |
| `data/raw/yell_monthly_visitation_comments.pdf` | IRMA → Monthly Visitation Comments | `Note` column (closures, shutdowns, counter changes) |
| `data/raw/yell_count_procedure_changes.pdf` | IRMA → Park Visitor Use and Count Procedure Changes | 1993 and 2013 counting-method changes |
| `data/raw/yellowstone_wolves_1995_2025.csv` | copy from Part 1 | Q1 (wolf numbers) |
| `data/processed/monthly_temperature.csv` | copy from Part 2 (3 SNOTEL stations, from 1984) | Q2 |
| `data/processed/winter_severity_index.csv` | copy from Part 2 | Q1 (control) |

The Part 1 and Part 2 files are **copies**, so this folder runs on its own. If those parts
update their outputs, copy the new versions here.

Two data facts shape the analysis:
* NPS switched from manual counts to **traffic-counter estimates in 1993**, two years before the
  wolf release. Every before/after-1995 comparison controls for it.
* The entrance traffic file counts **cars only** and starts in **1993**. In winter only the North
  gate has cars (West/South/East are snowmobile-only), so Q5 compares North with Highway 191
  instead of the West gate.

## Results

| Q | Question | Answer |
|---|---|---|
| 0 | What does the series look like? | 2.0M → 4.8M visits a year; July ≈ 66× November. Base model SARIMA(0,1,2)(1,1,1)₁₂ with shock dummies (fires −35%, COVID −65%, flood −35%, shutdowns −36%). |
| 1 | Did wolves bring tourists? | **Not park-wide.** Winter visits show no rise after 1995 (step −15%, p = 0.54; monthly model rules out more than +1.5%); they follow snowmobile rules (−30% after 2004). North-gate winter cars (the road to Lamar Valley) doubled after 1996 and move with the wolf count (elasticity ≈ 0.3, p = 0.02–0.27): suggestive, not proof. Full paragraph: `reports/tables/q1_answer_paragraph.txt`. |
| 2 | Is climate shifting when people visit? | The season is **spreading**: spring/autumn share 24% → 38% (p < 0.001), centroid unchanged. +3% visits per °C overall, +5–9% in shoulder months, −2.6% in July. The effect is same-month only (no Granger causality at any lag). |
| 3 | How fast does tourism recover? | 3–4 months for all three shocks. Visits lost in the first year: fires 156–702k, COVID 468–561k, flood 1.1–2.5M (ranges = SARIMA vs ETS counterfactuals). Only COVID was followed by a rebound above normal. |
| 4 | How well can visits be forecast? | No model beats "same month last year" significantly. SARIMA with d = 0 + drift is the best single model one month ahead; equal-weight combinations are best overall (MASE 1.14 vs 1.28 seasonal naive, n.s.). The original d = 1 SARIMA overshoots because it extrapolates recent growth (shown with ψ-weights). |
| 5 | North gate vs other entrances | No step at the first wolf winter; the doubling starts in 1997 (date chosen after seeing the data). Blind break tests: 1999 and 2009. Cannot prove a wolf effect with three pre-wolf winters. |

Syllabus extensions in notebook 13: AR/MA root checks, ARCH-LM test, over-differencing
check (d = 0), ψ-weights and eventual forecast function, forecast combination and encompassing
tests. In notebook 14: Granger causality / VAR with residual white-noise checks and impulse response, ETS counterfactuals.

## Main figures

`q0_stl.png`, `q1_winter_vs_summer_1995.png`, `q1_north_gate_vs_wolves.png`,
`q2_shoulder_share.png`, `q2_temperature_by_month.png`, `q3_counterfactuals_sarima_vs_ets.png`,
`q4_rolling_forecasts.png`, `q4b_combinations.png`, `q0_psi_weights_forecast_function.png`
(all in `reports/figures/`).
