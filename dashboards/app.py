import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# App setup
st.set_page_config(page_title="PredictUS: Regional ER Forecast", layout="centered")

# Load ER forecast data
forecast_df = pd.read_csv("data/processed/all_regions_er_forecast.csv")

# Load flu data
flu_df = pd.read_csv("data/processed/cdc_ilinet_flu_by_year.csv")

# Merge by Year + Region
df = pd.merge(forecast_df, flu_df, on=["Year", "region"], how="left")

# Title
st.title("PredictUS: U.S. Emergency Room Forecast Dashboard")
st.write("Interactive dashboard forecasting ER visits (2016–2025) using AI and CDC/HHS public data.")

# Sidebar filters
st.sidebar.header("📍 Filters")

# Region selector
region_selected = st.sidebar.selectbox("Select Region", sorted(df["region"].unique()))

# Filter region first
region_df = df[df["region"] == region_selected]

# Year filter based on available data for the region
min_year = int(region_df["Year"].min())
max_year = int(region_df["Year"].max())

start_year = st.sidebar.selectbox("Start Year", list(range(min_year, max_year + 1)), index=0)
end_year = st.sidebar.selectbox("End Year", list(range(min_year, max_year + 1)), index=len(range(min_year, max_year + 1)) - 1)

# Filter by year range
if start_year > end_year:
    st.warning("⚠️ Start year must be before end year.")
    st.stop()

filtered_df = region_df[(region_df["Year"] >= start_year) & (region_df["Year"] <= end_year)]

# Plot with Flu Overlay
fig, ax = plt.subplots(figsize=(10, 5))

# Plot ER forecast
ax.plot(filtered_df["Year"], filtered_df["Forecast"], label="Forecast", marker="o")
ax.fill_between(
    filtered_df["Year"],
    filtered_df["yhat_lower"],
    filtered_df["yhat_upper"],
    alpha=0.2,
    label="Confidence Interval"
)
ax.set_xlabel("Year")
ax.set_ylabel("Estimated ER Visits")
ax.set_title(f"{region_selected} Region ER Forecast with Flu Overlay ({start_year}–{end_year})")
ax.grid(True)

# Add flu trend line on secondary axis if column exists
if "Average_Flu_Percent" in filtered_df.columns and filtered_df["Average_Flu_Percent"].notna().any():
    ax2 = ax.twinx()
    ax2.plot(
        filtered_df["Year"],
        filtered_df["Average_Flu_Percent"],
        color="orange",
        linestyle="--",
        marker="s",
        label="Avg Flu % (CDC ILINet)"
    )
    ax2.set_ylabel("Average Flu %")
    ax2.legend(loc="upper left")

ax.legend(loc="upper right")
st.pyplot(fig)

st.markdown("*CDC ILINet flu data integrated for seasonal context. Values represent average % of outpatient visits for flu-like illness.*")

# Footer
st.markdown("Created by Naomi Oluyemi | MPH Candidate | Public Health x AI")
