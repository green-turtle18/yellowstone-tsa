# Data checklist

Tick each item once the file is in `data/raw/` or `data/external/` with its source noted below.
If an item can't be found, mark it ❌ and cut the dependent report sections.

| Status | Dataset | Frequency / span | Likely source | Unlocks |
|---|---|---|---|---|
| ✅ | Yellowstone wolves (31 variables) | annual, 1995–2025 | Yellowstone Wolf Project annual reports | 3, 4, 6.2–6.3 |
| ✅ | Gir lion census | 5-yearly, 1880–2025 | Gujarat Forest Dept census | 9.1–9.2 |
| ❌  | Gir lion deaths | annual, 2013–2025 | Inconsistent across sources | 9.3 |
| ⬜ | Yellowstone visitation | monthly, 1979–2025 | NPS Visitor Use Statistics | 3.2, 7 |
| ⬜ | Temperature (in-park stations) | daily → monthly | NOAA NCEI GHCN-Daily | 2.2, 5, 6 |
| ⬜ | Snowpack (SWE, snow depth) | daily → monthly | NRCS SNOTEL sites near the park | 2.2, 5, 6 |
| ⬜ | Northern Yellowstone elk counts | annual, as far back as possible | Northern Yellowstone Cooperative Wildlife Working Group | 6.1, 6.5–6.7 |
| ⬜ | Yellowstone bison estimates | annual | NPS bison program reports | 6.1, 6.5–6.7 |
| ⬜ | Exogenous drivers (gas prices etc.) | monthly | US EIA | 7.2 (optional) |
| ⬜ | Tiger data (estimates / NTCA mortality) | 4-yearly / monthly | NTCA | 9.5 (optional) |

## Known issues in existing data
- `northern_yellowstone_elk_herd_count`: only 3 values → replace with external series.
- Kill and death counts depend on collaring effort (`total_active_collars_year_end`) → prefer % columns.
- Missing values in `pups_born_min`, `pup_survival_rate_pct`, northern/non-northern split, collar columns.

## Sources (fill in as you download)
-
