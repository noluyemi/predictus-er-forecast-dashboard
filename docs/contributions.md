**Contributions – PredictUS: ER Surge Forecasting Dashboard**
---
Naomi Oluyemi – MPH Candidate | Public Health x AI

This document outlines my individual contributions to the design, development, and deployment of PredictUS, an open-source U.S. emergency department forecasting tool built to support real-time surge preparedness for hospitals and public health agencies.

 **Data Engineering & Acquisition**
---
- Independently sourced U.S. emergency room visit data (2016–2022) from HealthData.gov
- Integrated CDC ILINet FluView surveillance data to capture seasonal respiratory trends
- Performed full data wrangling, normalization, and harmonization using pandas and EDA techniques
- Merged regional and national datasets into time-series ready formats for modeling

**Forecast Modeling & Analysis**
---
- Developed and validated Prophet-based time series models for national and regional ER visit forecasting (through 2025)
- Engineered a dual-layer overlay that visualizes influenza-like illness (ILI) trends alongside ER forecast intervals
- Introduced yearly seasonality controls and uncertainty intervals to reflect real-world surge behavior
 
Dashboard Architecture & UX
---
Designed and deployed a fully interactive Streamlit dashboard for public exploration of regional ER surge predictions
Added user-controlled filters for region selection and custom date ranges
Implemented automatic flu overlay for seasonal interpretation; structured for future toggles (weather, mobility, etc.)

 Repository Structure & Technical Documentation
---
- Organized repository for academic transparency and reuse: /data, /notebooks, /dashboards, /docs, /media
- Maintained clear commit history and modular Python scripts for reproducibility
- Authored README.md, evaluation.md, and this contributions.md for scholarship, grant, and immigration reviewers

 Tools & Technology Stack
---
- Languages & Libraries: Python, Pandas, Prophet, Matplotlib, Streamlit
- Platforms: Google Colab, GitHub, Streamlit Cloud
- Data Sources: HealthData.gov, CDC FluView (ILINet), U.S. Census regions

Public Health Leadership & Impact
---
- Sole contributor responsible for the entire development cycle—from concept to public deployment
- PredictUS is a national-level AI tool designed to assist public hospitals, FEMA, and health departments in anticipating ER strain
- Project contributes to U.S. health system resilience, staffing efficiency, and equity-centered crisis prevention
- Designed with underserved communities in mind—empowering hospitals with early warnings before surges escalate
