import pandas as pd
import numpy as np

from pathlib import Path
import runpy
ROOT = Path(__file__).resolve().parents[1]
raw_path = str(ROOT / 'data/raw') + '/'
processed_path = str(ROOT / 'data/processed') + '/'

# 1. Timeline baseline (1984 - 2025)
df_master = pd.DataFrame({'Year': range(1984, 2026)})

# 2. Load raw CSVs
df_elk = pd.read_csv(raw_path + 'elk_count.csv')
df_wolves = pd.read_csv(raw_path + 'yellowstone_wolves_1995_2025.csv')
df_bison = pd.read_csv(raw_path + 'bison_count.csv')
df_ndvi = pd.read_csv(raw_path + 'Vegetation_summer_months.csv')
df_precip = pd.read_csv(raw_path + 'precipitation_std_year.csv')
df_pdsi = pd.read_csv(raw_path + 'drought_std_year.csv')

# 3. Standardize column names (Year + Variable)
df_elk = df_elk.rename(columns={df_elk.columns[0]: 'Year', df_elk.columns[1]: 'Elk_Count'})
df_wolves = df_wolves.rename(columns={df_wolves.columns[0]: 'Year', df_wolves.columns[1]: 'Wolf_Count'})
df_bison = df_bison.rename(columns={df_bison.columns[0]: 'Year', df_bison.columns[1]: 'Bison_Count'})
df_ndvi = df_ndvi.rename(columns={df_ndvi.columns[0]: 'Year', df_ndvi.columns[1]: 'NDVI'})
df_precip = df_precip.rename(columns={df_precip.columns[0]: 'Year', df_precip.columns[1]: 'Precip_Annual'})
df_pdsi = df_pdsi.rename(columns={df_pdsi.columns[0]: 'Year', df_pdsi.columns[1]: 'PDSI_Annual'})

# 4. Merge sequentially
for df in [df_elk, df_wolves, df_bison, df_ndvi, df_precip, df_pdsi]:
    df_master = df_master.merge(df[['Year', df.columns[1]]], on='Year', how='left')

# 5. Ecological adjustments & missing values
# Pre-1995 wolves were zero
df_master.loc[df_master['Year'] < 1995, 'Wolf_Count'] = 0

# Interpolate internal gaps, backward-fill leading gaps (1984-1985 elk), and forward-fill trailing endpoints (2025 climate)
for col in ['Elk_Count', 'Wolf_Count', 'Bison_Count', 'NDVI', 'Precip_Annual', 'PDSI_Annual']:
    df_master[col] = df_master[col].interpolate(method='linear').bfill().ffill()

# 6. Save final processed dataset
output_file = processed_path + 'yellowstone_master_ts_final.csv'
df_master.to_csv(output_file, index=False)
print(f"Dataset successfully created and cleaned at {output_file}")
# The canonical entry point also builds provenance and applies verified overrides.
runpy.run_path(str(ROOT / "scripts/build_master_flagged.py"), run_name="__main__")
