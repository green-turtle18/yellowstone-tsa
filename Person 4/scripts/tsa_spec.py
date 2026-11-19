"""Shared time-series settings for the Yellowstone vs Isle Royale comparison.

Every Q0-Q4 result that goes into the comparison table must be produced with the
functions in this file, so both systems are run identically. The written version
of these rules is docs/model_settings.md; if the two ever disagree, this file wins.

Usage from a notebook in notebooks/:
    import sys; sys.path.insert(0, str(ROOT / "scripts"))
    import tsa_spec as spec

Owner: Person 4. Written from the Person 4 brief, independently of the existing
Yellowstone notebooks. Version: see SPEC_VERSION. Change the version string whenever a
rule changes, and print it at the top of every notebook that uses the module.
"""
from __future__ import annotations

import functools
import warnings

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.tsa.api import VAR
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller, coint, kpss
from statsmodels.tsa.vector_ar.vecm import coint_johansen

SPEC_VERSION = "1.3 (2026-11-18)"


def _quiet(fn):
    """Silence statsmodels convergence/interpolation/index warnings inside spec functions."""
    @functools.wraps(fn)
    def wrapper(*a, **k):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return fn(*a, **k)
    return wrapper

ALPHA = 0.05
ADF_LAGS = (0, 1, 2)          # ADF at fixed lag orders, no autolag
ADF_MIN_REJECTIONS = 2         # stationary by ADF if it rejects at >= 2 of the 3
ARMA_CANDIDATES = [(0, 0), (1, 0), (2, 0), (0, 1)]   # the four candidates named in the brief
LJUNG_BOX_LAG_ID = 10          # min(10, n/5) for annual series of ~50 years
LJUNG_BOX_LAGS_DIAG = (5, 10)  # lags reported in diagnostics
ARCH_LAGS = 2
VAR_MAXLAGS = 3
VAR_TABLE_LAG = 1              # lag used for the comparison table (short Yellowstone sample)
IRF_HORIZON = 10
JOHANSEN_DET_ORDER = 0
JOHANSEN_K_AR_DIFF = 1
FORECAST_TEST_YEARS = 26       # last 26 years of each system's main sample
VAR_MIN_TRAIN = 15             # VAR forecasts scored only when >= 15 training rows exist
WOLF_UNIT = 10                 # wolf coefficients reported per 10 wolves (and per 1 SD)


# ---------------------------------------------------------------------------
# Q0  Stationarity and ARMA identification
# ---------------------------------------------------------------------------
@_quiet
def stationarity(x, name: str | None = None) -> dict:
    """ADF at fixed lags 0, 1, 2 (counts as rejecting the unit root if >= 2 of the 3 reject
    at 5 %), read together with KPSS (regression='c', nlags='auto'). The two tests have opposite
    nulls: ADF rejects + KPSS does not -> stationary; the reverse -> non-stationary; otherwise
    inconclusive. A majority over three lag orders keeps one lag choice from deciding the verdict."""
    x = pd.Series(x).dropna()
    res = {"series": name, "n": len(x)}
    ps = []
    for lag in ADF_LAGS:
        r = adfuller(x, maxlag=lag, autolag=None)
        res[f"ADF_stat_lag{lag}"] = r[0]
        res[f"p_lag{lag}"] = r[1]
        ps.append(r[1])
    adf_rejects = sum(p < ALPHA for p in ps) >= ADF_MIN_REJECTIONS
    k = kpss(x, regression="c", nlags="auto")
    res["KPSS_stat"], res["KPSS_p"] = k[0], k[1]
    kpss_rejects = k[1] < ALPHA
    res["ADF says"] = "stationary" if adf_rejects else "unit root"
    res["KPSS says"] = "non-stationary" if kpss_rejects else "stationary"
    res["conclusion"] = ("stationary" if adf_rejects and not kpss_rejects else
                         "non-stationary" if not adf_rejects and kpss_rejects else "inconclusive")
    return res


