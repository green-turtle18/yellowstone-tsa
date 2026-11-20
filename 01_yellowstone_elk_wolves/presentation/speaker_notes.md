## 1. Do wolves help explain elk population change?

OPEN: We are testing whether wolves add information about elk changes, rather than assuming that every decline after reintroduction was caused by wolves.
EXPLAIN: Annual observational data contain several competing influences. Surveys are counts, not complete censuses. The 42 rows do not mean 42 equally comparable direct observations.
DATA CAVEAT: Whole-herd coverage in 2020–2021, some historical estimates, wolf/elk geography and climate metadata remain unresolved. Recovered wolf counts for 1996–2000 form a separate scenario.
TRANSITION: First define the outcome and the competing models. Sources: reports/CONCLUSIONS.md and HANDOFF.md.

## 2. Models considered: growth, drivers and memory

OPEN: We model proportional annual change, not just the raw number of elk.
EXAMPLE: A fall from 10,000 to 9,000 gives log(0.9) = −0.1054, which is an exact 10% decline. A preceding increase of ten wolves makes x equal to one.
MODELS: We compare drift, single-driver models and a full model. The full driver set includes lagged bison log change, NDVI, precipitation, PDSI, harvest rate and winter severity. Timing and transformation rules differ by variable.
ERROR MODELS: AR(p) uses previous values, MA(q) uses previous innovations, and ARMA combines both. In regression-with-ARMA-errors notation, u_t = sum(phi_i u_(t-i)) + epsilon_t + sum(theta_j epsilon_(t-j)). Primary driver estimates use white-noise errors, with dynamic-error robustness checks including MA(2). EDA compares candidate ARMA orders.
CHECKS: ADF tests a unit-root null; KPSS tests stationarity. AIC/BIC penalise complexity. Ljung–Box checks residual autocorrelation and ARCH LM checks conditional variance patterns. Forecast transformations are learned within each training window. Source: scripts/analysis.py, q1_stationarity.csv and q1_diagnostics.csv.

## 3. The wolf estimate is negative but uncertain

OPEN: The point estimate is negative, but its uncertainty is central to the conclusion.
EXAMPLE: For a ten-wolf increase in the preceding annual change, the model predicts 0.0305 lower log elk growth. exp(−0.0305) is about 0.970, a roughly 3% lower prediction relative to the same model without that predictor increment. This is not a count of animals killed.
INTERPRET: The confidence interval crosses zero and p is 0.120. The full model also does not establish an independent wolf association. Small samples, survey noise and correlated drivers limit power.
VIVA: A p-value is calculated under the null; it is not the probability that wolves have no effect. Seven single-driver screens also have Bonferroni adjustments.
TRANSITION: Association is one question. The next asks whether past wolves improve prediction beyond elk history. Source: q1_coefficients.csv.

## 4. Granger causality: does wolf history help?

OPEN: We first predict elk growth from its own history. Then we ask whether adding wolf history helps.
MODEL: v is contemporary scaled wolf change, and the VAR supplies the one-year lag. Thus v_(t−1) is the same preceding wolf-change predictor used in the driver model. In the first equation c tests wolves to elk; in the second e tests elk to wolves.
RESULTS: VAR(1) p-values are 0.176 and 0.797. The prespecified one-lag model has 28 fitted observations. VAR(2) sensitivity also does not reject either direction at 5%. Both AIC and BIC prefer zero lags among those considered, which weakens support for a feedback interpretation.
CAVEAT: Omitted weather, observation changes and limited power can affect these tests. This is predictive information, not a controlled ecological intervention.
TRANSITION: The forecast test asks whether any of this improves actual held-out prediction. Sources: q2_granger.csv and q2_lag_selection.csv.

## 5. Forecast gains are small on held-out years

OPEN: A useful model should beat a simple forecast, not merely fit the historical record.
EQUATIONS: Drift forecast Nhat_t = N_(t−1) exp(mean training log growth). MAE = mean(abs(actual − forecast)). Gain = 100 × (1 − model MAE / drift MAE).
DESIGN: Train up to t−1 and predict t. Eligible years are 2011–2013, 2017–2019 and 2023–2025. Target and origin counts must meet the scoring rules. Avoid future interpolation and full-sample transformation selection.
RESULT: Primary MAEs are 1003.8, 986.4 and 1402.1 for drift, wolf-only and full conditional. The recovered-wolf scenario gives 983.1 and 1302.1 for the two driver models.
CAVEAT: Nine years are a small retrospective evaluation. Predictor publication dates are unverified, so do not claim established real-time forecast skill or statistically significant improvement. Sources: q3_scores.csv and forecast_sensitivity.csv.

## 6. Winter interactions and structural changes

