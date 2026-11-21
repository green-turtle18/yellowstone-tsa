# Yellowstone vs Isle Royale comparison

Runs Part 4's shared model settings (`../scripts/tsa_spec.py`, unchanged) on both systems, so the wolf effect on prey is estimated the same way in Yellowstone (elk) and on Isle Royale (moose): prey log growth on lagged wolf numbers, controlling for prey density, plus a VAR Granger test and forecasts scored on identical years.

- [Comparison report and drawbacks](report/COMPARISON.md)
- [Main comparison table](reports/tables/native_windows_comparison.csv)
- [Common-window (1984–2015) and observed-input results](reports/tables/comparison_summary.csv)
- [Forecasts scored on identical years](reports/tables/matched_calendar_forecast_scores.csv)
- [Wolf-effect graph](reports/figures/wolf_effect_comparison.png) · [Forecast graph](reports/figures/forecast_comparison.png)

From the repository root:

```sh
python 04_isle_royale/comparison/scripts/build_comparison.py
python -m unittest discover -s 04_isle_royale/comparison/tests -v
```

Inputs: `01_yellowstone_elk_wolves/data/processed/yellowstone_master_ts_flagged.csv` and `04_isle_royale/data/processed/isle_royale_annual.csv`. The script does not overwrite source data or Part 4's own results. Part 1's original change-in-wolves analysis addresses a different predictor; this comparison uses lagged wolf levels.
