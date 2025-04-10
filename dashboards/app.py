import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# App setup
st.set_page_config(page_title="PredictUS: Regional ER Forecast", layout="centered")

# Load ER forecast + mobility data
forecast_df = pd.read_csv("data/processed/all_regions_er_flu_mobility_forecast.csv")
forecast_df.columns = forecast_df.columns.str.strip().str.lower()

# Load flu data
flu_df = pd.read_csv("data/processed/cdc_ilinet_flu_by_year.csv")
flu_df.columns = flu_df.columns.str.strip().str.lower()
flu_df = flu_df.rename(columns={"average_flu_percent": "avg_flu_percent"})

# Merge datasets on 'year'
df = pd.merge(forecast_df, flu_df, on="year", how="left")

# Dashboard title
st.title(" PredictUS: U.S. ER Surge Forecast Dashboard")
st.markdown("Forecasting U.S. emergency room visits with AI, flu trends, and mobility behavior data.")

# Sidebar filters
st.sidebar.header("📍 Filters")
region_selected = st.sidebar.selectbox("Select Region", sorted(df["region"].unique()))

region_df = df[df["region"] == region_selected]
min_year = int(region_df["year"].min())
max_year = int(region_df["year"].max())

start_year = st.sidebar.selectbox("Start Year", list(range(min_year, max_year + 1)), index=0)
end_year = st.sidebar.selectbox("End Year", list(range(min_year, max_year + 1)), index=len(range(min_year, max_year + 1)) - 1)

if start_year > end_year:
    st.warning("⚠️ Start year must be before end year.")
    st.stop()

# Final filtered data
filtered_df = region_df[(region_df["year"] >= start_year) & (region_df["year"] <= end_year)]

# Main plot
fig, ax = plt.subplots(figsize=(10, 5))

# ER Forecast
ax.plot(filtered_df["year"], filtered_df["forecast"], label="ER Forecast", marker="o", linewidth=2)
ax.fill_between(filtered_df["year"], filtered_df["yhat_lower"], filtered_df["yhat_upper"], alpha=0.2, label="Confidence Interval")
ax.set_xlabel("Year")
ax.set_ylabel("Estimated ER Visits")
ax.set_title(f"{region_selected} Region: ER Forecast with Flu & Mobility Trends ({start_year}–{end_year})")
ax.grid(True)

# Flu + Mobility Overlay
if "avg_flu_percent" in filtered_df.columns:
    ax2 = ax.twinx()
    ax2.set_ylabel("Flu & Mobility Indicators (%)")

    if filtered_df["avg_flu_percent"].notna().any():
        ax2.plot(filtered_df["year"], filtered_df["avg_flu_percent"], color="orange", linestyle="--", marker="s", label="Avg Flu %")

    if (
        "retail_and_recreation_percent_change_from_baseline" in filtered_df.columns and
        "grocery_and_pharmacy_percent_change_from_baseline" in filtered_df.columns
    ):
        mobility_avg = filtered_df[
            ["retail_and_recreation_percent_change_from_baseline", "grocery_and_pharmacy_percent_change_from_baseline"]
        ].mean(axis=1)

        ax2.plot(filtered_df["year"], mobility_avg, color="green", linestyle=":", marker="^", label="Avg Mobility % (Retail + Grocery)")

    ax2.legend(loc="upper left")

# Finalize plot
ax.legend(loc="upper right")
st.pyplot(fig)

# Footer
st.markdown("*CDC ILINet flu and Google Mobility data provide seasonal and behavioral context for ER surge forecasting.*")
st.markdown("Created by **Naomi Oluyemi** | MPH Candidate | *Public Health x AI*")
