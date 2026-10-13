# Yellowstone Trophic Cascade: A Time Series Analysis (1984–2025)

## 📌 Project Overview
This repository contains a comprehensive time-series analysis designed to mathematically test one of the most famous ecological debates in modern history: **The Yellowstone Trophic Cascade.** 

The classic ecological narrative states that the reintroduction of gray wolves to Yellowstone National Park in 1995 caused a "top-down" trophic cascade. By drastically reducing the overpopulated Northern Yellowstone elk herd, the wolves supposedly allowed overgrazed vegetation (willows and aspens) to recover. 

However, many ecologists argue this narrative is an oversimplification. Skeptics suggest that "bottom-up" factors—such as severe droughts, harsh winters, and aggressive forage competition from a booming bison population—played a far greater role in the elk decline. 

Using the **Box-Jenkins methodology (SARIMAX forecasting)**, this project statistically isolates these variables over a 42-year timeline (1984–2025) to determine whether predator pressure (wolves), climate (drought/precipitation), or competitive exclusion (bison) holds the most predictive weight over the elk population.

---

## 📊 Datasets & Sources
The data in this project is strictly geographically constrained to the **Northern Range** of Yellowstone National Park to ensure spatial consistency. 

1. **Target Variable ($Y_t$): Northern Yellowstone Elk Count**
   * *Sources:* Dr. Dan MacNulty's Northern Yellowstone Cooperative Winter Elk Count (1984–2015) spliced with Montana Fish, Wildlife & Parks (MT FWP) administrative aerial estimates for Hunting District 313 (2016–2025). 
2. **Exogenous Variable 1 ($X_1$): Northern Range Wolf Population**
   * *Source:* National Park Service (NPS) Yellowstone Wolf Project Annual Reports (1995–2025). Missing early establishment years (1996–2000) were bridged via linear interpolation.
3. **Exogenous Variable 2 ($X_2$): Summer Vegetation (NDVI)**
   * *Source:* Climate Engine satellite imagery. Filtered strictly to June–August (JJA) to isolate active vegetative growth from winter snow cover.
4. **Exogenous Variable 3 ($X_3$): Annual Precipitation**
   * *Source:* TerraClimate via Climate Engine. Aligned to the "Water Year" (Oct–Sept) to properly capture critical winter snowpack accumulation.
5. **Exogenous Variable 4 ($X_4$): Palmer Drought Severity Index (PDSI)**
   * *Source:* TerraClimate via Climate Engine (Water Year).
6. **Exogenous Variable 5 ($X_5$): Northern Herd Bison Population**
   * *Sources:* NPS "Yellowstone Bison Population Status Report" (Oct 2023) detailing historic Northern Herd counts (1984–2022), augmented with recent MT news and conservation estimates for 2024–2025.

---

## 🗂️ Repository Structure

```text
├── data/
│   ├── raw/                  # Original, unmodified source datasets (CSVs, PDFs)
│   └── processed/            # Cleaned, merged, and interpolated datasets (e.g., yellowstone_master_ts_final.csv)
├── notebooks/                # Jupyter notebooks for EDA, Granger Causality, and SARIMAX modeling
├── reports/
│   └── figures/              # Generated visualizations (ACF/PACF, QQ plots, Decision Trees)
├── scripts/                  # Standalone Python processing scripts
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
└── .gitignore                # Ignored system files
```

---

## ⚙️ Methodology & Project Phases (Task Tracker)

### Phase 1: Exploratory Data Analysis (EDA) & Stationarity
- [x] Split timeline into 80% Training (1984–2017) and 20% Testing (2018–2025).
- [x] Apply Augmented Dickey-Fuller (ADF) test.
- [x] Log-difference the target variable ($d=1$) to resolve unit root.
- [x] Generate ACF and PACF plots for initial autoregressive and moving average parameters.

### Phase 2: Preliminary Regression & Granger Causality
- [x] Fit baseline regressions (Linear, Polynomial, Splines).
- [x] Run pairwise Granger Causality test to identify leading indicators (identifying Bison as a significant 1-year leading indicator).

### Phase 3: SARIMAX Modeling
- [ ] Build candidate SARIMAX models incorporating exogenous variables (Wolves, NDVI, Precip, PDSI).
- [ ] Rank candidate models using Akaike Information Criterion (AIC) and Bayesian Information Criterion (BIC) scores.
- [ ] Extract coefficients to determine which variable holds the most predictive weight.

### Phase 4: Diagnostic Checking
- [ ] Generate Quantile-Quantile (QQ) plot for residual normality.
- [ ] Plot Ljung-Box test across 20 lags to verify residuals act as white noise.
- [ ] Evaluate Train vs. Test accuracy using Mean Absolute Error (MAE).

### Phase 5: Explainability & Ecological Tipping Points
- [ ] Train a Decision Tree Regressor on exogenous variables.
- [ ] Export tree graphic to map ecological thresholds and breaking points.