# Yellowstone Trophic Cascade: A Time-Series Analysis

MATH F428 Time Series Analysis · BITS Pilani, K K Birla Goa Campus

## The question

Gray wolves were reintroduced to Yellowstone in 1995. The classic story is a **top-down trophic cascade**: wolves cut the northern elk herd, browsing pressure eased, and riverside willows and aspens recovered. Many ecologists say this is too simple, and that **bottom-up and competing factors** also drove the elk decline and shaped the vegetation: drought, hard winters, hunting outside the park, competition from a growing bison herd, and stream water levels.

We use time-series methods to test what the data can and cannot support:

1. Do wolves carry predictive information for elk numbers beyond the elk's own past, climate, hunting and bison? (Part 01)
2. Did riverside vegetation get greener than nearby slopes after 1995, and does it track water or elk more closely? How have snowpack and river timing changed? (Part 02)
3. How does human use of the park (visitation) vary and connect to climate? (Part 03)
4. In a simpler system with no hunting and no bison (Isle Royale), do the same methods find a wolf effect on prey? (Part 04)
5. Putting it together: how do the Yellowstone and Isle Royale results compare? (Part 05)

> **Scope.** Time-series models can show whether a variable helps *predict* another (Granger causality, ARIMAX) or whether a series changed at a known date (intervention models, break tests). On their own they cannot prove *causation*. With 30–60 annual observations per series, results are indicative, and each part reports them with that caveat.

## How the repository is organised

Each part of the project has its own folder. Each folder is self-contained, with its own data, code, notebooks and outputs, and has its own README explaining what it contains and how to run it.

```text
yellowstone-tsa/
├── 00_midsem/                     Mid-semester submission, kept as it was (superseded by 01)
├── 01_yellowstone_elk_wolves/     Part 1 · Elk, wolves, hunting, bison, winter severity
├── 02_vegetation_snow_river/      Part 2 · Riverside vegetation (NDVI), snowpack, Lamar River flow
├── 03_park_visitation/            Part 3 · Park visitation
├── 04_isle_royale/                Part 4 · Isle Royale wolves and moose (comparison system)
├── 05_synthesis/                  Combined comparison, final report and slides
├── requirements.txt               Python packages for every part
└── README.md                      This file
```

Inside each part folder the layout is the same:

| Folder | What it holds |
|---|---|
| `data/raw/` | Source files exactly as downloaded. Never edited by hand. |
| `data/processed/` | Datasets built from `raw/` by the scripts or notebooks. |
| `scripts/` | Python scripts that build the processed data or hold shared settings. |
| `notebooks/` | The analysis, numbered in the order to run them. |
| `reports/figures/`, `reports/tables/` | Outputs written by the notebooks. |

Notebook numbers are unique across the whole project, so a number points to one notebook: **01–05** are in Part 1, **08–10** in Part 4, and **11–12** in Part 2.

## How the parts connect

Most of each part stands alone. These are the only files that one part takes from another:

| File | Made in | Used by |
|---|---|---|
| `data/processed/yellowstone_master_ts_flagged.csv` (corrected elk, wolf, bison master) | 01 | 02 (notebook 11) |
| `data/processed/winter_severity_index.csv` (snow depth and cold, three SNOTEL stations) | 02 | 01 (copy in its own `data/processed/`) |
| `data/processed/monthly_temperature.csv` | 02 | 03 |
| `scripts/tsa_spec.py` (shared model settings) | 04 | 01, for the comparison table |
| `reports/tables/IR_comparison_column.csv` and the Yellowstone column | 04 and 01 | 05 |

## How to run

```sh
pip install -r requirements.txt
```

Then open a part's `notebooks/` folder in Jupyter (or Google Colab) and run its notebooks in number order. Each part's README gives any extra steps, such as rebuilding processed data.

## Data sources (summary)

Elk counts: Northern Yellowstone Cooperative Wildlife Working Group and Montana FWP. Wolves: NPS Yellowstone Wolf Project. Bison: NPS bison status reports. Snow and temperature: NRCS SNOTEL. River flow: USGS gauge 06191500 (Yellowstone River at Corwin Springs). Vegetation: Landsat NDVI via Climate Engine. Isle Royale: Wolves and Moose of Isle Royale project and NPS. Full citations are in each part's README and notebooks.

## Team

| Part | Folder | Owner |
|---|---|---|
| 1 | `01_yellowstone_elk_wolves/` | Person 1 |
| 2 | `02_vegetation_snow_river/` | Person 2 |
| 3 | `03_park_visitation/` | Person 3 |
| 4 | `04_isle_royale/` | Person 4 |
| 5 | `05_synthesis/` | All |