@_quiet
def identify_arma(y: pd.Series):
    """Fit white noise, AR(1), AR(2), MA(1) (each with a constant) to a stationary series.
    Admissible = all AR/MA terms significant at 5 % and residuals pass Ljung-Box at lag 10.
    Chosen = admissible model with the lowest BIC (BIC penalises extra terms more than AIC,
    which suits ~50 observations). Returns (table, fits, chosen_order)."""
    y = y.dropna()
    rows, fits = [], {}
    for p, q in ARMA_CANDIDATES:
        m = ARIMA(y, order=(p, 0, q), trend="c").fit()
        fits[(p, q)] = m
        terms = [k for k in m.params.index if k.startswith(("ar.", "ma."))]
        lb = acorr_ljungbox(m.resid, lags=[LJUNG_BOX_LAG_ID]).lb_pvalue.iloc[0]
        rows.append({
            "model": "white noise" if (p, q) == (0, 0) else f"ARMA({p},{q})",
            "coefficients": ", ".join(f"{k}={m.params[k]:.3f} (p={m.pvalues[k]:.2f})" for k in terms) or "—",
            "all terms significant": all(m.pvalues[k] < ALPHA for k in terms) if terms else True,
            "residual variance": m.params["sigma2"],
            f"LjungBox_p(lag{LJUNG_BOX_LAG_ID})": lb,
            "white-noise residuals": lb > ALPHA,
            "AIC": m.aic, "BIC": m.bic,
        })
    table = pd.DataFrame(rows)
    ok = [i for i, r in enumerate(rows) if r["all terms significant"] and r["white-noise residuals"]]
    chosen = ARMA_CANDIDATES[min(ok, key=lambda i: rows[i]["BIC"])] if ok else (0, 0)
    return table, fits, chosen


# ---------------------------------------------------------------------------
# Q1  ARIMAX on prey growth
# ---------------------------------------------------------------------------
def growth(n: pd.Series) -> pd.Series:
    """y_t = log N_t - log N_(t-1): change over the 12 months before count t."""
    return np.log(n.astype(float)).diff()


def core_regressors(prey: pd.Series, wolves: pd.Series) -> pd.DataFrame:
    """Row t holds what was present during the 12 months before count t
    (both systems count in winter, so wolves counted at t-1 are the predators
    present through the interval).
        wolves      W_(t-1) / 10                 predation pressure, per 10 wolves
        wolves_sd   W_(t-1) standardised         per 1 SD of the system's own wolf series
        density     log N_(t-1), centred          density dependence (Gompertz term)
    """
    w1 = wolves.astype(float).shift(1)
    ln1 = np.log(prey.astype(float)).shift(1)
    return pd.DataFrame({
        "wolves": w1 / WOLF_UNIT,
        "wolves_sd": (w1 - w1.mean()) / w1.std(),
        "density": ln1 - ln1.mean(),
    }, index=prey.index)


CORE_MODELS = {
    "drift": [],
    "wolves": ["wolves"],
    "density": ["density"],
    "wolves + density": ["wolves", "density"],
}


@_quiet
def fit_arimax(y: pd.Series, X: pd.DataFrame | None = None, order=(0, 0, 0)):
    """ARIMA(y, exog=X, order, trend='c') on the rows where y and X are all present."""
    y = y.rename(y.name or "y")
    d = pd.concat([y, X], axis=1).dropna() if X is not None and X.shape[1] else y.dropna().to_frame()
    exog = d.drop(columns=y.name) if X is not None and X.shape[1] else None
    return ARIMA(d[y.name], exog=exog, order=order, trend="c").fit(), d


def diagnose(res) -> dict:
    r = res.resid
    lb = acorr_ljungbox(r, lags=list(LJUNG_BOX_LAGS_DIAG)).lb_pvalue.values
    return {f"LjungBox_p_lag{l}": p for l, p in zip(LJUNG_BOX_LAGS_DIAG, lb)} | {
        "ARCH_p": het_arch(r, nlags=ARCH_LAGS)[1]}


def effect_table(fits: dict) -> pd.DataFrame:
    """Coefficient table: beta, 95 % CI, and beta x 100 as % change in prey per year."""
    rows = []
    for name, res in fits.items():
        ci = res.conf_int()
        for k in res.params.index:
            if k in ("const", "sigma2") or k.startswith(("ar.", "ma.")):
                continue
            rows.append({"model": name, "term": k, "beta": res.params[k], "p": res.pvalues[k],
                         "pct_per_unit": 100 * res.params[k],
                         "pct_CI_low": 100 * ci.loc[k, 0], "pct_CI_high": 100 * ci.loc[k, 1],
                         "n": int(res.nobs), "AIC": res.aic, "BIC": res.bic})
    return pd.DataFrame(rows)


