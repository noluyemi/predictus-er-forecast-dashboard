## PredictUS-TX (State-Level Prototype)

This sub-project applies PredictUS methods at the state level (Texas), merging weekly influenza (ILINet), Google mobility (2020–2022), and NOAA temperature anomalies.

### Pipeline
- `data/raw/` → Original downloaded datasets
- `notebooks/data_cleaning.ipynb` → Full cleaning pipeline (flu, mobility, temp → weekly merge)
- `data/processed/predictus_tx_merged.csv` → Final weekly dataset for modeling

### Next Steps
- Train multivariate models (XGBoost, Prophet) for +1 and +2 week ER/ILI surge forecasting
- Add visualization via Streamlit (`dashboards/app_tx.py`)
- Prepare for poster/paper submissions (APHA 2026)
