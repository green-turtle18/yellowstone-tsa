# Yellowstone conclusions

**Written conclusions for the current analysis — 20 November 2026.** These conclusions use the corrected, flagged Yellowstone master as the primary dataset. The recovered 1996–2000 northern wolf counts are a separate sensitivity scenario. The Yellowstone section is ready for inclusion in the project report; its evidential limitations remain explicit. Revise affected statements if the underlying data or model specifications change.

## Report-ready conclusions

### Drivers and feedback

The analysis does not establish a statistically clear independent relationship between lagged changes in northern wolf numbers and annual growth in the northern Yellowstone elk count. The wolf-only estimate is negative: a ten-wolf increase in the preceding annual change is associated with a 0.0305 reduction in annual log elk growth (95% confidence interval −0.0690 to 0.0080; p = 0.120; n = 40). The interval includes both a substantial negative association and a small positive association. In the full model, the corresponding estimate is −0.0273 (p = 0.408). These findings indicate uncertainty about the association under the chosen specifications, rather than demonstrating that wolves have no biological effect. [1]

The prespecified VAR(1) likewise provides no statistically significant evidence of predictive feedback in either direction: wolves to elk p = 0.176 and elk to wolves p = 0.797. Both AIC and BIC prefer zero lags within the tested lag range. This weak support for temporal dependence limits interpretation of the fitted feedback and impulse responses. Granger tests concern predictive information, not ecological causation. [2]

### Prediction and winter conditions

Adding the wolf predictor produces only a small forecasting improvement over drift. Across nine common eligible evaluation years, mean absolute error is 986.4 elk for the wolf-only model and 1,003.8 for drift, a gain of approximately 1.7%. The full conditional model performs worse, with an error of 1,402.1 elk. These conditional retrospective comparisons do not establish operational forecast skill: the evaluation sample is small, and availability of all predictors at the historical forecast origin has not been verified. [3]

Replacing the five interpolated northern wolf counts with published counts changes wolf-only error to 983.1 elk, while the full model's error falls to 1,302.1. The broad forecasting conclusion therefore survives this particular substitution: wolf-only improvement is small, and the full model still underperforms drift. This is a limited sensitivity result, not validation of every data value or every model conclusion. [4]

There is no statistical evidence of a wolf-by-winter interaction in the fitted specification (p = 0.990). This result does not distinguish additive from compensatory predation, especially because winter exposure windows are not fully aligned with individual survey dates. [5]

### Structural change and removals

BIC selects no breaks in the mean of annual log growth among the tested models. A separate continuous trend-break search has its lowest residual sum of squares at 2014. These results address different questions and are not contradictory: a preferred trend-break date is not evidence of a shift in mean annual growth, nor does it identify a particular ecological cause. [6]

The descriptive removals comparison is now complete for 1996–2004. Eberhardt et al. (2007), Table 1, reports 12,512 estimated wolf kills and 11,653 hunting removals over this period. All nine published hunting values match the project's late-hunt column. Estimated wolf kills exceed those published hunting values from 2000 onward; against the project's broader fall-plus-late totals, the crossover occurs in 2001. The latter totals include estimated fall components for 1998–2004. [7]

Neither these totals nor the regression establishes that one removal source has a greater effect on population growth. Wolves and hunters remove different age classes. The paper's separate 26% adjustment concerns prime adult age classes and must not be confused with total wolf kills. In the fitted joint standardised regression, neither wolf nor harvest coefficient is significant at 5% (p = 0.145 and 0.907 respectively). These results do not demonstrate that either removal mechanism is unimportant. [7, 8]

### Viability and observation error

The viability analysis should be interpreted as scenarios for a survey-count index, not estimates of extinction risk for the true population. Calibration using 27 eligible adjacent observed transitions gives mean annual log growth of −0.0157 and volatility of 0.1790. The Gompertz estimate is close to a random walk (phi = 0.9973), and the bootstrap likelihood-ratio result (p = 0.986) provides little support for the density-dependent alternative. [9]

For illustration, the fitted GBM gives a 38.7% probability of crossing below a count of 4,000 within ten years, starting from 7,226. Its bootstrap interval spans approximately 6.9%–78.7%, demonstrating substantial parameter uncertainty. This is a continuous-monitoring threshold-crossing probability, not the probability of being below 4,000 exactly ten years later. Annual-only simulations use a different monitoring convention. These scenarios omit future interventions, structural change and systematic survey bias; they are not management forecasts. [9]

The state-space extension separates estimated process variation from observation noise under its assumptions. It does not independently correct unknown sightability bias or differences in the areas covered by wolf and elk counts. The dataset's 42 annual rows must therefore not be treated as 42 fully comparable direct population measurements. Estimated values, unresolved whole-herd coverage in 2020–2021, changing survey methods and uncertain climate extraction metadata remain material limitations. [10, 11]

### Overall Yellowstone conclusion

The current annual series provides limited evidence that changes in wolf numbers alone explain or reliably predict changes in elk counts. The analysis quantifies uncertainty and shows that data definitions can affect interpretation, particularly for hunting removals and long-term risk scenarios. It neither disproves wolf effects nor isolates the causes of elk population change. Conclusions about trophic cascades would require evidence on vegetation, browsing and other ecological mechanisms beyond the annual series analysed here.

## Cross-system comparison — to be completed

**No Yellowstone–Isle Royale conclusion is asserted yet.** Once the matching Isle Royale analysis has been reviewed, compare wolf-effect estimates and intervals, both feedback directions, forecast gains against drift, and growth/volatility parameters. State the sample periods, missing-data treatment, survey differences and wolf-restoration regimes. Differences in p-values alone do not establish that ecological effects differ between systems. The available exploratory comparison is not a substitute for this final harmonised assessment.

## Evidence supporting this text

1. [Driver coefficients](tables/q1_coefficients.csv).
2. [Granger tests](tables/q2_granger.csv) and [lag selection](tables/q2_lag_selection.csv).
3. [Matched-year forecast scores](tables/q3_scores.csv).
4. [Candidate-data forecast sensitivity](../supplements/gap_research/forecast_sensitivity.csv).
5. [Winter interaction](tables/q4_interaction.csv).
6. [Growth-mean break selection](tables/q5_mean_breaks.csv) and [trend-break search](tables/q5_trend_breaks.csv).
7. [Q6 source and reconciliation](../supplements/q6_removals/README.md); Eberhardt et al. (2007), Journal of Wildlife Management 71:594–602, Table 1, printed p.598, DOI 10.2193/2005-770, user-supplied full paper.
8. [Joint wolf/harvest regression](tables/q6_hunting_vs_wolves.csv).
9. [Viability parameters](tables/q7_parameters.csv) and [threshold scenarios](tables/q7_threshold_probabilities.csv).
10. [State-space variance estimates](tables/r_variance_components.csv).
11. [Remaining source limitations](HANDOFF.md) and [data-gap register](../supplements/gap_research/gap_register.csv).