@_quiet
def run_core_models(prey, wolves, years=None, order=(0, 0, 0)):
    """Fit CORE_MODELS on a common set of rows. Returns (fits, effects, diagnostics)."""
    y = growth(prey).rename("y")
    X = core_regressors(prey, wolves)
    d = pd.concat([y, X], axis=1).dropna()
    if years is not None:
        d = d.loc[d.index.isin(years)]
    fits = {name: fit_arimax(d["y"], d[cols] if cols else None, order=order)[0]
            for name, cols in CORE_MODELS.items()}
    diag = pd.DataFrame({k: diagnose(v) for k, v in fits.items()}).T
    return fits, effect_table(fits), diag


# ---------------------------------------------------------------------------
# Q2  VAR, Granger, impulse responses
# ---------------------------------------------------------------------------
def var_data(prey, wolves) -> pd.DataFrame:
    """[dlog prey, dlog wolves]; rows need positive counts in both years."""
    return pd.DataFrame({"dlog_prey": growth(prey), "dlog_wolves": growth(wolves)}).replace(
        [np.inf, -np.inf], np.nan).dropna()


@_quiet
def fit_var(V: pd.DataFrame):
    """Lag chosen by BIC from select_order(maxlags=3), minimum 1; VAR(1) is always fitted
    too because it is the lag used in the comparison table. Returns dict."""
    sel = VAR(V).select_order(maxlags=VAR_MAXLAGS)
    p_bic = max(1, int(sel.bic))
    out = {"selected_lag_bic": p_bic, "selected_lag_aic": int(sel.aic), "order_table": sel.summary()}
    for label, p in [("table", VAR_TABLE_LAG), ("bic", p_bic)]:
        res = VAR(V).fit(p)
        out[f"var_{label}"] = res
        out[f"granger_{label}"] = {
            "wolves -> prey p": res.test_causality("dlog_prey", ["dlog_wolves"], kind="f").pvalue,
            "prey -> wolves p": res.test_causality("dlog_wolves", ["dlog_prey"], kind="f").pvalue,
            "lag": p, "n": res.nobs,
        }
    return out


# ---------------------------------------------------------------------------
# Q3  Cointegration
# ---------------------------------------------------------------------------
@_quiet
def cointegration(prey, wolves) -> dict:
    d = pd.DataFrame({"log_prey": np.log(prey.astype(float)),
                      "log_wolves": np.log(wolves.astype(float))}).replace(
        [np.inf, -np.inf], np.nan).dropna()
    eg_wp = coint(d["log_wolves"], d["log_prey"])
    eg_pw = coint(d["log_prey"], d["log_wolves"])
    jo = coint_johansen(d[["log_prey", "log_wolves"]], det_order=JOHANSEN_DET_ORDER,
                        k_ar_diff=JOHANSEN_K_AR_DIFF)
    rank_trace = int(sum(jo.lr1[i] > jo.cvt[i, 1] for i in range(2)
                         if all(jo.lr1[j] > jo.cvt[j, 1] for j in range(i + 1))))
    rank_maxeig = int(sum(jo.lr2[i] > jo.cvm[i, 1] for i in range(2)
                          if all(jo.lr2[j] > jo.cvm[j, 1] for j in range(i + 1))))
    return {"n": len(d),
            "EG wolves~prey p": eg_wp[1], "EG prey~wolves p": eg_pw[1],
            "Johansen trace stats": jo.lr1.round(2).tolist(), "trace 5% crit": jo.cvt[:, 1].round(2).tolist(),
            "Johansen max-eig stats": jo.lr2.round(2).tolist(), "max-eig 5% crit": jo.cvm[:, 1].round(2).tolist(),
            "rank (trace)": rank_trace, "rank (max-eig)": rank_maxeig, "data": d}


