"""Build clean Yellowstone visitation files from the raw IRMA exports.

Run from the 03_park_visitation/ folder:  python scripts/build_visitation_data.py

Inputs  (data/raw/, untouched IRMA exports)
    yell_visits_monthly_irma.xlsx            Recreation Visits By Month (1979 - current)
    yell_visits_annual_irma.xlsx             Annual Park Recreation Visits (1904 - last year)
    yell_traffic_counts_by_entrance_irma.xlsx Traffic Counts by Location (1993 - current)

Outputs (data/processed/)
    yell_visits_monthly.csv      Date, Year, Month, Visits, LogVisits, Preliminary, Note
    yell_traffic_by_entrance.csv Date, Year, Month, Entrance, Vehicles
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data/raw", ROOT / "data/processed"
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
LAST_FINAL_YEAR = 2025  # IRMA marks the current calendar year as preliminary


# ---------------------------------------------------------------- monthly visits
def read_monthly_visits() -> pd.DataFrame:
    raw = pd.read_excel(RAW / "yell_visits_monthly_irma.xlsx", header=None)
    hdr = raw.index[raw.apply(lambda r: "JAN" in r.values, axis=1)][0]
    cols = raw.iloc[hdr].tolist()
    body = raw.iloc[hdr + 1:].copy()
    body.columns = cols
    body = body.rename(columns={c: "Year" for c in cols if str(c) == "Year"})
    body = body[pd.to_numeric(body["Year"], errors="coerce").notna()]
    long = body.melt(id_vars="Year", value_vars=MONTHS,
                     var_name="Mon", value_name="Visits")
    long["Year"] = long["Year"].astype(int)
    long["Month"] = long["Mon"].map({m: i + 1 for i, m in enumerate(MONTHS)})
    long["Date"] = pd.to_datetime(dict(year=long.Year, month=long.Month, day=1))
    long["Visits"] = pd.to_numeric(long["Visits"], errors="coerce")
    long = long.dropna(subset=["Visits"])  # unreported future months of current year
    return (long.sort_values("Date")[["Date", "Year", "Month", "Visits"]]
            .reset_index(drop=True))


# Known oddities. Sources: project brief + IRMA "Monthly Visitation Comments"
# + IRMA "Park Visitor Use and Count Procedure Changes".
NOTES = {
    ("1988-07", "1988-09"): "1988 fires",
    ("1993-01", "1993-01"): "count procedure change: traffic-counter estimates replace manual counts (1993)",
    ("1995-11", "1995-11"): "government shutdown Nov 14-19 1995",
    ("1995-12", "1996-01"): "government shutdown Dec 16 1995 - Jan 6 1996",
    ("2013-01", "2013-01"): "count procedure change: new persons-per-vehicle multipliers (2013)",
    ("2013-10", "2013-10"): "government shutdown Oct 1-16",
    ("2014-07", "2014-07"): "West Entrance switched to traffic counter",
    ("2016-08", "2016-08"): "South Entrance closed 6 days (Berry Fire)",
    ("2017-08", "2017-08"): "solar eclipse (Aug 21)",
    ("2018-01", "2018-01"): "government shutdown Jan 20-22",
    ("2018-12", "2019-01"): "government shutdown Dec 22 2018 - Jan 26 2019",
    ("2020-03", "2020-03"): "COVID closure begins (Mar 24)",
    ("2020-04", "2020-04"): "COVID closure (park closed all month)",
    ("2020-05", "2020-05"): "COVID closure (South/East reopened May 18 only)",
    ("2021-04", "2021-04"): "new traffic counter at West Entrance",
    ("2021-06", "2021-06"): "new North Entrance station + counter (old counter caught one lane)",
    ("2022-01", "2022-01"): "North Entrance switches to counter-based counts",
    ("2022-06", "2022-06"): "flood closure (all entrances closed Jun 13; partial reopen Jun 22)",
    ("2022-07", "2022-10"): "flood: North & Northeast entrances closed (reopened Oct 15/30)",
    ("2025-10", "2025-10"): "government shutdown (lapse in funding)",
}

# Months to dummy out in the SARIMA (Q0 step 6). Count-procedure and minor
# items are notes only, not shock dummies.
SHOCK_DUMMIES = {
    "fire88":    ("1988-07", "1988-09"),
    "covid20":   ("2020-03", "2020-05"),
    "flood22":   ("2022-06", "2022-10"),
    "shutdown":  None,  # filled below: Oct 2013, Dec 2018, Jan 2019, Oct 2025
}
SHUTDOWN_MONTHS = ["1995-12", "1996-01", "2013-10", "2018-12", "2019-01", "2025-10"]


def add_notes(df: pd.DataFrame) -> pd.DataFrame:
    df["Note"] = ""
    ym = df["Date"].dt.strftime("%Y-%m")
    for (a, b), text in NOTES.items():
        m = (ym >= a) & (ym <= b)
        df.loc[m, "Note"] = np.where(df.loc[m, "Note"] == "", text,
                                     df.loc[m, "Note"] + "; " + text)
    for name, rng in SHOCK_DUMMIES.items():
        if rng is None:
            df[f"D_{name}"] = ym.isin(SHUTDOWN_MONTHS).astype(int)
        else:
            df[f"D_{name}"] = ((ym >= rng[0]) & (ym <= rng[1])).astype(int)
    df["Preliminary"] = (df["Year"] > LAST_FINAL_YEAR).astype(int)
    p = df.Preliminary == 1
    df.loc[p, "Note"] = (df.loc[p, "Note"] + "; preliminary (current-year IRMA data)").str.lstrip("; ")
    return df


# ------------------------------------------------------------- checks
def check_complete(df: pd.DataFrame) -> None:
    final = df[df.Year <= LAST_FINAL_YEAR]
    years = final.Year.nunique()
    assert len(final) == 12 * years, f"{len(final)} rows for {years} years"
    full = pd.date_range(final.Date.min(), final.Date.max(), freq="MS")
    assert final.Date.reset_index(drop=True).equals(pd.Series(full, name="Date")), "gaps"
    assert (final.Visits >= 0).all()
    zeros = final.loc[final.Visits == 0, "Date"].dt.strftime("%Y-%m").tolist()
    print(f"OK: {len(final)} monthly rows, {final.Date.min():%Y-%m} to "
          f"{final.Date.max():%Y-%m}, no gaps. Zero months: {zeros or 'none'}")


def cross_check_annual(df: pd.DataFrame) -> pd.DataFrame:
    ann = pd.read_excel(RAW / "yell_visits_annual_irma.xlsx", header=None)
    hdr = ann.index[ann.apply(lambda r: "Year" in r.values, axis=1)][0]
    ann = ann.iloc[hdr + 1:, [2, 3]]
    ann.columns = ["Year", "AnnualIRMA"]
    ann = ann[pd.to_numeric(ann.Year, errors="coerce").notna()].astype(int)
    sums = df[df.Year <= LAST_FINAL_YEAR].groupby("Year").Visits.sum().rename("MonthlySum")
    cmp_ = sums.to_frame().join(ann.set_index("Year"))
    cmp_["PctDiff"] = 100 * (cmp_.MonthlySum - cmp_.AnnualIRMA) / cmp_.AnnualIRMA
    bad = cmp_[cmp_.PctDiff.abs() > 1]
    print(f"Annual cross-check vs IRMA annual report: max |diff| = "
          f"{cmp_.PctDiff.abs().max():.3f}%; years >1%: {list(bad.index) or 'none'}")
    return cmp_


# ------------------------------------------------------------- entrance traffic
def read_traffic() -> pd.DataFrame:
    raw = pd.read_excel(RAW / "yell_traffic_counts_by_entrance_irma.xlsx", header=None)
    rows, loc = [], None
    for _, r in raw.iterrows():
        lab = r[2]
        if isinstance(lab, str) and lab.startswith("TRAFFIC COUNT"):
            loc = (lab.replace("TRAFFIC COUNT AT ", "").replace("TRAFFIC COUNT ON ", "")
                   .replace(" GATE", "").title())
            continue
        if loc and pd.notna(pd.to_numeric(lab, errors="coerce")):
            for i, m in enumerate(MONTHS):
                v = pd.to_numeric(r[3 + i], errors="coerce")
                rows.append((int(lab), i + 1, loc, v))
    t = pd.DataFrame(rows, columns=["Year", "Month", "Entrance", "Vehicles"])
    t["Date"] = pd.to_datetime(dict(year=t.Year, month=t.Month, day=1))
    # 1992 is all zeros and 1991 only has a December value: not real data.
    t = t[t.Year >= 1993].dropna(subset=["Vehicles"])
    return t.sort_values(["Entrance", "Date"])[["Date", "Year", "Month", "Entrance", "Vehicles"]]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    v = add_notes(read_monthly_visits())
    v["LogVisits"] = np.log(v.Visits.where(v.Visits > 0))
    check_complete(v)
    cmp_ = cross_check_annual(v)
    cols = ["Date", "Year", "Month", "Visits", "LogVisits", "Preliminary", "Note"] + \
           [c for c in v.columns if c.startswith("D_")]
    v[cols].to_csv(OUT / "yell_visits_monthly.csv", index=False, date_format="%Y-%m-%d")
    cmp_.round(4).to_csv(OUT / "yell_visits_annual_crosscheck.csv")

    t = read_traffic()
    t.to_csv(OUT / "yell_traffic_by_entrance.csv", index=False, date_format="%Y-%m-%d")
    print(f"Traffic: {t.Entrance.unique().tolist()}, {t.Date.min():%Y-%m} to {t.Date.max():%Y-%m}")


if __name__ == "__main__":
    main()
