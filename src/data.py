"""Shared data loaders so every notebook reads the same files the same way."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def load_wolves() -> pd.DataFrame:
    """Annual Yellowstone wolf data, 1995–2025, indexed by year."""
    df = pd.read_csv(RAW / "yellowstone_wolves_1995_2025.csv")
    return df.set_index("year")


def load_gir_lions(since: int = 1968) -> pd.DataFrame:
    """Gir lion census counts; defaults to the consistent Forest Dept series from 1968."""
    df = pd.read_csv(RAW / "gir_lion_census.csv")
    return df[df["Year"] >= since].set_index("Year")
