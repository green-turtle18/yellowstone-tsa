"""Generate report and Person 4 exchange table from actual outputs, not assumed results."""
from analysis import *
import platform
import json
import hashlib

def mdtable(d):
    d=d.copy()
    for c in d:
        if pd.api.types.is_float_dtype(d[c]):d[c]=d[c].map(lambda x:f'{x:.4g}' if pd.notna(x) else '—')
    return '| '+' | '.join(d.columns)+' |\n| '+' | '.join(['---']*len(d.columns))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in d.fillna('—').to_numpy())


def main():
    q=pd.read_csv(TABLE/'q1_coefficients.csv');g=pd.read_csv(TABLE/'q2_granger.csv');f=pd.read_csv(TABLE/'q3_scores.csv').set_index('model');v=pd.read_csv(TABLE/'q7_parameters.csv').iloc[0]
    w=q[(q.model=='d_wolves')&(q.term=='d_wolves')].iloc[0];wf=q[(q.model=='full')&(q.term=='d_wolves')].iloc[0]
    inter=pd.read_csv(TABLE/'q4_interaction.csv').query('term == "interaction"').iloc[0]
    breaks=pd.read_csv(TABLE/'q5_mean_breaks.csv');best=breaks.loc[breaks.BIC.idxmin()]
    trend=pd.read_csv(TABLE/'q5_trend_breaks.csv');tb=trend.loc[trend.RSS.idxmin(),'break_year']
    gain=100*(1-f.loc['wolves_only','MAE']/f.loc['drift','MAE'])
    comp=[]
    for label,path in [('before',ROOT/'reports/baseline/master_before_corrections.csv'),('after',None)]:
        d=load_data(path);y,x,_=features(d)
        for name,cols in [('wolf_only',['d_wolves']),('full',list(x))]:
            r,z=fit_arimax(y,x[cols]);comp.append(dict(dataset=label,model=name,wolf_beta=r.params.d_wolves,wolf_p=r.pvalues.d_wolves,n=len(z),drift_all_filled=y.mean()))
    comp=save(comp,'q0_before_after_same_method')
    text=f'''# Person 1 results — provisional, 19 November 2026

All seven questions and the observation-error extension have executable implementations. Q0 is only partly resolved: 2020–2021 whole-herd survey provenance, climate export metadata, and several historical values remain outstanding. Q6's descriptive wolf-kill comparison is complete; the full Isle Royale comparison still requires team inputs. See HANDOFF.md for precise requests.

## Findings from the current run

- **Q1:** Wolf-only coefficient {w.estimate:.4f} log-growth per +10 wolves (95% CI {w.ci_low:.4f} to {w.ci_high:.4f}; p={w.p:.4f}; n={int(w.n)}). Full-model coefficient {wf.estimate:.4f}, p={wf.p:.4f}. All screened variables, standard errors, CIs, adjusted p-values and diagnostics are exported. Approximate percentage effects are beta ×100; exact percentage changes are 100×(exp(beta)−1).
- **Q2:** VAR(1) wolves → elk p={g.iloc[0].p:.4f}; elk → wolves p={g.iloc[1].p:.4f}. Lag-2 sensitivity is reported. AIC favours lag {int(pd.read_csv(TABLE/'q2_lag_selection.csv').query('criterion == "aic"').sort_values('score').iloc[0].lag)}, BIC favours lag {int(pd.read_csv(TABLE/'q2_lag_selection.csv').query('criterion == "bic"').sort_values('score').iloc[0].lag)}. Retain the prespecified VAR(1), with disagreement explicit. No causal interpretation of the impulse response.
- **Q3:** On {int(f.loc['drift','n'])} common eligible years, wolf-only MAE is {f.loc['wolves_only','MAE']:.1f} elk versus drift {f.loc['drift','MAE']:.1f}; relative gain {gain:.1f}%. This small conditional retrospective comparison is not evidence of deployable forecast skill. The full model's MAE is {f.loc['full_conditional','MAE']:.1f}.
- **Q4:** Wolf × winter interaction beta={inter.estimate:.4f}, p={inter.p:.4f}. The sign alone cannot establish additive or compensatory predation.
- **Q5:** BIC selects {int(best.breaks)} growth-mean breaks; the single continuous trend-break search has its minimum RSS at {int(tb)}. These are different hypotheses. A selected date does not identify wolves, drought, fire or hunting as the cause.
- **Q6:** Standardised wolf and hunting coefficients, incremental R², true partial R² and VIF are in `tables/q6_hunting_vs_wolves.csv`. The descriptive comparison is complete in `../supplements/q6_removals/README.md`: Table 1 hunting removals match late hunt in all nine years; estimated wolf kills exceed that series from 2000, versus 2001 for existing fall-plus-late totals. Counts alone do not rank demographic effects.
- **Q7:** From {int(v.n)} verified adjacent annual transitions, log-growth drift is {v.mu:.4f} and volatility {v.sigma:.4f}. Filled-series drift is {v.mu_all_filled:.4f}; missing-year selection changes the estimate. Unconstrained Gompertz phi={v.phi:.4f}; stable OU condition 0<phi<1 is {bool(v.OU_stable)}. Bootstrap LR p={v.LR_bootstrap_p:.4f}. If phi is outside that interval, its simulated output is an AR(1) sensitivity, not a mean-reverting OU forecast.
- **R:** Process/observation uncertainty and smoothed latent counts are exported. The custom state model matches the growth equation; it does not resolve systematic sightability bias or spatial mismatch.

## What changed after the corrections (same implementation on both datasets)

{mdtable(comp)}

This isolates data changes within the new method. Original saved notebook outputs are retained in `baseline/`; historical numbers from the brief are not treated as verified results. Method changes also matter: stationarity-driven harvest differencing, train-only scaling and station baselines, predefined forecast models, past-only exogenous fills, and stricter common-year scoring.

## Conditional prediction comparison

{mdtable(f.reset_index()[['model','MAE','RMSE','MAPE','n']])}

No confidence interval or p-value is asserted for the small MAE difference. Scoring excludes filled targets, filled prior counts and unresolved geographic coverage. Survey method differences remain among eligible observations. Full-model predictors include winter information observed after some survey dates. Outcomes are count-scale medians exp(predicted log count), not lognormal bias-corrected means.

## Interpretation against the literature

[MacNulty et al. (2016)](https://home.nps.gov/yell/learn/ys-24-1-the-challenge-of-understanding-northern-yellowstone-elk-dynamics-after-wolf-reintroduction.htm) emphasise changing survey detection and multiple drivers. That matches the limitations here; failure to reject a wolf coefficient does not establish zero biological effect. This reference is *Yellowstone Science*, not PLOS ONE as stated in the brief.

[Ripple & Beschta (2012)](https://www.sciencedirect.com/science/article/pii/S0006320711004046) report vegetation patterns consistent with a cascade. [Brice et al. (2022)](https://onlinelibrary.wiley.com/doi/10.1111/ele.13915) show how sampling design changes the strength of that evidence. [Hobbs et al. (2024)](https://esajournals.onlinelibrary.wiley.com/doi/10.1002/ecm.1598) find limited riparian recovery after carnivore restoration. Annual elk and coarse NDVI regressions cannot adjudicate these vegetation-specific claims: browsing, hydrology, height and spatially representative vegetation data are different outcomes.

## Boundaries on interpretation

The data have 42 rows, not 42 independent, directly comparable population measurements. Filled outcomes bias dynamics; real-only selection can also bias drift. Wolf totals cover northern-range packs, while whole-herd elk include migrants outside the park. Correctly flagging these limitations matters more than selecting a significant model. No result is proof of trophic causation, an extinction probability for true abundance, or a validated policy recommendation.
'''
    (ROOT/'reports/RESULTS.md').write_text(text)
    exchange=[dict(metric='wolf_only_beta_per_10',Yellowstone=w.estimate,Isle_Royale=np.nan,specification='delta log prey ~ constant + lagged delta wolves / 10'),
        dict(metric='wolf_only_CI_low',Yellowstone=w.ci_low,Isle_Royale=np.nan,specification='ARIMA Gaussian 95% Wald CI'),
        dict(metric='wolf_only_CI_high',Yellowstone=w.ci_high,Isle_Royale=np.nan,specification='ARIMA Gaussian 95% Wald CI'),
        dict(metric='wolf_only_n',Yellowstone=w.n,Isle_Royale=np.nan,specification='full flagged sample; report real-only sensitivity'),
        dict(metric='Granger_wolf_to_prey_p',Yellowstone=g.iloc[0].p,Isle_Royale=np.nan,specification='VAR(1) contemporary delta log prey and delta wolves/10'),
        dict(metric='Granger_prey_to_wolf_p',Yellowstone=g.iloc[1].p,Isle_Royale=np.nan,specification='same VAR(1), reverse F-test'),
        dict(metric='MAE_gain_over_drift_percent',Yellowstone=gain,Isle_Royale=np.nan,specification='100*(1-wolf_MAE/drift_MAE), common real target/origin years'),
        dict(metric='GBM_log_drift',Yellowstone=v.mu,Isle_Royale=np.nan,specification='mean adjacent verified annual log changes'),
        dict(metric='GBM_volatility',Yellowstone=v.sigma,Isle_Royale=np.nan,specification='sample SD, ddof=1'),
        dict(metric='GBM_transition_n',Yellowstone=v.n,Isle_Royale=np.nan,specification='exclude any pair with imputed or unresolved-coverage count')]
    save(exchange,'person4_comparison')
    manifest={'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'statsmodels':sm.__version__,
        'seed':SEED,'data_sha256':hashlib.sha256((ROOT/'data/processed/yellowstone_master_ts_flagged.csv').read_bytes()).hexdigest(),
        'status':'provisional; see HANDOFF.md'}
    (ROOT/'reports/run_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
