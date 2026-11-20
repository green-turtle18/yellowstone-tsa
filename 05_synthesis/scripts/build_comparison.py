"""Reproducible comparison using Person 4's unchanged shared specification."""
from pathlib import Path
import sys, json, hashlib, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'05_synthesis'; TABLES=OUT/'reports/tables'
sys.path.insert(0,str(ROOT/'04_isle_royale/scripts'))
import tsa_spec as spec
YS=ROOT/'01_yellowstone_elk_wolves'
paths=[YS/'data/processed/yellowstone_master_ts_flagged.csv',ROOT/'04_isle_royale/data/processed/isle_royale_annual.csv',ROOT/'04_isle_royale/scripts/tsa_spec.py']
y=pd.read_csv(paths[0]).set_index('Year'); i=pd.read_csv(paths[1]).set_index('Year')
systems={'Yellowstone':(y.Elk_Count,y.Wolf_Northern,(y.Elk_Count_imputed.eq(0)&y.Elk_Count_coverage_unresolved.eq(0)),y.Wolf_Northern_imputed.eq(0)), 'Isle Royale':(i.Moose,i.Wolves,i.Moose_imputed.eq(0),i.Wolves_imputed.eq(0))}
rows=[]; effects_all=[]; scores_all=[]; granger_all=[]; growth_all=[]

def consecutive(s):
 assert s.index.is_unique and np.all(np.diff(s.index)==1),'Annual grid required'

def strict_forecast(p,w,valid,wvalid,test):
 # White-noise regressions permit nonadjacent eligible observations, but growth
 # is always formed on the intact calendar before selecting rows.
 g=spec.growth(p).rename('y'); x=spec.core_regressors(p,w)
 eligible=valid & valid.shift(1,fill_value=False) & wvalid.shift(1,fill_value=False)
 records=[]
 for t in test:
  if not eligible.loc[t]:continue
  train=eligible & (p.index<t)
  if train.sum()<10:continue
  record={'year':t,'actual':p.loc[t],'naive':p.loc[t-1],'drift':p.loc[t-1]*np.exp(g[train].mean())}
  for name,cols in [('ARIMAX wolves',['wolves']),('ARIMAX wolves + density',['wolves','density'])]:
   xt=x[cols].copy()
   if 'density' in cols:xt['density']=np.log(p).shift(1)-np.log(p).shift(1)[train].mean()
   fit,_=spec.fit_arimax(g[train],xt.loc[train],order=(0,0,0))
   record[name]=p.loc[t-1]*np.exp(fit.params['const']+(fit.params[cols]*xt.loc[t]).sum())
  records.append(record)
 return pd.DataFrame(records).set_index('year')

