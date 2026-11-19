"""Add fill-method columns to the Yellowstone master dataset.

Inputs  (run from the repo root):
    data/processed/yellowstone_master_ts_final.csv
    data/raw/yellowstone_wolves_1995_2025.csv
Output:
    data/processed/yellowstone_master_ts_flagged.csv

For every variable X there is now a column X_source saying where each value came from:
    count             real observation from the source
    count_hd313       real MT FWP Hunting District 313 count (2016+; may cover only part of the herd)
    interpolated      linear midpoint between neighbouring real counts
    backfilled        copied from the next real count (before the first observation)
    carried_forward   copied from the previous year (no new value available)
    estimate          news / conservation estimate, not an official count
    structural_zero   true zero (no wolves before the 1995 reintroduction)

If you later replace a filled value with a real one, change its entry in FILLS below.

Usage:  python scripts/build_master_flagged.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "processed" / "yellowstone_master_ts_final.csv"
WOLVES = ROOT / "data" / "raw" / "yellowstone_wolves_1995_2025.csv"
OUT = ROOT / "data" / "processed" / "yellowstone_master_ts_flagged.csv"

# ---------------------------------------------------------------------------
# Every non-observed value, by variable. Anything not listed = "count".
# ---------------------------------------------------------------------------
FILLS = {
    "Elk_Count": {
        1984: "backfilled",       # no count; copied from 1986
        1985: "backfilled",       # no count; copied from 1986
        1989: "interpolated",
        1991: "interpolated",
        1996: "interpolated",
        1997: "interpolated",
        2006: "interpolated",
        2014: "interpolated",
        2019: "carried_forward",  # copy of 2018
        2020: "carried_forward",  # copy of 2018
    },
    "Bison_Count": {
        2023: "carried_forward",  # identical to 2022 - check bison report
        2025: "estimate",         # news / conservation estimate
    },
    "Precip_Annual": {2025: "carried_forward"},  # copy of 2024 - re-download WY2025
    "PDSI_Annual": {2025: "carried_forward"},    # copy of 2024 - re-download WY2025
    "NDVI": {},
}

# Elk values from 2016 on come from a different survey (MT FWP HD 313)
ELK_SPLICE_YEAR = 2016

# Values to double-check against the original source (not fills, just suspicious)
VERIFY = {
    "Elk_Count": [1999],  # identical to 1998 (11,748) in MacNulty et al. 2016
}


def source_column(df: pd.DataFrame, col: str) -> pd.Series:
    src = pd.Series("count", index=df.index)
    for year, method in FILLS.get(col, {}).items():
        if year in src.index:
            src[year] = method
    if col == "Elk_Count":
        later = (src.index >= ELK_SPLICE_YEAR) & (src == "count")
        src[later] = "count_hd313"
    return src


master = pd.read_csv(MASTER).set_index("Year")
wolves = pd.read_csv(WOLVES).set_index("year")
out = pd.DataFrame(index=master.index)

# Elk, bison, vegetation, climate: value + source column
for col in ["Elk_Count", "Bison_Count", "NDVI", "Precip_Annual", "PDSI_Annual"]:
    out[col] = master[col]
    out[f"{col}_source"] = source_column(master, col)

# Wolves, park-wide total (what the old Wolf_Count column actually held)
park = wolves["total_wolves_end_of_year"].reindex(out.index)
out["Wolf_Park"] = park.fillna(0).astype(int)
out["Wolf_Park_source"] = np.where(out.index < 1995, "structural_zero", "count")

# Wolves, northern range only (matches the README's Northern Range focus)
north = wolves["northern_range_total_wolves"].reindex(out.index)
north_src = pd.Series("count", index=out.index)
north_src[out.index < 1995] = "structural_zero"
north[out.index < 1995] = 0
missing = north.isna()
north_src[missing] = "interpolated"
out["Wolf_Northern"] = north.interpolate(method="index").round().astype(int)
out["Wolf_Northern_source"] = north_src

# Optional 0/1 flag per variable for quick filtering in models
for col in ["Elk_Count", "Bison_Count", "NDVI", "Precip_Annual", "PDSI_Annual",
            "Wolf_Park", "Wolf_Northern"]:
    s = out[f"{col}_source"]
    out[f"{col}_imputed"] = (~s.isin(["count", "count_hd313", "structural_zero"])).astype(int)

out.index.name = "Year"
OUT.parent.mkdir(parents=True, exist_ok=True)
out.to_csv(OUT)

# Summary
print(f"Saved {OUT.relative_to(ROOT)}  ({len(out)} years, {out.index.min()}-{out.index.max()})\n")
for col in ["Elk_Count", "Bison_Count", "NDVI", "Precip_Annual", "PDSI_Annual",
            "Wolf_Park", "Wolf_Northern"]:
    counts = out[f"{col}_source"].value_counts().to_dict()
    print(f"{col:15s} {counts}")
for col, years in VERIFY.items():
    print(f"\nVerify against source: {col} in {years}")