"""Clean the Gir lion census file.

Input : data/raw/gir_lion_census_by_age.csv   (themapsdaily download, long format)
Output: data/processed/gir_lions_clean.csv    (one row per census year)

Run from the repo root:  python src/clean_lions.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "gir_lion_census_by_age.csv"
OUT = ROOT / "data" / "processed" / "gir_lions_clean.csv"

raw = pd.read_csv(RAW)

# 1. Remove duplicates. From 1963 on, every year appears as both "Gujarat" and
#    "India" with identical numbers. Keep Gujarat; earlier years only exist as
#    India / British Raj, so those are kept as they are.
raw["is_gujarat"] = (raw["region"] == "Gujarat").astype(int)
raw = (raw.sort_values("is_gujarat", ascending=False)
          .drop_duplicates(["year", "Demographic Group"]))

# 2. Reshape: one row per census year, one column per age/sex group.
df = raw.pivot(index="year", columns="Demographic Group", values="value")
df = df.rename(columns={
    "Overall": "total",
    "Adult - Male": "adult_male",
    "Adult - Female": "adult_female",
    "Sub-Adult": "sub_adult",
    "Cub": "cub",
})[["total", "adult_male", "adult_female", "sub_adult", "cub"]]
df.index.name = "year"

# 3. Quality flags.
df["source_flagged_inconsistent"] = raw.groupby("year")["quality"].apply(lambda s: s.notna().any())
parts = df[["adult_male", "adult_female", "sub_adult", "cub"]].sum(axis=1, min_count=1)
df["parts_sum_matches_total"] = parts == df["total"]

# Analysis window: 1968 onward = consistent Forest Department census method.
# Pre-1968 estimates are kept for context plots only.
df["use_in_analysis"] = df.index >= 1968

# 4. Derived columns.
df["years_since_prev"] = df.index.to_series().diff()
df["growth_rate_pct_per_yr"] = 100 * np.log(df["total"]).diff() / df["years_since_prev"]
df["cub_pct"] = 100 * df["cub"] / df["total"]
df["adult_sex_ratio_f_per_m"] = df["adult_female"] / df["adult_male"]

# Growth rate into 1968 compares two different census methods → blank it.
df.loc[1968, "growth_rate_pct_per_yr"] = np.nan

OUT.parent.mkdir(parents=True, exist_ok=True)
df.round(2).to_csv(OUT)
print(f"Saved {OUT.relative_to(ROOT)}: {len(df)} census years, "
      f"{int(df['use_in_analysis'].sum())} in analysis window")
