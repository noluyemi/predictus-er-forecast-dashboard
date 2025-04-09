import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# App setup
st.set_page_config(page_title="PredictUS: Regional ER Forecast", layout="centered")

# Load ER forecast data
forecast_df = pd.read_csv("data/processed/all_regions_er_flu_mobility_forecast.csv")
forecast_df.columns = forecast_df.columns.str.strip().str.lower()

# Load and prepare flu data
flu_df = pd.read_csv("data/processed/cdc_ilinet_flu_by_year.csv")
flu_df.columns = flu_df.columns.str.strip().str.lower()
flu_df = flu_df.rename(columns={"average_flu_percent": "avg_flu_percent"})

# Merge the two datasets on 'year'
df = pd.merge(forecast_df, flu_df, on="year", how="left")

# Title
st.title("PredictUS: U.S. Emergency Room Forecast Dashboard")
st.write("Interactive dashboard forecasting ER visits (2016–2025) using AI and CDC/HHS public data.")

# Sidebar filters
st.sidebar.header("📍 Filters")
region_selected = st.sidebar.selectbox("Select Region", sorted(df["region"].unique()))

# Filter region first
region_df = df[df["region"] == region_selected]

# Year filter based on available data for the region
min_year = int(region_df["year"].min())
max_year = int(region_df["year"].max())
start_year = st.sidebar.selectbox("Start Year", list(range(min_year, max_year + 1)), index=0)
end_year = st.sidebar.selectbox("End Year", list(range(min_year, max_year + 1)), index=len(range(min_year, max_year + 1)) - 1)

# Validate year range
if start_year > end_year:
    st.warning("⚠️ Start year must be before end year.")
    st.stop()

# Filter final dataset
filtered_df = region_df[(region_df["year"] >= start_year) & (region_df["year"] <= end_year)]

# Plotting
fig, ax = plt.subplots(figsize=(10, 5))

# Plot ER forecast
ax.plot(filtered_df["year"], filtered_df["forecast"], label="Forecast", marker="o")
ax.fill_between(filtered_df["year"], filtered_df["yhat_lower"], filtered_df["yhat_upper"], alpha=0.2, label="Confidence Interval")
ax.set_xlabel("Year")
ax.set_ylabel("Estimated ER Visits")
ax.set_title(f"{region_selected} Region ER Forecast with Flu + Mobility Trends ({start_year}–{end_year})")
ax.grid(True)

# Add flu and mobility overlay on secondary axis
if "avg_flu_percent" in filtered_df.columns and filtered_df["avg_flu_percent"].notna().any():
    ax2 = ax.twinx()
    ax2.plot(filtered_df["year"], filtered_df["avg_flu_percent"], color="orange", linestyle="--", marker="s", label="Avg Flu % (CDC ILINet)")
    ax2.set_ylabel("Flu & Mobility Trends")

    # Add mobility trend (average of retail + grocery)
    if (
        "retail_and_recreation_percent_change_from_baseline" in filtered_df.columns and
        "grocery_and_pharmacy_percent_change_from_baseline" in filtered_df.columns
    ):
        mobility_avg = filtered_df[
            ["retail_and_recreation_percent_change_from_baseline", "grocery_and_pharmacy_percent_change_from_baseline"]
        ].mean(axis=1)

        ax2.plot(filtered_df["year"], mobility_avg, color="green", linestyle=":", marker="^", label="Avg Mobility % (Retail + Grocery)")
        ax2.legend(loc="upper left")

ax.legend(loc="upper right")
st.pyplot(fig)

st.markdown("*CDC ILINet flu and Google Mobility data integrated for seasonal and behavioral context.*")
st.markdown("Created by Naomi Oluyemi | MPH Candidate | Public Health x AI")
