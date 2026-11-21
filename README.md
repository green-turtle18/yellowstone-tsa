# Yellowstone Trophic Cascade: A Time-Series Analysis

MATH F428 Time Series Analysis · BITS Pilani, K K Birla Goa Campus

Ashwath Chandramouli (2024ADPS0853G) · Leora Modi (2023B4AD0866G) · Nitin Sureshkumar (2024ADPS0881G) · Tanishk Milind Tasgaonkar (2024ADPS0874G)

**Final report: [`Final_Report.pdf`](Final_Report.pdf)** (LaTeX source and figures in [`report/`](report/))

## The question

Gray wolves were reintroduced to Yellowstone in 1995. The classic story is a **top-down trophic cascade**: wolves cut the northern elk herd, browsing pressure eased, and riverside willows and aspens recovered. Many ecologists say this is too simple, and that **bottom-up and competing factors** also drove the elk decline and shaped the vegetation: drought, hard winters, hunting outside the park, competition from a growing bison herd, and stream water.

We use time-series methods to test what the data can and cannot support:

1. Do wolves carry predictive information for elk numbers beyond the elk's own past, climate, hunting and bison? (Part 1)
2. Did riverside vegetation get greener than nearby slopes after 1995, and does it follow water, snowmelt or elk? How have snowpack and river timing changed? (Part 2)
3. Did wolves bring tourists, and is climate changing when people visit? (Part 3)
4. In a simpler system with no hunting and no bison (Isle Royale), do the same methods find a wolf effect on prey, and how does it compare with Yellowstone under one shared model? (Part 4)

> **Scope.** Time-series models can show whether a variable helps *predict* another (Granger causality, ARIMAX) or whether a series changed at a known date (intervention models, break tests). On their own they cannot prove *causation*. With 30–60 annual observations per series, results are indicative, and each part reports them with that caveat.

## How the repository is organised

```text
yellowstone-tsa/
├── Final_Report.pdf               The final report (all four parts)
├── report/                        LaTeX source of the report and its figures
├── 00_midsem/                     Mid-semester submission, kept as it was (superseded by Part 1)
├── 01_yellowstone_elk_wolves/     Part 1 · Elk, wolves, hunting, bison, winter severity
├── 02_vegetation_snow_river/      Part 2 · Riverside vegetation (NDVI), snowpack, Yellowstone River flow
├── 03_park_visitation/            Part 3 · Park visitation
├── 04_isle_royale/                Part 4 · Isle Royale wolves and moose
│   └── comparison/                Yellowstone vs Isle Royale under one shared model
├── requirements.txt               Python packages for every part
└── README.md                      This file
```

Each part folder is self-contained and has its own README. Inside each, the layout is the same:

| Folder | What it holds |
|---|---|
| `data/raw/` | Source files exactly as downloaded. Never edited by hand. |
| `data/processed/` | Datasets built from `raw/` by the scripts or notebooks. |
| `scripts/` | Python scripts that build the processed data or hold shared settings. |
| `notebooks/` | The analysis, numbered in the order to run them. |
| `reports/figures/`, `reports/tables/` | Outputs written by the notebooks. |

Notebook numbers are unique across the whole project: **01–05** Part 1, **07, 11–12** Part 2 (run 07 → 12 → 11), **13–14** Part 3, **08–10** Part 4.

## How the parts connect

Most of each part stands alone. These are the only files one part takes from another:

| File | Made in | Used by |
|---|---|---|
| `data/processed/yellowstone_master_ts_flagged.csv` (corrected elk, wolf, bison counts) | Part 1 | Part 2 (notebook 11), comparison |
| `data/processed/winter_severity_index.csv` (three SNOTEL stations) | Part 2 | Part 1 (copy in its own `data/processed/`) |
| `data/processed/monthly_temperature.csv` | Part 2 | Part 3 |
| `scripts/tsa_spec.py` (shared model settings) | Part 4 | comparison, Part 1 |

## How to run

```sh
pip install -r requirements.txt
```

Then open a part's `notebooks/` folder in Jupyter (or Google Colab) and run its notebooks in number order. Each part's README gives any extra steps. The comparison is rebuilt from the repository root with `python 04_isle_royale/comparison/scripts/build_comparison.py`.

## Data sources (summary)

Elk counts: Northern Yellowstone Cooperative Wildlife Working Group and Montana FWP. Wolves: NPS Yellowstone Wolf Project. Bison: NPS bison status reports. Snow and temperature: NRCS SNOTEL. River flow: USGS gauge 06191500 (Yellowstone River at Corwin Springs). Vegetation: Landsat NDVI via Climate Engine. Visitation: NPS visitor use statistics. Isle Royale: Wolves and Moose of Isle Royale project and NPS. Full citations are in each part's README and notebooks.

## Team

| Part | Folder | Owner |
|---|---|---|
| 1 | `01_yellowstone_elk_wolves/` | Ashwath Chandramouli |
| 2 | `02_vegetation_snow_river/` | Leora Modi |
| 3 | `03_park_visitation/` | Nitin Sureshkumar |
| 4 | `04_isle_royale/` | Tanishk Milind Tasgaonkar |
