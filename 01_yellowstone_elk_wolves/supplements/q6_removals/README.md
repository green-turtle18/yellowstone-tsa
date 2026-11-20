# Q6 completed: descriptive wolf-kill and hunting comparison

The completed comparison is integrated into notebook 03, the main reports and the drivers rebuild. The old q6_removals_pending.csv is retained only as a historical placeholder. Q6's statistical regression remains unchanged; this completes the previously blocked descriptive component.

## Source and definitions

Eberhardt, White, Garrott & Houston (2007), *A Seventy-Year History of Trends in Yellowstone's Northern Elk Herd*, Journal of Wildlife Management 71(2):594–602. DOI https://doi.org/10.2193/2005-770. Table 1 is on printed page 598 / PDF page 5. Source: the user-provided full paper, library ID `libfile_13c9a35b65e88191ad6e4ffac08e27d8`.

The methods (printed p.595) generally label winters by ending year: 1996 denotes 1995–1996. Estimated wolf kills are based on kill rates, not merely carcasses discovered. Table 1's 0.26 column is the authors' adjustment reflecting the fraction of recorded kills in prime adult age classes (3–14); it is **not** the total kill estimate, an independent annual age census, or a confidence bound. Keep the rounded published values separate.

## Reconciliation

All nine published hunting figures exactly match `Late_Hunt`, and all nine winter labels match `Season`. They do **not** match `Harvest_Total`, which includes fall hunting. The difference equals `Fall_Hunt` in each year. For 1998–2004 that fall component is an imputed 359 elk annually. Accordingly, the primary descriptive comparison uses both columns from the paper. The existing broader harvest total appears only as an explicitly labelled alternative. Numerical equality does not independently settle geographic/methodological compatibility.

## Findings

Across 1996–2004 the paper reports **12,512 estimated wolf kills** and **11,653 hunting removals**. Wolf kills exceed the paper's hunting removals in each of 2000–2004, but are lower in 1996–1999. Against the existing broader fall-plus-late total, the crossover is 2001 rather than 2000. This demonstrates why the harvest definition matters.

The adjusted 0.26 wolf-kill figures remain below the published hunting removals in every year. This reflects the paper's adjustment assumptions; it does not establish a causal ranking from our time series. Wolves and hunters remove different age classes, so total headcounts alone do not establish which has the larger effect on population growth. No year-specific wolf-kill intervals are provided in Table 1; none were invented. No values were extrapolated outside 1996–2004.

## Deliverables and reproduction

- `eberhardt_2007_table1.csv`: source transcription, separate total/adjusted columns and provenance.
- `q6_removals_reconciliation.csv`: year/season check, existing late/fall/total harvest, ratios and drawbacks.
- `q6_removals.png`: descriptive comparison.
- `q6_removals.ipynb`: viewable, reproducible notebook with embedded results.
- `validation.json`: transcription arithmetic and preservation checks.

Run from repository root: `.venv/bin/python 01_yellowstone_elk_wolves/supplements/q6_removals/build_q6.py`.

No existing raw data, candidate dataset or regression results are changed. The current descriptive comparison is also exported to reports/tables/q6_removals_comparison.csv. Other ecological provenance gaps and the full team comparison remain outstanding. The Q6 source-access handoff is now resolved; broad claims about causal or age-specific effects remain unsupported by this descriptive table.
