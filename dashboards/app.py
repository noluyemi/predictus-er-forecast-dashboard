import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# App setup
st.set_page_config(page_title="PredictUS: Regional ER Forecast", layout="centered")

# ER forecast + mobility + temperature data
forecast_df = pd.read_csv("data/processed/all_regions_er_flu_mobility_forecast.csv")
forecast_df.columns = forecast_df.columns.str.strip().str.lower()

# flu data
flu_df = pd.read_csv("data/processed/cdc_ilinet_flu_by_year.csv")
flu_df.columns = flu_df.columns.str.strip().str.lower()
flu_df = flu_df.rename(columns={"average_flu_percent": "avg_flu_percent"})

# Merged datasets
df = pd.merge(forecast_df, flu_df, on="year", how="left")

# Sidebar: Region & year filters
st.title("PredictUS: U.S. ER Surge Forecast Dashboard")
st.markdown("Forecasting U.S. emergency room visits using AI, flu trends, mobility data, and temperature insights.")

st.sidebar.header("Filters")
region_selected = st.sidebar.selectbox("Select Region", sorted(df["region"].unique()))

region_df = df[df["region"] == region_selected]
min_year = int(region_df["year"].min())
max_year = int(region_df["year"].max())

start_year = st.sidebar.selectbox("Start Year", list(range(min_year, max_year + 1)), index=0)
end_year = st.sidebar.selectbox("End Year", list(range(min_year, max_year + 1)), index=len(range(min_year, max_year + 1)) - 1)

if start_year > end_year:
    st.warning("Start year must be before end year.")
    st.stop()

# Filtered dataset
filtered_df = region_df[(region_df["year"] >= start_year) & (region_df["year"] <= end_year)].copy()

# Center temperature for display only
if "avg_temperature_f" in filtered_df.columns and filtered_df["avg_temperature_f"].notna().any():
    filtered_df["temp_centered"] = filtered_df["avg_temperature_f"] - filtered_df["avg_temperature_f"].mean()
else:
    filtered_df["temp_centered"] = None

# Plot
fig, ax = plt.subplots(figsize=(10, 5))

# Primary y-axis: ER Forecast
line1 = ax.plot(filtered_df["year"], filtered_df["forecast"], label="ER Forecast", color="steelblue", marker="o", linewidth=2)
ax.fill_between(filtered_df["year"], filtered_df["yhat_lower"], filtered_df["yhat_upper"], color="lightblue", alpha=0.3, label="Confidence Interval")

ax.set_xlabel("Year")
ax.set_ylabel("Estimated ER Visits")
ax.set_title(f"{region_selected} Region: ER Forecast with Flu, Mobility & Climate Trends ({start_year}–{end_year})")
ax.grid(True)

# Secondary y-axis
ax2 = ax.twinx()
ax2.set_ylabel("Flu %, Mobility %, Temp (°F, Centered)")

legend_lines = []
legend_labels = []

# Flu trend
if "avg_flu_percent" in filtered_df.columns and filtered_df["avg_flu_percent"].notna().any():
    line2, = ax2.plot(filtered_df["year"], filtered_df["avg_flu_percent"], color="orange", linestyle="--", marker="s", label="Avg Flu %")
    legend_lines.append(line2)
    legend_labels.append("Avg Flu %")

# Mobility trend (average of retail & grocery)
if (
    "retail_and_recreation_percent_change_from_baseline" in filtered_df.columns and
    "grocery_and_pharmacy_percent_change_from_baseline" in filtered_df.columns
):
    mobility_avg = filtered_df[
        ["retail_and_recreation_percent_change_from_baseline", "grocery_and_pharmacy_percent_change_from_baseline"]
    ].mean(axis=1)

    line3, = ax2.plot(filtered_df["year"], mobility_avg, color="green", linestyle=":", marker="^", label="Avg Mobility % (Retail + Grocery)")
    legend_lines.append(line3)
    legend_labels.append("Avg Mobility % (Retail + Grocery)")

# Temperature trend (centered)
if "temp_centered" in filtered_df.columns and filtered_df["temp_centered"].notna().any():
    line4, = ax2.plot(filtered_df["year"], filtered_df["temp_centered"], color="red", linestyle="-.", marker="D", linewidth=2, label="Avg Temp (°F, Centered)")
    legend_lines.append(line4)
    legend_labels.append("Avg Temp (°F, Centered)")

# Combine legends from both axes
lines1, labels1 = ax.get_legend_handles_labels()
lines_combined = lines1 + legend_lines
labels_combined = labels1 + legend_labels
fig.legend(lines_combined, labels_combined, loc="upper center", bbox_to_anchor=(0.5, 1.1), ncol=2, fontsize="medium", frameon=False)

# Show plot
st.pyplot(fig)

# Footer
st.markdown("*Includes AI forecast (Meta Prophet), CDC flu data, Google mobility trends, and NOAA regional temperatures.*")
st.markdown("Created by **Naomi Oluyemi** | MPH Candidate | *Public Health × AI*")
