# Model settings for the Yellowstone vs Isle Royale comparison

**Owner:** Person 4 · **Code:** `04_isle_royale/scripts/tsa_spec.py` (version printed as `SPEC_VERSION`, currently 1.3)

The comparison table only works if both systems are analysed in exactly the same way. Read this
document for the rules, but don't reimplement them: **import `tsa_spec.py` and call its functions**
on the Yellowstone series. If this document and the code ever disagree, the code wins. Tell
Person 4 before changing anything in it.

---

## 1. How to run it on Yellowstone (Person 1)

```python
import sys
from pathlib import Path
import pandas as pd

P4 = Path("<repo root>") / "04_isle_royale"
sys.path.insert(0, str(P4 / "scripts"))
import tsa_spec as spec
print(spec.SPEC_VERSION)                       # must match the version Person 4 used

# prey, wolves: pandas Series of winter counts, indexed by integer year, same index
prey   = ...   # northern Yellowstone elk counts
wolves = ...   # northern-range wolves (0 before 1995 is a real zero, not missing)
real   = ...   # boolean Series by year: True where the elk count is a real count (not imputed)
MAIN   = list(range(prey.index.min(), prey.index.max() + 1))

# Q0
import numpy as np
st = pd.DataFrame([spec.stationarity(np.log(prey.astype(float)), "log prey (level)"),
                   spec.stationarity(spec.growth(prey), "prey growth"),
                   spec.stationarity(np.log(wolves[wolves > 0].astype(float)), "log wolves (level)"),
                   spec.stationarity(spec.growth(wolves[wolves > 0]), "wolf growth")])
table, arma_fits, ORDER = spec.identify_arma(spec.growth(prey))

# Q1
fits, effects, diagnostics = spec.run_core_models(prey, wolves, order=(ORDER[0], 0, ORDER[1]))

# Q2
var_out = spec.fit_var(spec.var_data(prey, wolves))

# Q3
coint = spec.cointegration(prey, wolves)

# Q4: test window = the last 26 years of the main sample, real counts only
test = MAIN[-spec.FORECAST_TEST_YEARS:]
fc = spec.rolling_forecasts(prey, wolves, test, score_mask=real)
scores = spec.forecast_scores(fc)

# Comparison-table column
col = spec.comparison_row("Yellowstone", prey, wolves, MAIN, effects, var_out, scores)
pd.Series(col, name="Yellowstone").to_csv("YS_comparison_column.csv")
```

Send Person 4 the file `YS_comparison_column.csv`. Isle Royale's column is
`04_isle_royale/reports/tables/IR_comparison_column.csv`, made with the same function.

---

## 2. Data conventions

| Item | Rule |
|---|---|
| Unit of time | One row per winter count, labelled by the year it was flown |
| Prey growth | y_t = log N_t − log N_(t−1): the change over the 12 months before count *t* |
| Time alignment | Every regressor in row *t* is what was present **during** those 12 months, i.e. the value counted at *t−1*. Both systems are counted in winter, so this is the same alignment for both |
| Imputed values | Kept in the data with a `_imputed = 1` flag; **not scored** as forecast targets (`score_mask`) |
| Wolves = 0 | Real zeros (Yellowstone before 1995). Kept in the ARIMAX (wolves in levels). Log-based steps (VAR, cointegration) automatically use only years with wolves > 0 in both years |

---

## 3. The rules, question by question

### Q0 — Stationarity and ARMA identification
| Setting | Value | Why |
|---|---|---|
| ADF | `adfuller(x, maxlag=L, autolag=None)` for L = 0, 1, 2 | Fixed lags, so the lag choice is not data-mined |
| ADF verdict | Rejects the unit root if p < 0.05 at **≥ 2 of the 3** lags | One lag order can't decide the result alone |
| KPSS | `kpss(x, regression="c", nlags="auto")`, rejects stationarity if p < 0.05 | Opposite null to ADF |
| Combined verdict | ADF rejects + KPSS doesn't → stationary; reverse → non-stationary; otherwise inconclusive | |
| Series tested | log levels and growth rates of prey and wolves | |
| ARMA candidates | white noise, AR(1), AR(2), MA(1), each with a constant, fitted to prey growth | The brief's four candidates |
| Admissible | All AR/MA terms significant at 5 % **and** Ljung–Box p > 0.05 at lag 10 | lag 10 ≈ min(10, n/5) for ~50 annual points |
| Chosen | Admissible model with the **lowest BIC** (white noise if none is admissible) | BIC penalises extra terms; suits small samples |

