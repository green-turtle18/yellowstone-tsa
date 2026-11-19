import os
os.environ.setdefault('MPL_IGNORE_SYSTEM_FONTS','1')
os.environ.setdefault('MPLCONFIGDIR','/tmp/yellowstone-mpl')
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import unittest
import numpy as np
import pandas as pd
from analysis import first_passage, gbm_sim, features, load_data, segment_search, GrowthStateModel, real_mask

class AnalysisTests(unittest.TestCase):
    def test_zero_drift_reflection_formula(self):
        from scipy.stats import norm
        actual=first_passage(0,.2,8000,4000,10)
        self.assertAlmostEqual(float(actual),2*norm.cdf(-np.log(2)/(.2*np.sqrt(10))),12)
    def test_probability_boundaries_and_monotonicity(self):
        self.assertEqual(float(first_passage(-.02,.2,4000,4000,10)),1)
        p=[float(first_passage(-.02,.2,8000,4000,t)) for t in [10,25,50]]
        self.assertTrue(0<=p[0]<=p[1]<=p[2]<=1)
    def test_bridge_matches_continuous_formula(self):
        annual,bridge=gbm_sim(-.02,.2,8000,4000,25,np.random.default_rng(12),paths=40000)
        target=float(first_passage(-.02,.2,8000,4000,25))
        self.assertLessEqual(annual,bridge)
        self.assertLess(abs(bridge-target),.015)
    def test_future_changes_do_not_change_training_transforms(self):
        d=load_data();_,x,a=features(d,cutoff=2010)
        altered=d.copy();altered.loc[altered.index>=2010,['NDVI','Precip_Annual','PDSI_Annual']]*=100
        _,z,b=features(altered,cutoff=2010)
        pd.testing.assert_frame_equal(x.loc[:2010],z.loc[:2010])
        pd.testing.assert_frame_equal(a,b)
    def test_exact_break_recovery(self):
        y=pd.Series(np.r_[np.zeros(10),np.ones(10)*3],index=range(2000,2020))
        out=segment_search(y,max_breaks=1)
        self.assertEqual(out.iloc[1].break_years,'2010')
        self.assertAlmostEqual(out.iloc[1].RSS,0)
    def test_state_covariates_affect_next_transition(self):
        z=pd.DataFrame({'z':[10.,20.,30.]})
        m=GrowthStateModel(pd.Series([1.,2.,3.]),z)
        m.update(np.array([.1,2.,.3,.4]))
        np.testing.assert_allclose(m.ssm['state_intercept'],[[40.1,60.1,.1]])
        self.assertAlmostEqual(m.ssm['state_cov',0,0],.3)
    def test_screening_adjustment_uses_number_of_tests(self):
        table=pd.read_csv(Path(__file__).resolve().parents[1]/'reports/tables/q1_coefficients.csv')
        screen=table[table.model.eq(table.term)]
        self.assertEqual(len(screen),7)
        np.testing.assert_allclose(screen.p_bonferroni_screen,np.minimum(1,screen.p*7))
    def test_provenance_and_real_transition_mask(self):
        d=load_data();self.assertEqual(d.loc[2018,'Elk_Count'],7579)
        self.assertEqual(d.loc[2019,'Elk_Count_imputed'],0)
        self.assertEqual(d.loc[2014,'Wolf_Northern_imputed'],0)
        self.assertFalse(real_mask(d,True).loc[2020])
        self.assertFalse(real_mask(d,True).loc[2021])
        self.assertEqual(d.loc[2023,'Elk_Count'],5976)

if __name__=='__main__':unittest.main()
