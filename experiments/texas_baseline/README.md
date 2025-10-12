
# PredictUS-TX (State-Level Prototype)

This sub-project applies **PredictUS** methods at the **state level (Texas)**, using weekly influenza surveillance (CDC ILINet, 2015–2025) and NOAA temperature data as predictors.  
Google COVID-19 mobility data (2020–2022) was also processed but not yet integrated due to limited coverage.

---

## Pipeline

- `data/raw/` → Original downloaded datasets (ILINet, NOAA, mobility)  
- `notebooks/data_cleaning.py` → Cleaning pipeline (flu + temp → weekly merge)  
- `data/processed/predictus_tx_flu_temp.csv` → Final weekly dataset (flu + temperature only, 2015–2025)  
- `notebooks/baseline_flu_temp_xgboost.py` → XGBoost baseline (+1 week forecasting)  
- `notebooks/baseline_flu_temp_linear.py` → Linear regression baseline
- `notebooks/surge_detection.py` → Surge alert generation (mean + k×SD threshold) 
- `notebooks/threshold_optimization.py` → Threshold optimization using F1-score & Youden Index 
- `media/` → Output plots (XGBoost, Linear Regression, Surge Detection, Threshold Optimization) 

---

---

## Current Results
| Model | R² | Standardized Z-Score | Notes |
|--------|----|-----|-------|
| **XGBoost** | 0.73 | 0.28 | Captures nonlinear + lag relationships |

Plots are saved in `/plots/` (e.g., `lr_vs_actual_tx-2.png`, `xgb_vs_actual_tx-3.png`)  

---

Surge Detection & Threshold Validation

Surge alerts are defined as predicted ILI values exceeding a dynamic threshold:

**Surge threshold formula:**  
Threshold = Mean (μ) + k × Standard Deviation (σ)

where **μ** = mean ER ILI volume (train set), **σ** = standard deviation, and **k** is tuned via optimization.

---
The optimal threshold was identified using a grid search (k=1.0 to 2.5), maximizing both the **F1-Score** (predictive balance) and the **Youden Index** (overall discriminative power).

| Metric | Optimal Value (k=1.25) | Interpretation for Public Health |
| :--- | :--- | :--- |
| **Optimal k** | **1.25** | The optimal surge alert threshold is set at **1.25 standard deviations above the mean** of historical flu activity. |
| **Sensitivity (Recall)** | **94.12%** | **CRITICAL:** The model correctly **identifies over 94% of actual flu surges** (minimizing missed outbreaks). |
| **Specificity** | **97.06%** | The model correctly **predicts a normal week over 97% of the time** (minimizing unnecessary resource deployment). |
| **NPV (Negative Predictive Value)** | **99%** | The model is **near-perfect** at confirming when a surge is **not** going to happen (99% certainty of no surge when alert is negative). |

### Operational Impact Summary (Last Test Fold)

The model was tested over **85 weeks**. Of the 17 actual surge periods, the model correctly issued an alert for **16 (True Positives)** and only missed **1 (False Negative)**. This demonstrates **high actionability** for immediate hospital resource allocation.

**Artifacts:**
- `media/tx_surge_detection_k1.00.png` — Surge alert visualization  
- `media/threshold_optimization_plot.png` — F1 & Youden vs. k curve  
- `config/tx_threshold_best.json` — Full saved metrics  
- `data/processed/tx_threshold_gridsearch.csv` — All tested k-values (1.0–2.5)

Interpretation:  
The threshold optimization ensures that surge alerts are *data-driven* rather than arbitrary, improving interpretability and reproducibility when comparing predicted vs actual surges.

---


##  Next Steps

1. **Add proxy features** for behavioral and mobility patterns (holiday calendars, Google Trends, traffic/weather anomalies).  
2. **Run multi-state replication** (California, Florida, New York) for external validation.  
3. **Evaluate lead-time performance:** how early the model detects upcoming surges.  
4. **Deploy Streamlit dashboard** for real-time visualization.  
5. **Draft preprint/manuscript** describing data, model validation, and surge metrics for submission to open-access journal.

---

## References
- CDC ILINet — Influenza-Like Illness Surveillance  
- NOAA Climate Data Online  
- Google COVID-19 Community Mobility Reports  
- Youden WJ (1950). *Index for rating diagnostic tests*. **Cancer**, 3(1):32–35.  
- Chicco & Jurman (2020). *Advantages of the Matthews correlation coefficient over F1 score and accuracy in binary classification evaluation*. **BMC Genomics**.
