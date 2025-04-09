**Evaluation & Use Case: ER Forecast + Flu Overlay**

**Purpose**
This dashboard allows public health professionals, hospital administrators, and policy leaders to visualize projected ER visit volumes alongside flu season severity, giving them early insight for staffing, triage, and resource planning.

**Why Overlay Flu Data?**
Seasonal influenza is a key driver of ER spikes. By integrating CDC ILINet data (average % of outpatient visits for flu-like illness), we:

- Reveal patterns that mirror or diverge from flu season
- Help decision-makers determine if upcoming surges are flu-related or possibly due to other emerging threats
- Promote equity-driven planning in regions with under-resourced ER systems

**Technical Notes:**
- Forecasts are generated using Prophet (Meta) on public CDC/HHS datasets
- Flu data is sourced from CDC FluView (ILINet) and mapped by year
- Dual-axis plots present ER forecasts (left axis) and flu trends (right axis)

**Example Insight**
In the Midwest, the 2023 ER surge forecast closely aligns with a 5% flu trend spike — indicating a likely seasonal overload.
In contrast, the South region’s forecast for 2025 shows an uptick not explained by flu, suggesting a need to investigate non-flu drivers (e.g., heat, mobility, RSV, or environmental alerts).

**Limitations:**
- ILINet data is national (not state-specific in this version)
- Flu data currently available only up to 2023
- Future versions will integrate weather anomalies, Google mobility trends, and capacity APIs

---

##  Modeling Reflection (April 2025)

**Model Used:** Prophet (Meta/Facebook’s time series forecasting tool)  
**Target Variable:** Annual emergency department (ED) visits by region  
**Auxiliary Input:** CDC ILINet flu percentages (seasonal respiratory strain proxy)  

### Strengths:
- Captures long-term ER visit trends with minimal tuning  
- Handles seasonal variation using Prophet’s built-in yearly seasonality  
- Offers interpretability — helpful for public health transparency and decision support  
- Overlaying flu data gives immediate context for respiratory-related surges

###  Limitations:
- Prophet is univariate by design (can’t natively handle multiple features like weather + flu + mobility)  
- Small dataset size at the regional level limits model expressiveness  
- Works best for macro-level annual forecasting — not yet ready for weekly predictions or real-time alerting

---

### Next Modeling Steps (May 2025)

- Test **multivariate models** (XGBoost, LSTM, or Prophet hybrid pipelines)  
- Integrate **weather anomalies**, **Google mobility**, and holiday indicators  
- Train **state-level models** to improve local forecasting accuracy  
- Implement validation using **MAPE**, **RMSE**, or cross-region backtesting  
- Prepare **technical preprint** and GitHub issue threads for feedback from public health modelers