for scenario in ['native_windows','common_1984_2015','common_observed_only']:
 columns={}
 for name,(prey,wolves,valid,wvalid) in systems.items():
  print(f'Running {scenario}: {name}',flush=True)
  first,last=(1984,2025) if name=='Yellowstone' else (1959,2015)
  if scenario!='native_windows':first,last=1984,2015
  p=prey.loc[first:last];w=wolves.loc[first:last];v=valid.loc[first:last];wv=wvalid.loc[first:last]
  consecutive(p);consecutive(w)
  strict=scenario=='common_observed_only'
  arma,_,order=spec.identify_arma(spec.growth(p))
  if strict:order=(0,0)
  eligible=v & v.shift(1,fill_value=False) & wv.shift(1,fill_value=False)
  years=p.index[eligible] if strict else p.index
  fits,effects,diag=spec.run_core_models(p,w,years=years,order=(order[0],0,order[1]))
  for model,fit in list(fits.items()):
   if not fit.mle_retvals.get('converged',True):
    with warnings.catch_warnings():
     warnings.simplefilter('ignore')
     fits[model]=fit.model.fit(start_params=fit.params,method_kwargs={'method':'powell','maxiter':1000})
    fit=fits[model]
    diag.loc[model,'optimizer_retry']='Powell, same likelihood and specification'
    for k,val in spec.diagnose(fit).items():diag.loc[model,k]=val
   diag.loc[model,'optimizer_converged']=fit.mle_retvals.get('converged',True)
   if not fit.mle_retvals.get('converged',True):print(f'Optimizer warning: {scenario} {name} {model}',flush=True)
  effects=spec.effect_table(fits)
  effects_all.append(effects.assign(system=name,scenario=scenario,arma=str(order)))
  diag.to_csv(TABLES/f'{scenario}_{name.replace(" ","_")}_diagnostics.csv')
  arma.to_csv(TABLES/f'{scenario}_{name.replace(" ","_")}_arma.csv',index=False)
  V=spec.var_data(p,w)
  # No dropping interior years and treating them as consecutive VAR observations.
  consecutive(V)
  var=spec.fit_var(V) if not strict else None
  if var:
   granger_all.append(dict(system=name,scenario=scenario,**var['granger_table']))
  tests=list(p.index[-spec.FORECAST_TEST_YEARS:])
  fc=strict_forecast(p,w,v,wv,tests) if strict else spec.rolling_forecasts(p,w,tests,score_mask=v)
  scores=spec.forecast_scores(fc);scores_all.append(scores.rename_axis('model').reset_index().assign(system=name,scenario=scenario))
  fc.to_csv(TABLES/f'{scenario}_{name.replace(" ","_")}_forecasts.csv')
  for model in scores.index:
   ok=fc[model].notna();scores.loc[model,'years']=','.join(map(str,fc.index[ok]))
  scores.to_csv(TABLES/f'{scenario}_{name.replace(" ","_")}_scores.csv')
  g=spec.growth(p);g=g[eligible] if strict else g.dropna()
  growth_all.append(dict(system=name,scenario=scenario,n=len(g),drift=100*g.mean(),volatility=100*g.std()))
  e=effects.set_index(['model','term']).loc[('wolves + density','wolves')]
  lagw=w.shift(1).loc[years].dropna(); sd=lagw.std()
  r=dict(scenario=scenario,system=name,first=first,last=last,n=int(e['n']),arma=str(order),beta=100*e.beta,low=e.pct_CI_low,high=e.pct_CI_high,p=e.p,per_sd=100*e.beta*sd/10,sd_low=e.pct_CI_low*sd/10,sd_high=e.pct_CI_high*sd/10,wolf_sd=sd,forecast_gain=scores.loc['ARIMAX wolves','MAPE gain over drift %'],forecast_n=int(scores.loc['ARIMAX wolves','years scored']),granger_wolf_p=var['granger_table']['wolves -> prey p'] if var else np.nan)
  rows.append(r)
  if not strict:
   col=spec.comparison_row(name,p,w,list(p.index),effects,var,scores)
   columns[name]=pd.Series(col)
   if scenario=='native_windows':
    colpath=TABLES/('YS_comparison_column.csv' if name=='Yellowstone' else 'IR_comparison_column_reproduced.csv')
    pd.Series(col,name=name).to_csv(colpath)
 if columns:pd.DataFrame(columns).to_csv(TABLES/f'{scenario}_comparison.csv')

summary=pd.DataFrame(rows);summary.to_csv(TABLES/'comparison_summary.csv',index=False)
pd.concat(effects_all).to_csv(TABLES/'model_effects.csv',index=False)
pd.concat(scores_all).to_csv(TABLES/'forecast_scores.csv',index=False)
pd.DataFrame(granger_all).to_csv(TABLES/'granger.csv',index=False)
pd.DataFrame(growth_all).to_csv(TABLES/'growth_parameters.csv',index=False)
# Score both systems on identical calendar years as an additional forecast check.
matched=[]
for scenario in ['common_1984_2015','common_observed_only']:
 frames={name:pd.read_csv(TABLES/f'{scenario}_{name.replace(" ","_")}_forecasts.csv',index_col='year') for name in systems}
 common=frames['Yellowstone'].index.intersection(frames['Isle Royale'].index)
 for name,fc in frames.items():
  sc=spec.forecast_scores(fc.loc[common,['actual','naive','drift','ARIMAX wolves','ARIMAX wolves + density']])
  matched.append(sc.rename_axis('model').reset_index().assign(system=name,scenario=scenario,years=','.join(map(str,common))))
matched=pd.concat(matched);matched.to_csv(TABLES/'matched_calendar_forecast_scores.csv',index=False)
# Check that the imported workflow reproduces Person 4's supplied rounded results.
original=pd.read_csv(ROOT/'04_isle_royale/reports/tables/IR_comparison_column.csv',index_col=0).iloc[:,0]
reproduced=pd.read_csv(TABLES/'IR_comparison_column_reproduced.csv',index_col=0).iloc[:,0]
for key in reproduced.index:
 assert str(original.loc[key])==str(reproduced.loc[key]),(key,original.loc[key],reproduced.loc[key])

