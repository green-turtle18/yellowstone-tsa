# Complete Yellowstone–Isle Royale comparison and update presentation

## Summary
Completes the population time-series comparison using Person 4's shared specification, with native-window replication, a common 1984–2015 window, and an observed-input sensitivity analysis. Original datasets and Person 4's analysis code remain unchanged.

- Reproduces the supplied Isle Royale comparison column at its reported precision.
- Scores both systems on identical calendar years for the common-window forecast comparison.
- Keeps the original Yellowstone change-in-wolves results distinct from the comparison's lagged-wolf-level models.
- Adds comparison tables, confidence-interval and forecast graphs, provenance hashes, and five comparison tests.
- Updates conclusions, handoff notes and the ten-slide presentation, with model equations, a dedicated Granger-causality explanation, presenter notes and four editable charts.
- Aligns the synthesis forecast graph with the matched-year headline results and documents the two per-SD scaling conventions.
- Extends the rebuild to regenerate the comparison, validate slide values and package links, and refresh handoff archives.
- Removes obsolete notebook-cache entries from handoff packaging and corrects old relocation instructions.

## Main result
Across the same 22 test years, wolf-only forecast MAPE improves by 8.2% over drift in Isle Royale and worsens by 5.3% in Yellowstone. The common-window VAR(1) wolf-to-prey p-values are 0.009 and 0.530, respectively. These are predictive associations, not evidence of a causal difference between ecosystems.

## Validation
Run from the repository root:

```sh
python 01_yellowstone_elk_wolves/scripts/run_all.py
```

The pipeline executes five Yellowstone notebooks, runs ten Yellowstone tests and five comparison tests, checks the four slide charts against source tables, checks PPTX package links, and rebuilds handoff archives. Source data and the shared Isle Royale specification are unchanged.

## Remaining limitations
- Visual inspection of the final layout in PowerPoint remains necessary; native rendering was unavailable in this environment.
- The strict sensitivity has only seven common forecast years.
- Historical reconstructed counts, survey coverage and timing differences, and unverified predictor publication dates remain documented.
- Isle Royale kill-rate observations are missing; no direct kill-rate comparison is claimed.
- The broader synthesis of vegetation and visitation results remains separate work.