OPEN: Wolves could matter differently in severe winters. An interaction allows the wolf slope to vary with winter conditions.
EQUATION: The wolf slope is β + δs. The displayed interaction equation is schematic; the fitted model includes its specified controls. p=0.990 gives no evidence of a changing slope in this specification. Winter exposure windows may extend beyond some surveys. This does not distinguish additive from compensatory mortality.
BREAKS: The growth-mean search uses exact segmentation, minimum segment lengths, BIC and the zero-break option. It selects zero breaks. A separate continuous piecewise-linear trend search has lowest RSS at 2014. The hinge term changes slope without forcing a discontinuous jump.
CAVEAT: This is not a formal Bai–Perron confidence set or causal attribution to an event. Sources: q4_interaction.csv, q5_mean_breaks.csv and q5_trend_breaks.csv.

## 7. State-space model: counts contain survey noise

OPEN: The observed count mixes animal dynamics with the survey process. A state-space model explicitly separates those sources of variation under its assumptions.
NOTATION: x is the latent log abundance index, z is the aligned driver vector, eta is process noise and epsilon is observation noise. The symbol x here is not the wolf predictor on earlier slides.
EXAMPLE: If a survey suddenly misses more elk, a model without observation error would force the full drop into population dynamics. This model can distribute it between process and observation variation.
KALMAN: A noisy observation gets less weight than a precise one. Filtering uses information through that year. Smoothing uses later data too and is not a real-time forecast.
LIMIT: Random-noise separation does not identify unknown sightability, changing area coverage or systematic measurement bias. The fitted state model uses 33 observed counts on a 40-year grid. Source: r_variance_components.csv and analysis.py.

## 8. Hunting definitions change the removals comparison

OPEN: This is a descriptive comparison of estimated removals, not a direct test of which mechanism matters more for population growth.
SOURCE: Eberhardt et al. (2007), Table 1, printed page 598, DOI 10.2193/2005-770. The published hunting values match late hunt in all nine years. The broader project harvest series adds fall hunting, including estimated fall components for 1998–2004.
EXPLAIN: That definition changes the crossover from 2000 to 2001. Neither comparison supplies the age-specific reproductive impact of the removals.
CAVEATS: Annual wolf-kill confidence intervals are unavailable in the source table. The separate 26% adjustment concerns prime adult classes and is not total kills. Additive mortality increases deaths; compensatory mortality partly replaces other deaths. These totals cannot settle that distinction. Source: q6_removals_comparison.csv.

## 9. Viability models describe uncertain scenarios

OPEN: These models ask what paths are possible if the fitted dynamics continue. They are scenarios, not management forecasts.
GBM: μ is average log growth, σ is volatility, and B is Brownian motion. Estimates are μ=−0.0157 and σ=0.1790 from 27 eligible adjacent transitions. The population-scale drift would be μ + σ²/2.
GOMPERTZ: Density dependence can make log abundance return toward an equilibrium when 0<φ<1. Here φ=0.9973 and bootstrap LR p=0.986 provide little support over a random walk.
GRAPH: Annual checks miss crossings between years. A count may fall below 4,000 and recover before year ten, so first passage differs from endpoint probability. Brownian-bridge simulation checks the continuous result.
UNCERTAINTY: The 6.9%–78.7% interval is parameter uncertainty conditional on GBM, not all ecological or survey uncertainty. Future interventions and systematic bias are omitted. Source: q7_parameters.csv and q7_threshold_probabilities.csv.

## 10. Isle Royale provides a comparison, not a causal test

OPEN: We rerun both systems with the same shared specification, rather than comparing coefficients from different models.
DIFFERENCE: This model uses lagged wolf levels and prey density. The original Yellowstone headline uses lagged wolf changes. The comparison VAR uses prey and wolf log growth, whereas the original Yellowstone VAR uses prey log growth and scaled wolf-number changes. Thus their p-values are not interchangeable.
RESULT: On identical 22 test years, MAPE gain is −5.31% in Yellowstone and +8.21% in Isle Royale. Common-window wolf-to-prey Granger p-values are 0.530 and 0.009. The strict observed-input sensitivity has only seven common forecast years.
CLOSE: The Yellowstone data do not establish a clear independent wolf effect, and the forecast gain in the original specification is small. Isle Royale provides clearer predictive evidence under shared models. This neither disproves wolf biology in Yellowstone nor proves a causal difference between ecosystems.
LIMITS: Reconstructed moose counts, survey timing, geography and ecological regimes differ. Remaining kill-rate observations are unavailable. The two systems’ viability probabilities refer to different events and should not be directly ranked. Sources: 05_synthesis/report/COMPARISON.md and its tables.