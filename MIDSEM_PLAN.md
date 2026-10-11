# Midsem goal: everything doable with lectures 1–20

Lectures covered: probability foundations (1–3), EDA & decomposition (4–8),
stationarity / ADF / ACF / PACF / regression / nonlinear regression (9–14),
AR, MA, ARMA, Yule–Walker (15–20).

## Sections to complete before midsem

| # | Section | Methods (lecture block) | Notebook |
|---|---|---|---|
| 1 | Introduction + research questions | — | — |
| 2 | Data (2.1, 2.5, 2.6) | — | `01_data_cleaning` |
| 3 | EDA (3.1, 3.3) | plots, smoothing, polynomial/LOESS trends (4–8) | `02_eda` |
| 4 | Wolf dynamics (4.1–4.3, 4.4a, 4.5, 4.7–4.9) | logistic fit, ADF, ACF/PACF, ARMA, Yule–Walker, Ljung–Box (9–20) | `03_wolf_dynamics` |
| 6 | Prey switching & selection (6.2–6.3) | trend regression on kill shares (9–14) | `04_prey_kills` |
| 9 | Gir lions growth comparison (9.1–9.2) | exponential vs logistic fit, growth rates (9–14) | `05_gir_lions` |

**Stretch goal:** if climate data is downloaded in time, add 3.2 / 5.1 (decomposition + trend test) — pre-midsem methods.

## Not for midsem
ARIMA on full series, interventions, SARIMA/SARIMAX, forecasting, VAR/Granger, ARCH, ML benchmark.

## 5-minute talk (6 slides)
1. Question & why it matters
2. Data: 31 years, key variables, limitations
3. Wolf trajectory with phases marked
4. Logistic fit + ADF results + ACF/PACF → tentative ARMA
5. Wolves vs Gir lions: growth-rate / carrying-capacity table
6. Full report plan & data still to collect
