## 1. Yellowstone elk and wolves

The primary dataset is the corrected, flagged Yellowstone master, with 42 annual rows. Numerical entries include estimates and are not 42 fully comparable observations. Model samples differ. Recovered wolf counts are a separate sensitivity scenario. Q0 data audit, Q1 drivers, Q2 feedback, Q3 predictions, Q4 winter, Q5 breaks, Q6 removals, Q7 viability and R observation error are covered. Source: reports/CONCLUSIONS.md and reports/RESULTS.md. Prepared 20 November 2026.

## 2. Wolf effects and feedback remain uncertain

The regressor is (wolves[t−1]−wolves[t−2])/10, and the outcome is log(elk[t])−log(elk[t−1]). A ten-wolf increase refers to the preceding annual change, not a level effect. The wolf-only interval includes negative and small positive associations. Full model includes the other covariates. Non-significance does not prove no biological effect. Granger tests concern predictive information, not causation. Both AIC and BIC prefer lag 0. Sources: reports/tables/q1_coefficients.csv, q2_granger.csv, q2_lag_selection.csv.

## 3. Wolves add little forecasting accuracy

Evaluation years: 2011, 2012, 2013, 2017, 2018, 2019, 2023, 2024, 2025. Training transformations use training data only, and scoring excludes imputed targets/prior counts and unresolved coverage. Full-model predictors include information potentially after some surveys. These are conditional retrospective predictions. No statistical significance is asserted for MAE differences. Candidate northern counts for 1996–2000 are 19,32,42,35,65. Conflicting source values for other years remain unresolved. Sources: reports/tables/q3_scores.csv and supplements/gap_research/forecast_sensitivity.csv.

## 4. Winter and break tests give limited evidence

Winter interaction does not distinguish additive from compensatory mortality. Exposure windows are not fully aligned to survey dates. Growth-mean break selection and the trend-break search are different hypotheses. The selected trend date is not a formal causal attribution or a Bai–Perron confidence set. The growth-state model converges with 33 observed values on a 40-year model grid. SDs are on the fitted latent log-count/process and observation scale, not numbers of elk. Spatial mismatches remain. Sources: q4_interaction.csv, q5_mean_breaks.csv, q5_trend_breaks.csv, r_variance_components.csv.

## 5. The hunting definition changes the comparison

Eberhardt et al. (2007), A Seventy-Year History of Trends in Yellowstone’s Northern Elk Herd, J Wildlife Management 71:594–602, DOI 10.2193/2005-770. Table 1, PDF page 5 / printed p.598, user-provided paper. Total kills by year: 517,591,788,1182,1084,1773,1897,2069,2611. Hunting: 1400,2465,1313,1683,974,1259,1139,718,702. Winter-year labels match existing harvest seasons. The plotted fall-plus-late series includes estimated fall components for 1998–2004. No annual confidence intervals are available for the wolf estimates. Published 0.26 adjustment reflects prime-age classes and is retained separately, not used as total kills. No annual uncertainty intervals are supplied. The joint standardised regression has p=0.145 for wolves and p=0.907 for harvest, so it cannot establish a ranking either. Sources: supplements/q6_removals/README.md and reports/tables/q6_hunting_vs_wolves.csv.

## 6. Viability estimates are uncertain scenarios

Continuous first passage counts any crossing during ten years. Annual monitoring checks only at yearly intervals and can miss crossings between observations. The bootstrap interval covers parameter uncertainty conditional on GBM, not systematic survey bias or future ecological changes. Thresholds apply to a survey-count index. Source: reports/tables/q7_threshold_probabilities.csv and q7_parameters.csv. No management or extinction forecast is asserted.

## 7. Yellowstone and Isle Royale comparison

Source: 05_synthesis/report/COMPARISON.md and reports/tables in that folder. Both systems use Person 4 specification 1.3. Lagged wolf levels and density differ from the original Yellowstone change-in-wolves model. Full coefficients and 95% intervals are in comparison_summary.csv. Negative forecast gain means worse performance than drift. Shared 22-year forecasts include filled training inputs; strict observed-input sensitivity has only seven shared years. Differences in significance do not prove different ecological effects. Survey timing, source conflicts and missing Isle Royale kill rates remain documented.