# ---------------------------------------------------------------------------
# Q4  Rolling-origin one-year-ahead forecasts
# ---------------------------------------------------------------------------
@_quiet
def rolling_forecasts(prey, wolves, test_years, score_mask=None) -> pd.DataFrame:
    """Expanding window. For each test year t: fit on rows <= t-1, forecast the count at t
    as N_(t-1) * exp(yhat). Models: naive (yhat = 0), drift (mean growth), ARIMAX wolves,
    ARIMAX wolves + density, VAR(1) on [dlog prey, dlog wolves].
    score_mask: boolean Series by year, True = real count (only those targets are scored)."""
    prey = prey.astype(float)
    y = growth(prey).rename("y")
    X = core_regressors(prey, wolves)
    V = var_data(prey, wolves)
    rows = []
    for t in test_years:
        if score_mask is not None and not bool(score_mask.get(t, True)):
            continue
        row = {"year": t, "actual": prey.loc[t]}
        train_y = y.loc[:t - 1].dropna()
        preds = {"naive": 0.0, "drift": train_y.mean()}
        for name, cols in [("ARIMAX wolves", ["wolves"]), ("ARIMAX wolves + density", ["wolves", "density"])]:
            Xt = core_regressors(prey.loc[:t], wolves.loc[:t])   # centring uses data up to t only
            res, _ = fit_arimax(y.loc[:t - 1], Xt.loc[:t - 1, cols])
            preds[name] = res.params["const"] + (Xt.loc[t, cols] * res.params[cols]).sum()
        Vt = V.loc[:t - 1]
        if len(Vt) >= VAR_MIN_TRAIN + VAR_TABLE_LAG and (t - 1) in Vt.index:
            vr = VAR(Vt).fit(VAR_TABLE_LAG)
            preds["VAR(1)"] = vr.forecast(Vt.values[-VAR_TABLE_LAG:], 1)[0, 0]
        else:
            preds["VAR(1)"] = np.nan
        for k, v in preds.items():
            row[k] = prey.loc[t - 1] * np.exp(v)
        rows.append(row)
    return pd.DataFrame(rows).set_index("year")


def forecast_scores(fc: pd.DataFrame) -> pd.DataFrame:
    """MAE (animals) and MAPE (%) per model, plus % MAE and MAPE gain over drift computed on
    the same years the model was scored on."""
    out = {}
    for m in [c for c in fc.columns if c != "actual"]:
        ok = fc[m].notna()
        err = (fc.loc[ok, m] - fc.loc[ok, "actual"]).abs()
        derr = (fc.loc[ok, "drift"] - fc.loc[ok, "actual"]).abs()
        mae, dmae = err.mean(), derr.mean()
        mape = 100 * (err / fc.loc[ok, "actual"]).mean()
        dmape = 100 * (derr / fc.loc[ok, "actual"]).mean()
        out[m] = {"years scored": int(ok.sum()), "MAE": mae, "MAPE %": mape,
                  "MAE gain over drift %": 100 * (1 - mae / dmae),
                  "MAPE gain over drift %": 100 * (1 - mape / dmape)}
    return pd.DataFrame(out).T


# ---------------------------------------------------------------------------
# Q8  Comparison-table row
# ---------------------------------------------------------------------------
def comparison_row(system, prey, wolves, main_years, effects, var_out, scores) -> dict:
    """One column of the Yellowstone vs Isle Royale table. Every entry is computed the same way."""
    y = growth(prey).loc[lambda s: s.index.isin(main_years)].dropna()
    e = effects.set_index(["model", "term"])

    def fmt(model):
        r = e.loc[(model, "wolves")]
        return f"{r.pct_per_unit:+.1f} [{r.pct_CI_low:+.1f}, {r.pct_CI_high:+.1f}], p={r.p:.3f}"
    g = var_out["granger_table"]
    return {
        "system": system,
        "years (prey growth)": f"{y.index.min()}–{y.index.max()} (n={len(y)})",
        "wolf effect alone, % prey growth per +10 wolves [95% CI]": fmt("wolves"),
        "wolf effect with density, % per +10 wolves [95% CI]": fmt("wolves + density"),
        "wolf effect with density, % per +1 SD of wolves":
            f"{e.loc[('wolves + density', 'wolves'), 'pct_per_unit'] * wolves.astype(float).std() / WOLF_UNIT:+.1f}",
        "Granger p, wolves → prey (VAR(1))": round(g["wolves -> prey p"], 3),
        "Granger p, prey → wolves (VAR(1))": round(g["prey -> wolves p"], 3),
        "forecast MAPE gain over drift, ARIMAX wolves (%)":
            f"{scores.loc['ARIMAX wolves', 'MAPE gain over drift %']:+.1f}",
        "drift of log prey (mean growth, %/yr)": round(100 * y.mean(), 2),
        "volatility of log prey (SD of growth, %)": round(100 * y.std(), 1),
    }
