"""Shared data loaders so every notebook reads the same files the same way."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def load_wolves() -> pd.DataFrame:
    """Annual Yellowstone wolf data, 1995–2025, indexed by year."""
    df = pd.read_csv(RAW / "yellowstone_wolves_1995_2025.csv")
    return df.set_index("year")


def load_gir_lions(analysis_only: bool = True) -> pd.DataFrame:
    """Cleaned Gir lion census; by default only the consistent 1968+ series."""
    df = pd.read_csv(ROOT / "data" / "processed" / "gir_lions_clean.csv", index_col="year")
    return df[df["use_in_analysis"]] if analysis_only else df
