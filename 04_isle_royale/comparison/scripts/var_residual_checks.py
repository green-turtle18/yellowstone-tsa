"""White-noise checks for the VARs behind the Granger tests in Parts 1 and 4.

A Granger test is only valid if the VAR's residuals are white noise. This script refits
the two prespecified VARs and runs the multivariate Portmanteau test (and a Ljung-Box test
on each equation). Run from the repository root:

    python 04_isle_royale/comparison/scripts/var_residual_checks.py
"""
from pathlib import Path
import sys
import warnings

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.api import VAR

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "04_isle_royale/comparison/reports/tables/var_residual_whiteness.csv"
sys.path.insert(0, str(ROOT / "04_isle_royale/scripts"))
import tsa_spec as spec  # noqa: E402

rows = []

def check(system, data, lags, nlags, cause, effect):
    for p in lags:
        res = VAR(data).fit(p)
        lb = [round(acorr_ljungbox(res.resid[c], lags=[nlags]).lb_pvalue.iloc[0], 3) for c in (effect, cause)]
        rows.append({"system": system, "VAR lag": p, "years": f"{data.index.min()}–{data.index.max()}", "n": int(res.nobs),
                     "Granger test": f"{cause} → {effect}", "Granger p": round(res.test_causality(effect, [cause], kind="f").pvalue, 3),
                     "residual lags tested": nlags, "Portmanteau p": round(res.test_whiteness(nlags=nlags, adjusted=True).pvalue, 3),
                     "Ljung–Box p, prey equation": lb[0], "Ljung–Box p, wolf equation": lb[1]})

# Part 1: elk growth and wolf changes, 1997-2025 (the prespecified Q2 VAR).
y = pd.read_csv(ROOT / "01_yellowstone_elk_wolves/data/processed/yellowstone_master_ts_flagged.csv", index_col="Year")
ys = pd.DataFrame({"dlog_elk": np.log(y["Elk_Count"]).diff(), "d_wolves": y["Wolf_Northern"].diff() / 10}).loc[1997:].dropna()
check("Yellowstone (Part 1)", ys, [1, 2], 8, "d_wolves", "dlog_elk")

# Part 4: moose and wolf growth, 1959-2015, built with the shared specification.
ir = pd.read_csv(ROOT / "04_isle_royale/data/processed/isle_royale_annual.csv", index_col="Year")
v = spec.var_data(ir["Moose"].astype(float).loc[1959:2015], ir["Wolves"].astype(float).loc[1959:2015])
check("Isle Royale (Part 4)", v, [1, 2, 3, 4], 10, "dlog_wolves", "dlog_prey")

table = pd.DataFrame(rows)
table.to_csv(OUT, index=False)
print(table.to_string(index=False))
