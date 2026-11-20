# Part 5 · Synthesis

The Yellowstone–Isle Royale population time-series comparison is complete for the supplied data. The broader synthesis of Parts 2 and 3 remains separate work.

- [Comparison report and drawbacks](report/COMPARISON.md)
- [Main comparison table](reports/tables/native_windows_comparison.csv)
- [Common-window and observed-input results](reports/tables/comparison_summary.csv)
- [Forecasts scored on identical years](reports/tables/matched_calendar_forecast_scores.csv)
- [Wolf-effect graph](reports/figures/wolf_effect_comparison.png)
- [Forecast graph](reports/figures/forecast_comparison.png)

From the repository root:

```sh
python 05_synthesis/scripts/build_comparison.py
python -m unittest discover -s 05_synthesis/tests -v
```

The script imports Part 4's unchanged shared specification. It does not overwrite source data or Part 4's results. Part 1's original change-in-wolves analysis remains available and addresses a different predictor. The current shared comparison uses lagged wolf levels.
