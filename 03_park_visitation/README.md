# Part 3 · Park visitation

**Status:** in progress. The analysis will be added here.

Use the same layout as the other parts:

```text
03_park_visitation/
├── data/raw/            visitation files as downloaded (NPS visitor use statistics)
├── data/processed/
├── scripts/
├── notebooks/           number new notebooks from 13 so numbers stay unique across the project
└── reports/figures/, reports/tables/
```

## Inputs from other parts

Monthly mean air temperature for the park is built in Part 2:
`../02_vegetation_snow_river/data/processed/monthly_temperature.csv`

Read it with a path relative to this folder, for example:

```python
from pathlib import Path
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()   # this folder
temp = pd.read_csv(ROOT.parent / "02_vegetation_snow_river" / "data" / "processed" / "monthly_temperature.csv")
```