plt.rcParams.update({'font.size':11})
fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
for idx,(scenario,title) in enumerate([('native_windows','Original sample windows'),('common_1984_2015','Same calendar window: 1984–2015')]):
 d=summary[summary.scenario.eq(scenario)]
 for j,(_,r) in enumerate(d.iterrows()):
  axes[idx].errorbar(r.per_sd,j,xerr=[[r.per_sd-r.sd_low],[r.sd_high-r.per_sd]],fmt='o',capsize=5,color=['#193B32','#9B572B'][j])
 axes[idx].set(yticks=[0,1],yticklabels=d.system.tolist(),title=title,xlabel='Log-growth percentage points per 1 SD of lagged wolves')
 axes[idx].set_ylim(-.6,1.6)
 axes[idx].axvline(0,color='gray',linestyle='--');axes[idx].grid(axis='x',alpha=.2)
fig.suptitle('Wolf association controlling for prey density: 95% model intervals')
fig.savefig(OUT/'reports/figures/wolf_effect_comparison.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,4.5),layout='constrained')
for j,name in enumerate(systems):
 d=summary[summary.system.eq(name)]
 gains=[float(d[d.scenario.eq('native_windows')].forecast_gain.iloc[0])]+[float(matched[(matched.system==name)&(matched.scenario==scenario)&(matched.model=='ARIMAX wolves')]['MAPE gain over drift %'].iloc[0]) for scenario in ['common_1984_2015','common_observed_only']]
 ax.bar(np.arange(3)+(j-.5)*.35,gains,width=.35,label=name,color=['#193B32','#9B572B'][j])
ax.axhline(0,color='gray');ax.set(xticks=range(3),xticklabels=['Original windows\n23 / 26 scored years','1984–2015\n22 shared years','Observed-only\n7 shared years'],ylabel='MAPE improvement over drift (%)',title='Wolf-only forecasts: positive values indicate improvement');ax.legend()
fig.savefig(OUT/'reports/figures/forecast_comparison.png',dpi=180);plt.close(fig)

def table(d):
 lines=['| Sample / system | Wolf coefficient [95% CI] | p | Wolf → prey Granger p | Forecast MAPE gain | Scored years |','|---|---:|---:|---:|---:|---:|']
 for _,r in d.iterrows():
  gp='Not estimated' if pd.isna(r.granger_wolf_p) else f'{r.granger_wolf_p:.3f}'
  lines.append(f'| {r.scenario} / {r.system} | {r.beta:+.2f} [{r.low:+.2f}, {r.high:+.2f}] | {r.p:.3f} | {gp} | {r.forecast_gain:+.2f}% | {r.forecast_n} |')
 return '\n'.join(lines)
matched_lines=['| Sample | System | Shared years | MAPE gain over drift |','|---|---|---:|---:|']
for _,r in matched[matched.model.eq('ARIMAX wolves')].iterrows():
 matched_lines.append(f"| {r.scenario} | {r.system} | {int(r['years scored'])} | {r['MAPE gain over drift %']:+.2f}% |")
report='''# Yellowstone–Isle Royale comparison

The comparison is complete for the supplied datasets. We re-ran both systems with Person 4's unchanged `tsa_spec.py` rather than juxtaposing the earlier Yellowstone results with different predictors.

## Matched specifications and results

The coefficient below is for lagged wolf **levels**, controlling for lagged log prey abundance. Units are log-growth percentage points per ten wolves, not exact percentage changes in animal numbers. Yellowstone's original headline used changes in wolf numbers, so these results supplement rather than replace that analysis. Both native-window model selections choose white-noise errors (see exported ARMA tables).

'''+table(summary)+'''

## Identical forecast years

'''+'\n'.join(matched_lines)+'''
These scores restrict both systems to the same eligible calendar years within each scenario.

## Figures

![Wolf associations and model intervals](../reports/figures/wolf_effect_comparison.png)

![Forecast sensitivity](../reports/figures/forecast_comparison.png)

The original-window bars use each system's eligible years. The two common-window groups use identical calendar years, matching the identical-year table above.

## Interpretation

The native-window Isle Royale analysis reproduces Person 4's supplied table exactly at its reported precision. Its density-adjusted wolf association is negative and marginally significant, and VAR(1) detects wolf-to-prey predictive information. Those results alone do not establish a stronger ecological effect than in Yellowstone: sample periods, populations, measurement practices and wolf histories differ. The common-window results and the observed-only sensitivity above show how conclusions depend on those choices. A difference between significant and non-significant p-values is not itself a significant difference between systems.

The legacy shared-specification column rescales by the SD of all wolf levels in the window. The graph and comparison_summary.csv instead use lagged wolves on the fitted sample, so their per-SD values differ slightly from that legacy column. Both conventions are labelled here. The per-standard-deviation graph rescales wolf coefficients using the lagged wolf series on each fitted sample. It reports model intervals, not a causal comparison or an area-adjusted predator-density effect. Forecast gains compare each model with drift on its own eligible years. Animal-count MAE is not comparable in scale between elk and moose, so MAPE gain is used here. Exact scored years and full diagnostics accompany the tables.

## Limitations and drawbacks

| Issue | Treatment / remaining drawback |
|---|---|
| Different original windows | Yellowstone 1984–2025, Isle Royale 1959–2015. Also rerun both on 1984–2015. These windows still mix ecological regimes. |
| Imputed Yellowstone inputs | Shared-specification replication includes filled training data. Separately exclude transitions with estimated/unresolved prey endpoints and imputed lagged wolves from the observed-only sensitivity. This reduces sample size and may introduce selection effects. |
| Calendar gaps | Form differences on intact annual grids. Full-data VAR uses contiguous years only. Do not fit a gap-compressed VAR in the observed-only sensitivity. |
| Forecast eligibility | Native replication excludes invalid targets. Strict sensitivity additionally requires valid origin counts, filters training transitions and excludes imputed lagged wolves. It uses fixed white-noise errors for both systems. Publication availability remains unverified. |
| Count and timing differences | Yellowstone northern wolf counts are December counts, whereas elk counts vary across winter. Shared lag-one convention does not make exposure windows identical to Isle Royale winter counts. |
| Reconstructed moose series | Person 4 flags the historical project series as reconstructed; its non-imputed flag does not imply a raw aerial count. Observed-only filtering cannot eliminate that difference. |
| Wolf regime and geography | Yellowstone includes pre-reintroduction zero wolves. Isle Royale's main sample ends in 2015 and excludes the later restoration period. Per-SD scaling does not harmonise park area or survey geography. |
| Optimizer warnings | Convergence flags are exported for every core model. Fits with optimizer warnings are retried using Powell on the same likelihood, without changing the shared module. The native Isle Royale density-only model and observed-only Yellowstone density-adjusted model required retries. The headline native Isle Royale wolf results reproduce the supplied table. Shared rolling forecast fits do not expose convergence diagnostics. |
| Sparse data and model uncertainty | Wald intervals and multiple exploratory tests require caution. No formal between-system causal-effect difference is asserted. |
| Viability | Yellowstone prey-count threshold scenarios and Isle Royale stochastic wolf-extinction simulations concern different species, thresholds and models. Their probabilities must not be ranked against each other. Comparable log-prey drift and volatility are exported separately. |
| Kill-rate data | Isle Royale's kill-rate template remains unfilled. A direct empirical cross-system kill-rate comparison is unavailable and is outside the completed population time-series comparison. |

## Reproduce and provenance

Run `python 05_synthesis/scripts/build_comparison.py` from the repository root. The script preserves both source datasets and Person 4's code and outputs. It writes the Yellowstone handoff column, reproduced Isle Royale column, matched-window tables, diagnostics, forecasts, figures and input hashes. The supplied Isle Royale table is checked against the regenerated native-window column.

Sources: `01_yellowstone_elk_wolves/data/processed/yellowstone_master_ts_flagged.csv`; `04_isle_royale/data/processed/isle_royale_annual.csv`; `04_isle_royale/docs/model_settings.md`; `04_isle_royale/scripts/tsa_spec.py`; `04_isle_royale/reports/tables/IR_comparison_column.csv`.
'''
(OUT/'report/COMPARISON.md').write_text(report)
(OUT/'reports/validation.json').write_text(json.dumps({'status':'passed','spec_version':spec.SPEC_VERSION,'person4_table_reproduced':True,'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'scenarios':json.loads(summary.to_json(orient='records'))},indent=2,allow_nan=False))
print(summary.to_string(index=False))
