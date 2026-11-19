"""Create the three analysis notebooks; existing notebooks are patched separately."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def md(s):return {'cell_type':'markdown','metadata':{},'source':s.splitlines(True)}
def code(s):return {'cell_type':'code','metadata':{},'source':s.splitlines(True),'execution_count':None,'outputs':[]}
setup='''from pathlib import Path
import sys
import pandas as pd
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
if str(ROOT / "scripts") not in sys.path: sys.path.insert(0, str(ROOT / "scripts"))
from analysis import *
pd.set_option("display.max_columns", 20)
'''
items=[('03_elk_drivers', 'Q1–Q4 and Q6: Elk drivers', 'drivers', [
('Q1: Every driver and full model','q1_coefficients'),('Q1: Stationarity before and after transformations','q1_stationarity'),
('Q1: Robustness checks','q1_robustness'),('Q1: Diagnostics','q1_q4_diagnostics'),('Q2: Lag choice','q2_lag_selection'),
('Q2: Both Granger directions, lags 1 and 2','q2_granger'),('Q3: Matched-year conditional prediction scores','q3_scores'),
('Q4: Winter × wolves','q4_interaction'),('Q6: Hunting vs wolves','q6_hunting_vs_wolves'),('Q6: Removals source still required','q6_removals_pending')],
'''These associations are provisional. The forecast evaluation is conditional retrospective prediction, not an operational forecast: harvest and full winter severity are not demonstrably available at the origin. Scoring excludes imputed targets and origins and unresolved survey coverage. Training uses observed elk transitions and past-only exogenous fills; transformations are re-estimated inside each origin. Q1 full-sample results deliberately retain flagged values for comparison with sensitivity checks. Seven screening tests use Bonferroni ×7, so the expected number of false positives under seven true nulls is 0.35 at 5%. A non-significant interaction cannot distinguish additive from compensatory mortality. Q6 uses level harvest rate as specified, even if its stationarity is uncertain; see Q1 for the differenced alternative. A coefficient sign does not prove the mortality mechanism.'''),
('04_breaks_state_space','Q5 and R: Breaks and noisy counts','breaks_state',[
('Q5: Mean-shift model comparison, including no break','q5_mean_breaks'),('Q5: Trend break search','q5_trend_breaks'),('Q5: CUSUM','q5_cusum'),
('R: Growth-state coefficients','r_state_coefficients'),('R: Observation and process error','r_variance_components'),('R: Q1 comparison','r_q1_comparison'),('R: Density-dependent measurement-error model','r_density_dependence')],
'''The break search is exact L2 dynamic programming with annual candidate boundaries and a five-year minimum segment, equivalent to the specified Dynp objective with jump=1. This is not a formal Bai–Perron significance test. BIC counts segment means, searched break dates and variance; break dates label the first year of the new segment. Searching over dates invalidates ordinary fixed-date p-values. Break coincidence cannot identify a cause. The custom Kalman model puts covariates into latent growth, matching the brief's equation; UnobservedComponents(exog=Z) would put them in the observation equation. Missing and unresolved-coverage counts are NaN on the annual grid. State bands condition on fitted parameters and exogenous fills; they do not include all parameter or data uncertainty. Check convergence and weak variance identification before interpreting.'''),
('05_elk_viability','Q7: Threshold-risk scenarios','viability',[
('GBM vs Gompertz threshold probabilities','q7_threshold_probabilities'),('Parameters and bootstrap likelihood-ratio comparison','q7_parameters'),('Gompertz growth regression','q7_gompertz_coefficients')],
'''These are model-conditioned scenarios for survey-count indices, not validated extinction or management-risk forecasts. Calibration uses adjacent non-imputed counts with verified coverage. N0 is the latest observed count, 7,226, which is an underestimate of true abundance. GBM first passage is continuous-time; annual-only simulation understates it, so a Brownian-bridge correction checks the formula. Gompertz probabilities use annual monitoring and should be compared to annual GBM simulations. The OU label is appropriate only when 0 < phi < 1; otherwise the fitted AR(1) is not a stable continuous OU. The random-walk null has nonstandard asymptotics, so LR inference uses a parametric bootstrap rather than a chi-square reference. The GBM intervals cover parameter sampling uncertainty under the fitted model, not survey bias, future interventions or structural changes.''')]
for name,title,func,tables,summary in items:
 cells=[md('# '+title+'\n\n**Provisional data:** read `reports/HANDOFF.md` before reporting conclusions. Implementation lives in `scripts/analysis.py`.'),code(setup),code(func+'()')]
 for heading,table in tables:cells +=[md('## '+heading),code(f'pd.read_csv(TABLE / "{table}.csv")')]
 cells +=[md('## Plain-English summary\n\n'+summary),code('print((ROOT / "reports/RESULTS.md").read_text())')]
 nb={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3'}},'nbformat':4,'nbformat_minor':4}
 (ROOT/'notebooks'/f'{name}.ipynb').write_text(json.dumps(nb,indent=1)+'\n')
