"""Build the Isle Royale annual master file (Person 4).

Inputs  (run from the repo root):
    data/raw/isle_royale_project_1959_2019.csv   Wolves and Moose of Isle Royale project,
                                                  "Data_wolves_moose_Isle_Royale_June2019.csv"
                                                  (as bundled in R package dsem, dataset isle_royale)
    data/raw/isle_royale_nps_1980_2026.csv       NPS "Wolf & Moose Populations 1980 to Today" download
    data/raw/isle_royale_climate_marss.csv       R package MARSS, dataset isleRoyal
                                                  (NE Minnesota climate division, 1959-2011)
    data/raw/isle_royale_kill_rates_TO_FILL.csv  kill rates + moose CIs from the annual reports
                                                  (mostly empty: the reports give these only as figures)
Outputs:
    data/processed/isle_royale_annual.csv
    reports/tables/isle_royale_source_disagreements.csv

Column conventions (from the brief: `_source` and `_imputed` flags on every variable):
    X_source   where each value came from
                 count            project count (primary series)
                 count_nps        NPS count (used only after the project file ends, 2020+)
                 interpolated     linear midpoint between neighbouring counts
                 missing          no value (left empty, never filled)
    X_imputed  0/1, 1 = not a real observation

Period column (annual winter counts, labelled by the winter they were flown in):
    normal                  all other years
    parvo_crash             1980-1982  canine parvovirus crash (wolves 50 -> 14)
    near_extinction         2012-2018  wolves 9 -> 2, no breeding
    reintroduction          2019       first count after the Sept 2018 - Sept 2019 translocations
    post_reintroduction     2020+
Main_sample = 1 for 1959-2015 (the brief's main analysis window).

Usage:  python scripts/build_isle_royale_annual.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]   # the Person 4 folder
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed" / "isle_royale_annual.csv"
DIS = ROOT / "reports" / "tables" / "isle_royale_source_disagreements.csv"

proj = pd.read_csv(RAW / "isle_royale_project_1959_2019.csv").set_index("Year")
nps = (pd.read_csv(RAW / "isle_royale_nps_1980_2026.csv", na_values=["N/A"])
       .rename(columns={"Number of Moose": "Moose", "Number of Wolves": "Wolves"})
       .set_index("Year"))
clim = pd.read_csv(RAW / "isle_royale_climate_marss.csv").set_index("Year")
kill = pd.read_csv(RAW / "isle_royale_kill_rates_TO_FILL.csv").set_index("Year")

years = pd.RangeIndex(1959, int(nps.index.max()) + 1, name="Year")
out = pd.DataFrame(index=years)

# ---------------------------------------------------------------------------
# Counts: project file is primary (1959-2019); NPS extends it (2020+)
# ---------------------------------------------------------------------------
for col in ["Wolves", "Moose"]:
    s = proj[col].reindex(years).astype(float)
    src = pd.Series(np.where(s.notna(), "count", "missing"), index=years)
    later = (years > proj.index.max())
    s[later] = nps[col].reindex(years)[later]
    src[later & s.notna()] = "count_nps"
    gap = s.isna() & (years > proj.index.max()) & (years < nps.index.max())
    s = s.interpolate(method="index", limit_area="inside")
    src[gap] = "interpolated"
    out[col] = s.round().astype("Int64")
    out[f"{col}_source"] = src
    # NPS values kept side by side for the overlap check
    out[f"{col}_NPS"] = nps[col].reindex(years).astype("Int64")

# The MARSS copy of the counts must agree with the project file (it is an extract of it)
m_chk = clim[["Wolf", "Moose"]].rename(columns={"Wolf": "Wolves"})
mismatch = (m_chk - proj.loc[m_chk.index, ["Wolves", "Moose"]]).abs().sum().sum()
assert mismatch == 0, f"MARSS isleRoyal counts differ from the project file ({mismatch})"

# ---------------------------------------------------------------------------
# Climate (NE Minnesota division, deg F and inches), 1959-2011 only
# ---------------------------------------------------------------------------
CLIM = {
    "jan.feb.ave.temp": "Temp_JanFeb", "jan.feb.ave.precip": "Precip_JanFeb",
    "apr.may.ave.temp": "Temp_AprMay", "apr.may.ave.precip": "Precip_AprMay",
    "july.sept.ave.temp": "Temp_JulSep", "july.sept.ave.precip": "Precip_JulSep",
}
for raw_col, col in CLIM.items():
    s = clim[raw_col].reindex(years)
    out[col] = s
    out[f"{col}_source"] = np.where(s.notna(), "count", "missing")

# ---------------------------------------------------------------------------
# Kill rate and moose confidence interval (annual reports) - mostly missing
# ---------------------------------------------------------------------------
for col in ["Kill_rate_per_wolf_per_month", "Moose_CI90_low", "Moose_CI90_high"]:
    s = pd.to_numeric(kill[col], errors="coerce").reindex(years)
    out[col] = s
    out[f"{col}_source"] = np.where(s.notna(), "annual_report", "missing")

# ---------------------------------------------------------------------------
# Flags
# ---------------------------------------------------------------------------
for col in ["Wolves", "Moose"] + list(CLIM.values()):
    out[f"{col}_imputed"] = (~out[f"{col}_source"].isin(["count", "count_nps"])).astype(int)

period = pd.Series("normal", index=years)
period[(years >= 1980) & (years <= 1982)] = "parvo_crash"
period[(years >= 2012) & (years <= 2018)] = "near_extinction"
period[years == 2019] = "reintroduction"
period[years >= 2020] = "post_reintroduction"
out["Period"] = period
out["Main_sample"] = ((years >= 1959) & (years <= 2015)).astype(int)

OUT.parent.mkdir(parents=True, exist_ok=True)
out.to_csv(OUT)

# ---------------------------------------------------------------------------
# Where the two count sources disagree (overlap 1980-2019)
# ---------------------------------------------------------------------------
ov = pd.DataFrame({
    "Moose_project": proj["Moose"], "Moose_NPS": nps["Moose"],
    "Wolves_project": proj["Wolves"], "Wolves_NPS": nps["Wolves"],
}).loc[1980:2019]
ov["Moose_diff_pct"] = 100 * (ov["Moose_NPS"] / ov["Moose_project"] - 1)
ov["Wolves_diff"] = ov["Wolves_NPS"] - ov["Wolves_project"]
# Is the NPS moose value equal to the project value one year earlier or later?
ov["NPS_moose_equals_project_t+1"] = ov["Moose_NPS"].values == proj["Moose"].reindex(ov.index + 1).values
ov["NPS_moose_equals_project_t-1"] = ov["Moose_NPS"].values == proj["Moose"].reindex(ov.index - 1).values
DIS.parent.mkdir(parents=True, exist_ok=True)
ov.round(1).to_csv(DIS)

print(f"Saved {OUT.relative_to(ROOT)}  ({len(out)} years, {years.min()}-{years.max()})")
for col in ["Wolves", "Moose", "Temp_JanFeb", "Kill_rate_per_wolf_per_month"]:
    print(f"{col:30s} {out[f'{col}_source'].value_counts().to_dict()}")
print("\nOverlap 1980-2019:")
print(f"  wolves identical in {(ov['Wolves_diff'] == 0).sum()} of {len(ov)} years")
print(f"  moose identical in  {(ov['Moose_diff_pct'].abs() < 0.5).sum()} of {len(ov)} years; "
      f"median |diff| {ov['Moose_diff_pct'].abs().median():.0f}%")
