
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
| Model | R² | MAE | Notes |
|--------|----|-----|-------|
| **Linear Regression** | 0.63 | 506 | Baseline performance (flu + temp) |
| **XGBoost** | 0.85 | 252 | Captures nonlinear + lag relationships |

Plots are saved in `/plots/` (e.g., `lr_vs_actual_tx-2.png`, `xgb_vs_actual_tx-3.png`)  

---

Surge Detection & Threshold Validation

Surge alerts are defined as predicted ILI values exceeding a dynamic threshold:

**Surge threshold formula:**  
Threshold = Mean (μ) + k × Standard Deviation (σ)

where **μ** = mean ER ILI volume (train set), **σ** = standard deviation, and **k** is tuned via optimization.

### Optimization Results
| Metric | Optimal Value |
|---------|----------------|
| **Best k (Youden/F1)** | **1.0 × SD above mean** |
| **Sensitivity** | 0.94 |
| **Specificity** | 0.95 |
| **PPV** | 0.80 |
| **NPV** | 0.99 |
| **F1-score** | 0.86 |
| **Youden Index** | 0.89 |

**Artifacts:**
- `media/tx_surge_detection_k1.00.png` — Surge alert visualization  
- `media/threshold_optimization_plot.png` — F1 & Youden vs. k curve  
- `config/tx_threshold_best.json` — Full saved metrics  
- `data/processed/tx_threshold_gridsearch.csv` — All tested k-values (1.0–2.5)

Interpretation:  
The threshold optimization ensures that surge alerts are *data-driven* rather than arbitrary, improving interpretability and reproducibility when comparing predicted vs actual surges.

---

## Key Insights

- Temperature and flu intensity alone explain **85%** of variance in ER ILI visits statewide.
- Optimal surge threshold (mean + 1×SD) achieves high discriminative validity:
  - Sensitivity and specificity above 0.9  
  - Near-perfect negative predictive value (0.99)
- Demonstrates the **feasibility of proactive ER surge monitoring** from open data.

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
