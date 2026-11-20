"""Q4 rolling-origin forecasts (slow step, run separately from notebook 13).

Run from the 03_park_visitation/ folder after notebook 13's Q0 section has written
reports/tables/q0_sarima_spec.json and reports/tables/q4_ets_selection.csv:

    python scripts/q4_rolling_forecasts.py

Writes reports/tables/q4_rolling_forecasts.csv, which notebook 13 then loads.
If reports/tables/q0_sarima_d0_spec.json exists (written by notebook 13, Q0.9), the d = 0 + drift
SARIMA alternative is included as a fifth model.
At every month-end origin from Dec 2009 to Nov 2025, each model is refitted on data up
to the origin and forecasts 1 and 12 months ahead. Takes ~5-10 minutes on 2 cores.
"""
import json
import sys
import time
import warnings
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "reports/tables"
H = (1, 12)
EXOG = ["D_fire88", "D_covid20", "D_flood22", "D_shutdown"]

v = pd.read_csv(ROOT / "data/processed/yell_visits_monthly.csv", parse_dates=["Date"], index_col="Date")
v = v[v.Preliminary == 0].asfreq("MS")
y, visits = v["LogVisits"], v["Visits"]

spec = json.loads((TAB / "q0_sarima_spec.json").read_text())
ORDER, SORDER = tuple(spec["order"]), tuple(spec["seasonal_order"])
X = v[EXOG].copy()
X["C_count93"] = (v.index >= "1993-01-01").astype(int)
X["C_count13"] = (v.index >= "2013-01-01").astype(int)
assert list(X.columns) == spec["exog"]

ets = pd.read_csv(TAB / "q4_ets_selection.csv").iloc[0]
ETS_SPEC = dict(error=ets.error, trend=None if pd.isna(ets.trend) else ets.trend,
                damped_trend=bool(ets.damped), seasonal=ets.seasonal)

# HW/ETS cannot take the zero in Apr 2020 or dummies: replace COVID and flood months in
# the training data by the same month one year earlier (scoring always uses actuals).
visits_clean = visits.copy()
for d in v.index[(v.D_covid20 == 1) | (v.D_flood22 == 1)]:
    visits_clean[d] = visits[d - pd.DateOffset(years=1)]


def fc_snaive(m, hmax):
    idx = pd.date_range(m + pd.DateOffset(months=1), periods=hmax, freq="MS")
    return pd.Series([visits[d - pd.DateOffset(years=1)] for d in idx], idx)  # h <= 12


def fc_sarima(m, hmax):
    fit = SARIMAX(y[:m], exog=X[:m], order=ORDER, seasonal_order=SORDER).fit(disp=False)
    idx = pd.date_range(m + pd.DateOffset(months=1), periods=hmax, freq="MS")
    Xf = X.reindex(idx).copy()
    Xf[EXOG] = 0  # the forecaster does not know a shock is coming
    Xf[["C_count93", "C_count13"]] = X.loc[m, ["C_count93", "C_count13"]].values
    pr = fit.get_forecast(hmax, exog=Xf)
    return pd.Series(np.exp(pr.predicted_mean + pr.var_pred_mean / 2).values, idx)  # log-normal mean


spec0_path = TAB / "q0_sarima_d0_spec.json"
SPEC0 = json.loads(spec0_path.read_text()) if spec0_path.exists() else None


def fc_sarima_d0(m, hmax):
    fit = SARIMAX(y[:m], exog=X[:m], order=tuple(SPEC0["order"]), seasonal_order=tuple(SPEC0["seasonal_order"]),
                  trend="c").fit(disp=False)
    idx = pd.date_range(m + pd.DateOffset(months=1), periods=hmax, freq="MS")
    Xf = X.reindex(idx).copy()
    Xf[EXOG] = 0
    Xf[["C_count93", "C_count13"]] = X.loc[m, ["C_count93", "C_count13"]].values
    pr = fit.get_forecast(hmax, exog=Xf)
    return pd.Series(np.exp(pr.predicted_mean + pr.var_pred_mean / 2).values, idx)


def fc_hw(m, hmax):
    return ExponentialSmoothing(visits_clean[:m], trend="add", seasonal="mul",
                                seasonal_periods=12).fit().forecast(hmax)


def fc_ets(m, hmax):
    return ETSModel(visits_clean[:m], seasonal_periods=12, **ETS_SPEC).fit(disp=False).forecast(hmax)


MODELS = {"Seasonal naive": fc_snaive, "SARIMA": fc_sarima, "Holt–Winters": fc_hw, "ETS": fc_ets}
if SPEC0 is not None:
    MODELS["SARIMA d=0 + drift"] = fc_sarima_d0


def run_origin(m):
    recs = []
    for name, f in MODELS.items():
        fc = f(m, max(H))
        for h in H:
            tgt = m + pd.DateOffset(months=h)
            if tgt <= visits.index[-1]:
                recs.append(dict(origin=m, target=tgt, h=h, model=name,
                                 forecast=float(fc[tgt]), actual=float(visits[tgt])))
    return recs


if __name__ == "__main__":
    origins = list(pd.date_range("2009-12-01", "2025-11-01", freq="MS"))
    t0, out = time.time(), []
    with Pool(2) as pool:
        for i, recs in enumerate(pool.imap(run_origin, origins), 1):
            out.extend(recs)
            if i % 12 == 0 or i == len(origins):
                print(f"{i}/{len(origins)} origins done ({time.time() - t0:.0f}s)", flush=True)
    df = pd.DataFrame(out).sort_values(["model", "h", "origin"])
    df.to_csv(TAB / "q4_rolling_forecasts.csv", index=False)
    print(f"Wrote {len(df)} forecasts to {TAB / 'q4_rolling_forecasts.csv'}")
    sys.exit(0)
