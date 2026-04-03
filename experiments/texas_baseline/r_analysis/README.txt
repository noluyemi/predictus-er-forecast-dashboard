## R Analysis (Graduate Research Validation)

This directory contains the R-based statistical validation of the PredictUS-TX pipeline, 
developed as part of graduate coursework in Health Data Science at UT Southwestern.

### What This Analysis Does
- Cleans and prepares 10 years of weekly CDC ILINet and NOAA temperature data (2015–2025)
- Engineers lag features to give the model a 1-2 week memory of prior flu activity
- Runs a multiple linear regression confirming temperature as a significant predictor of flu ER visits
- Optimizes a surge detection threshold via grid search using F1 score and Youden Index

### Key Results
- Linear regression R² = 0.927 — model explains 92.7% of weekly flu variation in Texas
- Optimal surge threshold identified at k = 1.9 (F1 = 0.899, Youden = 0.857)
- Both metrics independently confirmed k = 1.9 as the data-driven optimal threshold

### Files
- `r_analysis/predictus_tx_analysis.Rmd` — Full annotated R Markdown analysis

### Data Sources
- CDC ILINet — Weekly influenza-like illness surveillance
- NOAA Climate Data Online — Weekly average temperature for Texas
