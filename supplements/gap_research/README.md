# Yellowstone data-gap research supplement

Prepared 19 November 2026. **All original data, scripts, notebooks and reports remain unchanged.** This folder is an additive research package, not a replacement production dataset. Sources were checked online; unavailable or incompatible numbers were not invented.

## What was recovered

- **Northern-range wolves, 1996–2000:** 19, 32, 42, 35 and 65 respectively, from the [NPS 2020 report](https://home.nps.gov/yell/learn/nature/upload/FINAL-FOR-APPROVAL-WOLF-REPORT-2020_508R.pdf), retrospective population figure/table. These replace only interpolated values in a **new candidate copy**, `yellowstone_candidate_wolf_gaps.csv`. `wolf_gap_additions.csv` records old/new values, source and drawbacks. Corroborating [Mech 2024 Table 2](https://nsojournals.onlinelibrary.wiley.com/doi/full/10.1002/wlb3.01358) uses the same early northern counts. Northern-range wolves and whole-herd elk do not cover identical geography; that existing limitation remains.
- **Historical elk provenance:** `historical_elk_source_crosswalk.csv` transcribes 21 annual entries from [Tallian et al. 2017, Appendix Table S1](https://qanr.usu.edu/wild/labs/macnulty-lab/files/tallian-et-al-2017-functional-ecology.pdf), with survey dates, uncorrected total counts and explicit modelled flags. It is evidence for reconciliation, not a merge-ready replacement. The published 1998/1999 totals are 11,736/11,742, whereas the existing values are both 11,748. The source's 1999 survey-date entry is reproduced as printed and needs clarification. Survey dates in December often belong to the preceding calendar year. No-survey years 1996, 1997, 2006 and 2014 remain model estimates.
- **Isle Royale:** downloaded the [official NPS dataset](https://www.nps.gov/isro/learn/nature/wolf-moose-populations.htm). The untouched download is retained; a separate 1984–2025 extract preserves missing 2021/2025 observations and excludes 2026. An exploratory comparison uses identical, contiguous 1997–2020 windows, plus 1997–2017 to avoid the later wolf-restoration regime. No missing year is compressed out of the time axis. Yellowstone still contains filled values in this comparison; results are preliminary.

## Measured repercussions

Matched nine eligible evaluation years: 2011–2013, 2017–2019, 2023–2025. MAE is in elk; lower is better.

| Model | Original MAE | Candidate MAE | Interpretation |
|---|---:|---:|---|
| Drift | 1003.79 | 1003.79 | Unchanged benchmark |
| Wolf-only | 986.39 | 983.06 | Very small improvement; advantage over drift rises from 1.7% to 2.1% |
| Full conditional | 1402.13 | 1302.12 | Improved, but still worse than drift |

These are conditional retrospective predictions, not a prospective forecast validation. Nine evaluation years are too few for strong claims. Retrospective wolf counts may not have been available at historical forecast origins. Coefficients, confidence intervals and per-year predictions are supplied separately; statistical associations do not establish causation. The candidate was chosen from source evidence, not by optimizing forecast accuracy.

## Drawbacks and decisions

The complete machine-readable record is **`gap_register.csv`**, including a dedicated **drawbacks** column, mitigation and handoff requirements.

| Gap | Drawback / remaining issue | Action taken |
|---|---|---|
| Early wolves | Retrospective NPS 2001/2008 values (70/57) conflict with existing observed 77/56; early park totals also differ | Added only five missing northern counts in separate scenario; retained all observed originals |
| Elk 2020 | 5,738 in a 2020 compilation is explicitly a 2018 survey | Rejected as a 2020 observation |
| Elk 2021 | HD313 count excludes park portion; park-only figures may use different dates/methods | No synthetic whole-herd sum |
| Elk 2024 | Explicit 5,597 count conflicts with denominator implied by later rounded growth percentage | Preserved explicit count; no reverse calculation |
| Historical elk | Winter-year labels, modelled values and corrected abundance are different measurements | Separate source/date crosswalk only |
| Bison 2023 | Narrative annual average versus selected survey count | No replacement; existing sensitivity work remains intact |
| Climate 2025 | Polygon and original version unknown; TerraClimate advises against mixing v1.0 and v1.1 | No arbitrary geographic or version splice |
| NDVI 2025 | Polygon, sensor harmonisation, masks and compositing unknown | No incompatible satellite/annual substitute |
| Wolf mortality | Annual estimates from Eberhardt Table 1 not recovered; carcasses are not annual population mortality | Left unresolved |
| Isle Royale | Different observation methods; missing years; restoration changes dynamics | Separate dataset and preliminary comparison, explicit missing values and regime sensitivity |

[TerraClimate product documentation](https://www.climatologylab.org/terraclimate.html) explains the version change and non-mixing recommendation. Current precipitation/PDSI files are calendar-year TerraClimate exports; replacing them with water-year NOAA summaries would not preserve their meaning. Current NDVI is a summer Landsat export. A 2025 endpoint is not needed for the existing lag-one climate predictors of the 2025 elk outcome, but will matter for later predictions.

## What to hand off, and to whom

1. **NPS Wolf Project / wildlife data owner:** send `wolf_gap_additions.csv` and `gap_register.csv`. Request the geographic/counting definitions and revision history for early park totals and northern wolves in 2001 and 2008. Ask whether the retrospective series is the preferred consistent series. No existing observed data should be changed without resolving this.
2. **FWP / NPS elk survey owner:** send `historical_elk_source_crosswalk.csv` and the relevant register rows. Request 1984–2003 original survey records, synchronized whole-herd 2020/2021 counts (or explicit no-survey confirmation), and the denominator for the 2025 comparison to 2024. Ask for survey date, area, method, coverage, corrections and uncertainty—not just a number.
3. **Original climate/NDVI exporter:** send the existing raw export filenames and register rows. Request Polygon1 GeoJSON, original product/version, scaling, masks, seasonal aggregation and export script. Reproduce overlapping years before accepting endpoints; any full-version refresh must remain a separate series.
4. **Team member/library with lawful article access:** request Eberhardt et al. (2007), DOI `10.2193/2005-770`, Table 1 and its explanatory text. Need annual wolf-kill estimates, units, year convention and uncertainty. Do not substitute carcass discoveries.
5. **Person 4 / comparative-analysis owner:** hand over both Isle Royale CSVs and `isle_royale_comparison_preliminary.csv`. Review survey comparability and restoration effects before incorporating results in the final comparative table.

These are prepared handoffs; no messages have been sent.

## Files and reproduction

- `gap_register.csv`: decisions, drawbacks, mitigation, source links, owner requests.
- `wolf_gap_additions.csv`: proposed five-row overlay.
- `yellowstone_candidate_wolf_gaps.csv`: separate master-schema candidate; originals untouched.
- `historical_elk_source_crosswalk.csv`: source evidence, not a replacement series.
- `isle_royale_nps_download.csv`: official download; `isle_royale_project_window.csv`: bounded extract.
- `forecast_sensitivity.csv`, `coefficient_sensitivity.csv`: baseline/candidate comparison.
- `baseline/`, `wolf_gap_candidate/`: forecasts, training transformation audits and plots.
- `isle_royale_comparison_preliminary.csv`: matched-window VAR(1) tests, both directions.
- `original_file_hashes.json`, `validation.json`: preservation checks.

Run from project root: `.venv/bin/python supplements/gap_research/build_supplement.py`. This rebuilds only supplement outputs, using the retained official download and recorded transcriptions. It imports existing analysis helpers without running the production pipeline. The script asserts five wolf differences, preserves Isle Royale missing years, and verifies SHA-256 hashes of all 96 baseline project files. It does not establish compatibility for the unresolved sources; those remain explicitly blocked.
