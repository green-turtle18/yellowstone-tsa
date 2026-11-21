"""Evidence checks for matched scoring, calendar handling and source preservation."""
from pathlib import Path
import hashlib,json,unittest
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[3];T=ROOT/'04_isle_royale/comparison/reports/tables'

class ComparisonTests(unittest.TestCase):
 def test_inputs_match_recorded_hashes(self):
  manifest=json.loads((T.parent/'validation.json').read_text())
  for name,digest in manifest['input_sha256'].items():
   self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)
 def test_same_calendar_years_and_scores(self):
  scores=pd.read_csv(T/'matched_calendar_forecast_scores.csv')
  for scenario,group in scores.groupby('scenario'):
   self.assertEqual(group.years.nunique(),1)
   for _,row in group.iterrows():
    fc=pd.read_csv(T/f'{scenario}_{row.system.replace(" ","_")}_forecasts.csv',index_col='year')
    years=list(map(int,row.years.split(',')));fc=fc.loc[years]
    error=(fc[row.model]-fc.actual).abs()/fc.actual
    drift=(fc.drift-fc.actual).abs()/fc.actual
    self.assertEqual(len(years),row['years scored'])
    self.assertAlmostEqual(100*(1-error.mean()/drift.mean()),row['MAPE gain over drift %'],places=8)
 def test_strict_forecasts_have_valid_origins_and_targets(self):
  data=pd.read_csv(ROOT/'01_yellowstone_elk_wolves/data/processed/yellowstone_master_ts_flagged.csv',index_col='Year')
  fc=pd.read_csv(T/'common_observed_only_Yellowstone_forecasts.csv',index_col='year')
  for t in fc.index:
   for year in [t-1,t]:
    self.assertEqual(data.loc[year,'Elk_Count_imputed'],0)
    self.assertEqual(data.loc[year,'Elk_Count_coverage_unresolved'],0)
   self.assertEqual(data.loc[t-1,'Wolf_Northern_imputed'],0)
 def test_all_core_fits_converged(self):
  for p in T.glob('*_diagnostics.csv'):
   self.assertTrue(pd.read_csv(p).optimizer_converged.all(),str(p))
 def test_person4_reproduction(self):
  old=pd.read_csv(ROOT/'04_isle_royale/reports/tables/IR_comparison_column.csv',index_col=0).iloc[:,0]
  new=pd.read_csv(T/'IR_comparison_column_reproduced.csv',index_col=0).iloc[:,0]
  for key in new.index:self.assertEqual(str(old.loc[key]),str(new.loc[key]))
if __name__=='__main__':unittest.main()
