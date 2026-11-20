"""Build a winter severity index (and monthly temperature) from daily SNOTEL data.

Usage (from the repo root):
    python scripts/build_severity_index.py data/raw/snotel_northeast_entrance.csv [more station files ...]

Outputs:
    data/processed/winter_severity_index.csv   one row per winter, labelled by the year it ends
    data/processed/monthly_temperature.csv     monthly mean air temperature (deg C), for Person 3

Winter convention: Nov (Y-1) - Apr (Y) is labelled Y, the same as the elk counts
(the 1995-96 winter is 1996). Melt-out uses the water year Oct (Y-1) - Sep (Y).

Severity components (all from snow water equivalent, which is complete back to 1966):
    Peak_SWE_in      largest SWE of the water year
    Accum_SWE_in_d   sum of daily SWE over Nov-Apr (deep AND long-lasting snow scores high)
    Snow_days        days in the water year with SWE >= 1 inch
Severity_index = mean of the three z-scores, averaged across stations. Each station is
standardised over the winters all stations share, so the stations sit on one baseline;
winters before the later stations start use fewer stations (see Stations_used).
Cold_days (Nov-Apr days with mean temp < 0 F) is reported separately because
temperature only starts in 1984 at Northeast Entrance.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

MIN_COVERAGE = 0.9          # drop a winter if more than 10% of days are missing
SNOW_DAY_SWE_IN = 1.0       # a "snow day" has at least 1 inch of SWE on the ground
TEMP_MIN_F = -60            # anything colder is treated as a sensor error


def load_station(path):
    d = pd.read_csv(path, comment="#", parse_dates=["Date"])
    cols = {c: c for c in d.columns}
    for c in d.columns:
        lc = c.lower()
        if lc.startswith("snow water equivalent"):
            cols[c] = "SWE"
        elif lc.startswith("snow depth"):
            cols[c] = "DEPTH"
        elif lc.startswith("air temperature average"):
            cols[c] = "TAVG"
    d = d.rename(columns=cols).set_index("Date").sort_index()
    if "TAVG" in d:
        d.loc[d["TAVG"] < TEMP_MIN_F, "TAVG"] = np.nan
    d["water_year"] = d.index.year + (d.index.month >= 10)
    return d


def winter_stats(d):
    rows = []
    for wy, g in d.groupby("water_year"):
        win = g[(g.index.month >= 11) | (g.index.month <= 4)]
        expected_win = len(pd.date_range(f"{wy-1}-11-01", f"{wy}-04-30"))
        expected_wy = len(pd.date_range(f"{wy-1}-10-01", f"{wy}-09-30"))
        cov_win = win["SWE"].count() / expected_win
        cov_wy = g["SWE"].count() / expected_wy
        if cov_win < MIN_COVERAGE:
            continue
        swe = g["SWE"]
        peak_date = swe.idxmax()
        after = swe.loc[peak_date:]
        melted = after[after <= 0]
        melt_doy = melted.index[0].dayofyear if len(melted) and cov_wy >= MIN_COVERAGE else np.nan
        cold = np.nan
        if "TAVG" in win and win["TAVG"].count() / expected_win >= MIN_COVERAGE:
            cold = int((win["TAVG"] < 0).sum())
        rows.append({
            "Year": wy,
            "Peak_SWE_in": swe.max(),
            "Peak_SWE_date": peak_date.date().isoformat(),
            "Accum_SWE_in_d": win["SWE"].sum(),
            "Snow_days": int((swe >= SNOW_DAY_SWE_IN).sum()) if cov_wy >= MIN_COVERAGE else np.nan,
            "Melt_out_doy": melt_doy,
            "Cold_days": cold,
            "Coverage": round(cov_win, 3),
        })
    return pd.DataFrame(rows).set_index("Year")


def zscore(s, ref):
    """Standardise using only the reference years, so every station shares one baseline."""
    r = s.loc[s.index.intersection(ref)]
    return (s - r.mean()) / r.std()


def main(paths):
    per_station = {Path(p).stem: winter_stats(load_station(p)) for p in paths}
    comps = ["Peak_SWE_in", "Accum_SWE_in_d", "Snow_days"]
    # Common baseline: winters every station has (otherwise a station that starts in a
    # snowy decade would look systematically mild, or vice versa).
    ref = None
    for w in per_station.values():
        yrs = w.dropna(subset=comps).index
        ref = yrs if ref is None else ref.intersection(yrs)
    station_index = pd.DataFrame({
        name: pd.concat([zscore(w[c], ref) for c in comps], axis=1).mean(axis=1, skipna=False)
        for name, w in per_station.items()
    })
    print(f"Baseline winters: {ref.min()}-{ref.max()} ({len(ref)})")
    print("Agreement between stations (correlation of yearly index):")
    print(station_index.corr().round(2))
    # Combined columns. Station means would jump whenever a station joins (Parker Peak is
    # higher and snowier), so combine as anomalies from each station's baseline mean.
    out = pd.DataFrame(index=station_index.index)
    out.index.name = "Year"
    out["Severity_index"] = station_index.mean(axis=1)
    out["Stations_used"] = station_index.notna().sum(axis=1)
    out["Severity_imputed"] = 0
    out["Melt_out_anom_days"] = pd.DataFrame({
        n: w["Melt_out_doy"] - w["Melt_out_doy"].loc[w.index.intersection(ref)].mean()
        for n, w in per_station.items()
    }).mean(axis=1)
    # Raw components per station, for anyone who wants the physical values.
    for name, w in per_station.items():
        short = name.replace("snotel_", "")
        for c in ["Peak_SWE_in", "Accum_SWE_in_d", "Snow_days", "Melt_out_doy", "Cold_days"]:
            out[f"{c}__{short}"] = w[c]
    out = out.round(3)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    out.to_csv("data/processed/winter_severity_index.csv")

    # Monthly temperature: average station anomalies from a shared 1988-2025 monthly
    # climatology, then add back the mean climatology, so the series doesn't jump when
    # stations start or drop out.
    temps = {}
    for p in paths:
        d = load_station(p)
        if "TAVG" not in d:
            continue
        m = d["TAVG"].resample("MS").agg(["mean", "count"])
        m.loc[m["count"] / m.index.days_in_month < MIN_COVERAGE, "mean"] = np.nan
        temps[Path(p).stem] = (m["mean"] - 32) * 5 / 9
    if temps:
        t = pd.DataFrame(temps)
        base = t.loc["1988":"2025"]
        clim = base.groupby(base.index.month).mean()
        anom = t - clim.reindex(t.index.month).set_index(t.index)
        overall = clim.mean(axis=1).reindex(t.index.month).values
        mt = pd.DataFrame({
            "Temp_mean_C": anom.mean(axis=1) + overall,
            "Temp_anom_C": anom.mean(axis=1),
            "Stations_used": t.notna().sum(axis=1),
        })
        mt = mt[mt["Stations_used"] > 0].round(2)
        mt.index.name = "Month"
        mt.to_csv("data/processed/monthly_temperature.csv")

    print(out[["Severity_index", "Stations_used", "Melt_out_anom_days"]].describe().round(2))


if __name__ == "__main__":
    main(sys.argv[1:] or ["data/raw/snotel_northeast_entrance.csv"])
