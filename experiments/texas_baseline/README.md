
# PredictUS-TX (State-Level Prototype)

This sub-project applies PredictUS methods at the state level (Texas), using **weekly influenza surveillance (CDC ILINet, 2015–2025)** and **NOAA temperature data** as predictors.  
Mobility data (Google COVID-19 mobility, 2020–2022) was also processed, but because of limited coverage it is not yet integrated into the baseline model.

---

## Pipeline

- `data/raw/` → Original downloaded datasets (ILINet, NOAA, mobility)  
- `notebooks/data_cleaning.py` → Cleaning pipeline (flu + temp → weekly merge)  
- `data/processed/predictus_tx_flu_temp.csv` → Final weekly dataset (flu + temperature only, 2015–2025)  
- `notebooks/baseline_flu_temp_xgboost.py` → XGBoost baseline (+1 week forecasting)  
- `notebooks/baseline_flu_temp_linear.py` → Linear regression baseline  

---

## Current Results

- **Linear Regression**: R² ≈ 0.63, MAE ≈ 506 (baseline performance with flu + temp)  
- **XGBoost**: R² ≈ 0.85, MAE ≈ 252 (captures nonlinear relationships and lag effects)  

Plots are saved in `/plots/` (e.g., `lr_vs_actual_tx-2.png`, `xgb_vs_actual_tx-3.png`)  

---

## Next Steps

1. Add proxy features for **behavioral/mobility effects** (holiday calendars, Google Trends, traffic/weather anomalies).  
2. Explore **Prophet/SARIMAX** models for seasonality comparisons.  
3. Expand to **state-by-state pipelines** for national coverage.  
4. Build interactive visualization via Streamlit
5. Draft **preprint** outlining methodology, results, and applications.  

---
