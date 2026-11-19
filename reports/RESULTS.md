# Person 1 results — provisional, 19 November 2026

All seven questions and the observation-error extension have executable implementations. Q0 is only partly resolved: 2020–2021 whole-herd survey provenance, climate export metadata, and several historical values remain outstanding. Q6's descriptive wolf-kill comparison and the Isle Royale side require external inputs. See HANDOFF.md for precise requests.

## Findings from the current run

- **Q1:** Wolf-only coefficient -0.0305 log-growth per +10 wolves (95% CI -0.0690 to 0.0080; p=0.1200; n=40). Full-model coefficient -0.0273, p=0.4077. All screened variables, standard errors, CIs, adjusted p-values and diagnostics are exported. Approximate percentage effects are beta ×100; exact percentage changes are 100×(exp(beta)−1).
- **Q2:** VAR(1) wolves → elk p=0.1760; elk → wolves p=0.7971. Lag-2 sensitivity is reported. AIC favours lag 0, BIC favours lag 0. Retain the prespecified VAR(1), with disagreement explicit. No causal interpretation of the impulse response.
- **Q3:** On 9 common eligible years, wolf-only MAE is 986.4 elk versus drift 1003.8; relative gain 1.7%. This small conditional retrospective comparison is not evidence of deployable forecast skill. The full model's MAE is 1402.1.
- **Q4:** Wolf × winter interaction beta=-0.0003, p=0.9900. The sign alone cannot establish additive or compensatory predation.
- **Q5:** BIC selects 0 growth-mean breaks; the single continuous trend-break search has its minimum RSS at 2014. These are different hypotheses. A selected date does not identify wolves, drought, fire or hunting as the cause.
- **Q6:** Standardised wolf and hunting coefficients, incremental R², true partial R² and VIF are in `tables/q6_hunting_vs_wolves.csv`. The supplied harvest CSV has no wolf-kill column. No removals numbers were invented.
- **Q7:** From 27 verified adjacent annual transitions, log-growth drift is -0.0157 and volatility 0.1790. Filled-series drift is -0.0198; missing-year selection changes the estimate. Unconstrained Gompertz phi=0.9973; stable OU condition 0<phi<1 is True. Bootstrap LR p=0.9860. If phi is outside that interval, its simulated output is an AR(1) sensitivity, not a mean-reverting OU forecast.
- **R:** Process/observation uncertainty and smoothed latent counts are exported. The custom state model matches the growth equation; it does not resolve systematic sightability bias or spatial mismatch.

## What changed after the corrections (same implementation on both datasets)

| dataset | model | wolf_beta | wolf_p | n | drift_all_filled |
| --- | --- | --- | --- | --- | --- |
| before | wolf_only | -0.03957 | 0.04243 | 40 | -0.02385 |
| before | full | -0.03815 | 0.1392 | 40 | -0.02385 |
| after | wolf_only | -0.03053 | 0.12 | 40 | -0.01981 |
| after | full | -0.02734 | 0.4077 | 40 | -0.01981 |

This isolates data changes within the new method. Original saved notebook outputs are retained in `baseline/`; historical numbers from the brief are not treated as verified results. Method changes also matter: stationarity-driven harvest differencing, train-only scaling and station baselines, predefined forecast models, past-only exogenous fills, and stricter common-year scoring.

## Conditional prediction comparison

| model | MAE | RMSE | MAPE | n |
| --- | --- | --- | --- | --- |
| drift | 1004 | 1261 | 16.66 | 9 |
| full_conditional | 1402 | 2085 | 24.81 | 9 |
| naive | 1034 | 1245 | 17.54 | 9 |
| wolves_only | 986.4 | 1245 | 16.39 | 9 |

No confidence interval or p-value is asserted for the small MAE difference. Scoring excludes filled targets, filled prior counts and unresolved geographic coverage. Survey method differences remain among eligible observations. Full-model predictors include winter information observed after some survey dates. Outcomes are count-scale medians exp(predicted log count), not lognormal bias-corrected means.

## Interpretation against the literature

[MacNulty et al. (2016)](https://home.nps.gov/yell/learn/ys-24-1-the-challenge-of-understanding-northern-yellowstone-elk-dynamics-after-wolf-reintroduction.htm) emphasise changing survey detection and multiple drivers. That matches the limitations here; failure to reject a wolf coefficient does not establish zero biological effect. This reference is *Yellowstone Science*, not PLOS ONE as stated in the brief.

[Ripple & Beschta (2012)](https://www.sciencedirect.com/science/article/pii/S0006320711004046) report vegetation patterns consistent with a cascade. [Brice et al. (2022)](https://onlinelibrary.wiley.com/doi/10.1111/ele.13915) show how sampling design changes the strength of that evidence. [Hobbs et al. (2024)](https://esajournals.onlinelibrary.wiley.com/doi/10.1002/ecm.1598) find limited riparian recovery after carnivore restoration. Annual elk and coarse NDVI regressions cannot adjudicate these vegetation-specific claims: browsing, hydrology, height and spatially representative vegetation data are different outcomes.

## Boundaries on interpretation

The data have 42 rows, not 42 independent, directly comparable population measurements. Filled outcomes bias dynamics; real-only selection can also bias drift. Wolf totals cover northern-range packs, while whole-herd elk include migrants outside the park. Correctly flagging these limitations matters more than selecting a significant model. No result is proof of trophic causation, an extinction probability for true abundance, or a validated policy recommendation.
