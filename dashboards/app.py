import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set dashboard config
st.set_page_config(page_title="PredictUS: Regional ER Forecasts", layout="centered")

# Load region forecast data
df = pd.read_csv("data/processed/all_regions_er_forecast.csv")

# Dashboard title
st.title("PredictUS: U.S. Emergency Room Forecast by Region")
st.write("""
Forecasting ER visits from 2016 to 2025 across four U.S. regions using public health data and Prophet modeling.
This dashboard supports proactive planning for hospitals, emergency managers, and public health teams.
""")

# Dropdown to select region
region_selected = st.selectbox("📍 Choose a U.S. Region", sorted(df['region'].unique()))

# Filter for region
region_df = df[df["region"] == region_selected]

# Plot forecast
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(region_df["Year"], region_df["Forecast"], label="Forecast", marker="o")
ax.fill_between(region_df["Year"], region_df["yhat_lower"], region_df["yhat_upper"], alpha=0.2, label="Confidence Interval")
ax.set_title(f"{region_selected} Region ER Visit Forecast (2016–2025)")
ax.set_xlabel("Year")
ax.set_ylabel("Estimated Visits")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Footer
st.markdown("Created by Naomi Oluyemi | MPH Candidate | Public Health x AI")
