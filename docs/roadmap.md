# PredictUS Project Roadmap

This file documents the development milestones of the PredictUS: ER Forecast Dashboard.

---

## Completed Milestones

### Week 1–2 (March–April 2025)
-  Defined national impact and problem statement
-  Created GitHub repo with README and structure
-  Identified and cleaned CDC ER visit dataset (2016–2022)
-  Built initial linear regression model in Colab
-  Designed a static dashboard (Streamlit)
-  Created a PDF summary and uploaded to `docs/`
-  Added interactive year-range filter to dashboard
-  Trained and evaluated a Prophet model to forecast ER visits using historical data
-  Exported Prophet model output (2023–2025 forecast) to CSV
-  Uploaded forecast CSV to GitHub (`data/processed/`)
-  Replaced LinearRegression with Prophet in the Streamlit dashboard
-  Visualized prediction intervals (uncertainty bands) in the app
-  Captured live dashboard screenshot for portfolio
-  Embedded forecast chart in `README.md`
-  Updated project roadmap (`docs/roadmap.md`) for traceability

---

## Upcoming Milestones

### April 2025
- Add subgroup filters (age, region)
- Introduce mobility, flu, and weather data
- Host dashboard on custom domain

---

_Last updated: April 2, 2025_
