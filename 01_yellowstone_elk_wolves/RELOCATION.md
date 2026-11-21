# Repository layout and reproduction

The Yellowstone work lives in `01_yellowstone_elk_wolves/`. The comparison reads the unchanged Isle Royale dataset and shared model code in `04_isle_royale/`, and writes results to `04_isle_royale/comparison/`.

Run from a full repository checkout:

```sh
python 01_yellowstone_elk_wolves/scripts/run_all.py
```

The pipeline rebuilds Yellowstone outputs, executes its notebooks and tests, rebuilds and tests the comparison, updates the seven-slide presentation, and refreshes handoff archives. The Part 1 archive alone is not sufficient to rerun comparison stages; use the full checkout. Original input files are preserved. Temporary environments and caches are excluded from Git.
