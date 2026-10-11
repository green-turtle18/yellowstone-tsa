# Climate, Predators and People: A Time-Series Study of the Yellowstone Ecosystem

MATH F428 – Time Series Analysis and Forecasting, BITS Pilani Goa Campus.

We study how climate, predators, prey and people interact in Yellowstone National Park, using the
reintroduced grey wolf population (1995–2025) as the core series. An optional final section compares
Yellowstone with Indian predator recovery programs (Gir lions, tigers).

This outline deliberately includes everything we might do. Sections will be cut once we know which
datasets we can actually obtain (see `DATA_TODO.md`).

**Legend:** `[MIDSEM]` = uses lectures 1–20, target for the midsem progress talk ·
`[POST]` = needs post-midsem lectures (21–42) · `[DATA?]` = depends on data we don't have yet.

---

## Report outline

**Abstract**

### 1. Introduction `[MIDSEM]`
- 1.1 Motivation: why reintroduction outcomes matter; Yellowstone as the reference case
- 1.2 Research questions
- 1.3 Contributions

### 2. Data `[MIDSEM]`
- 2.1 Wolf population dataset (1995–2025): construction, variables, missing values
- 2.2 Climate data: temperature and snowpack stations; winter-severity index `[DATA?]`
- 2.3 Visitation data (1979–2025, monthly) `[DATA?]`
- 2.4 Prey data: northern elk counts, bison estimates `[DATA?]`
- 2.5 Data limitations: annual frequency, small n, counting effort (collars), method changes
- 2.6 Train/test strategy: holdout years, rolling-origin evaluation

### 3. Exploratory Analysis `[MIDSEM]`
- 3.1 Wolf population trajectory and its phases (growth, crash, stabilisation)
- 3.2 Decomposition of climate and visitation series (classical, STL) `[DATA?]`
- 3.3 Smoothing and trend estimation: moving average, LOESS, polynomial

### 4. Wolf Population Dynamics
- 4.1 Growth-curve modelling: exponential vs logistic; carrying-capacity estimate `[MIDSEM]`
- 4.2 Stationarity analysis: ADF, differencing, regime split `[MIDSEM]`
- 4.3 Model identification: ACF and PACF `[MIDSEM]`
- 4.4a ARMA on the stable phase (2009+) `[MIDSEM]`
- 4.4b ARIMA on the full series `[POST]`
- 4.5 Diagnostic checking: residual ACF, Ljung–Box, QQ plots `[MIDSEM]`
- 4.6 Structural breaks and interventions: distemper years (2005, 2008), 2021 hunting spike `[POST]`
- 4.7 Pack structure: more packs or bigger packs? `[MIDSEM]`
- 4.8 Northern range vs interior dynamics `[MIDSEM]`
- 4.9 Reproduction and mortality: pup survival, changing mix of death causes `[MIDSEM]`

### 5. Climate Trends `[DATA?]`
- 5.1 Trend in temperature and snowpack: deterministic vs stochastic trend `[MIDSEM-able]`
- 5.2 Seasonal ARIMA for monthly climate series `[POST]`
- 5.3 Change in snow-season length

### 6. Prey, Climate and the Predator–Prey System
- 6.1 Elk and bison populations `[DATA?]`
- 6.2 Prey switching: the elk-to-bison shift in kills `[MIDSEM]` (descriptive + regression)
- 6.3 Prey selection: age/sex composition of elk killed `[MIDSEM]`
- 6.4 Variable selection and stationarity checks `[POST]`
- 6.5 VAR specification and lag selection `[POST]`
- 6.6 Granger causality `[POST]`
- 6.7 Impulse responses: how a severe winter propagates through the system `[POST]`
- 6.8 Ecological interpretation

### 7. Visitation Dynamics `[POST]` `[DATA?]`
- 7.1 SARIMA modelling of monthly visits
- 7.2 SARIMAX with climate variables
- 7.3 Intervention analysis: 1988 fires, COVID-19, 2022 flood
- 7.4 Did wolf reintroduction change winter tourism? (post-1995 winter-share test)
- 7.5 Volatility check: ARCH test on residuals

### 8. Forecasting Benchmark `[POST]`
- 8.1 Models: ARIMA/SARIMA, Holt–Winters, gradient boosting, LSTM, foundation models (Chronos/TimesFM), Gaussian process
- 8.2 Evaluation design: rolling-origin backtests, multiple horizons, MAE/RMSE
- 8.3 Results by series: short annual vs long monthly
- 8.4 Forecast combination
- 8.5 Final forecasts with prediction intervals

### 9. Comparison with Indian Recovery Programs: Growth Trajectories and Projections (optional)
- 9.1 Gir lions: recovery vs reintroduction `[MIDSEM]` (growth rates, curve fits)
- 9.2 Growth-rate and carrying-capacity comparison `[MIDSEM]`
- 9.3 Mortality comparison incl. distemper outbreaks (lion deaths 2013–2025) `[POST]`
- 9.4 Projections with bootstrap intervals; Yellowstone as reference scenario `[POST]`
- 9.5 Tigers: national estimates / Panna–Sariska / monthly NTCA mortality `[DATA?]`

### 10. Limitations
### 11. Conclusion (answer each research question from 1.2)
### 12. Availability
### 13. Acknowledgement
### References

---

## Repository layout

```
data/raw/         original datasets, never edited
data/processed/   cleaned data produced by notebooks/scripts
data/external/    downloaded third-party data (climate, visitation, elk, bison)
notebooks/        analysis notebooks, numbered by report section
src/              shared helper functions
figures/          exported plots used in slides/report
reports/          midsem slides and final report
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