### Q1 — ARIMAX on prey growth
Model: y_t = μ + β_W·(W_(t−1)/10) + β_D·(log N_(t−1) − mean) + ε_t, errors = the ARMA order chosen in Q0.

| Model name | Regressors |
|---|---|
| `drift` | none |
| `wolves` | W_(t−1)/10 |
| `density` | log N_(t−1), centred |
| `wolves + density` | both |

- All four are fitted on the **same rows**, with `ARIMA(..., trend="c")`.
- Report β × 100 as **% change in prey growth per +10 wolves**, with the 95 % CI. Also report it per +1 SD of the system's own wolf series. The two parks have very different wolf numbers, so the per-SD figure is the fairer comparison.
- Diagnostics: Ljung–Box at lags 5 and 10, ARCH test with 2 lags.
- Climate is **system-specific** and not part of the comparison table. Each person adds their own climate variables in a separate model.

### Q2 — VAR and Granger
| Setting | Value |
|---|---|
| Variables | [Δlog prey, Δlog wolves] |
| Lag for the comparison table | **1** (Yellowstone's wolf series is only ~30 years) |
| Lag also reported | BIC choice from `select_order(maxlags=3)`, minimum 1 |
| Granger test | `res.test_causality(caused, [causing], kind="f")`, both directions |
| Impulse responses | 10 years, unit (non-orthogonalised) shocks |

### Q3 — Cointegration
Engle–Granger in both orderings (`coint`) and Johansen with `det_order=0, k_ar_diff=1` on [log prey, log wolves].
Rank = number of leading trace statistics above the 5 % critical value. Fit a VECM only if the rank ≥ 1.

### Q4 — Rolling-origin forecasts
| Setting | Value |
|---|---|
| Window | Expanding: for each test year *t*, fit on everything up to *t−1* |
| Test years | The **last 26 years** of each system's main sample (Isle Royale: 1990–2015) |
| Forecast | Count at *t* = N_(t−1) · exp(predicted growth) |
| Models | naive (no change), drift (mean growth), ARIMAX `wolves`, ARIMAX `wolves + density`, VAR(1) |
| VAR | Scored only when ≥ 15 training rows exist; its gain is measured against drift **on the same years** |
| Scores | MAE (animals), MAPE (%), and the % gain in each over drift |
| Targets scored | Real counts only |

---

## 4. The comparison table

Each system contributes one column from `spec.comparison_row(...)`:

| Row | How it's computed |
|---|---|
| years (prey growth) | rows used in Q1 |
| wolf effect alone, % per +10 wolves [95% CI], p | `wolves` model |
| wolf effect with density, % per +10 wolves [95% CI], p | `wolves + density` model |
| wolf effect with density, % per +1 SD of wolves | same, rescaled by the SD of W |
| Granger p, wolves → prey | VAR(1) |
| Granger p, prey → wolves | VAR(1) |
| forecast MAPE gain over drift, ARIMAX wolves (pre-chosen) | Q4 |
| drift of log prey (%/yr) | mean of prey growth |
| volatility of log prey (%) | SD of prey growth |

Merge the two columns:

```python
ir = pd.read_csv("04_isle_royale/reports/tables/IR_comparison_column.csv", index_col=0)
ys = pd.read_csv("YS_comparison_column.csv", index_col=0)
table = ys.join(ir, how="outer")
```

---

## 5. Known differences to state in the write-up
- **Isle Royale moose 1959–2002** come from the project's reconstructed series and are smoother than raw aerial
  counts. This can make Isle Royale growth look less volatile than a raw survey would. The NPS series is used as a robustness check.
- **Sample lengths differ** (Isle Royale 56 growth rates; Yellowstone fewer, and wolves only from 1995). With
  fewer years, Yellowstone p-values are less likely to be significant even for the same true effect.
- **Wolf density differs** (Isle Royale ≈ 544 km²). Compare the per-SD effect, not only the per-10-wolves one.
