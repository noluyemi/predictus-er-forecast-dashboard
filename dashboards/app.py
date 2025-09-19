import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# App setup
st.set_page_config(page_title="PredictUS: Regional ER Forecast", layout="centered")

# forecast + mobility + temp
forecast_df = pd.read_csv("data/processed/all_regions_er_flu_mobility_forecast.csv")
forecast_df.columns = forecast_df.columns.str.strip().str.lower()

# flu data
flu_df = pd.read_csv("data/processed/cdc_ilinet_flu_by_year.csv")
flu_df.columns = flu_df.columns.str.strip().str.lower()
flu_df = flu_df.rename(columns={"average_flu_percent": "avg_flu_percent"})

# Temperature Data
temp_df = pd.read_csv("data/processed/noaa_temp_master.csv")
temp_df = temp_df.rename(columns={"Value": "avg_temp", "Year": "year", "Region": "region"})
temp_df.columns = temp_df.columns.str.strip().str.lower()

# forecast + flu + temp
df = pd.merge(forecast_df, flu_df, on="year", how="left")
df = pd.merge(df, temp_df, on=["year", "region"], how="left")

# Center temperatures
df["temp_centered"] = df["avg_temp"] - df["avg_temp"].mean()

# Title
st.title("PredictUS: U.S. ER Surge Forecast Dashboard")
st.markdown("Forecasting ER visits using AI, flu patterns, mobility behavior, and temperature trends.")

# Sidebar filters
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

filtered_df = region_df[(region_df["year"] >= start_year) & (region_df["year"] <= end_year)].copy()

# Temperature check (safe fallback)
has_temp = "temp_centered" in filtered_df.columns and filtered_df["temp_centered"].notna().any()

if not has_temp:
    st.warning("Temperature data not available for this region and year range.")

# Plot
fig, ax = plt.subplots(figsize=(10, 5))

# Primary: ER Forecast
ax.plot(filtered_df["year"], filtered_df["forecast"], color="steelblue", marker="o", linewidth=2, label="ER Forecast")
ax.fill_between(filtered_df["year"], filtered_df["yhat_lower"], filtered_df["yhat_upper"], color="lightblue", alpha=0.3, label="Confidence Interval")
ax.set_xlabel("Year")
ax.set_ylabel("Estimated ER Visits")
ax.set_title(f"{region_selected} Region: ER Forecast with Flu, Mobility & Temperature Trends ({start_year}–{end_year})")
ax.grid(True)

# Secondary: flu, mobility, temperature
ax2 = ax.twinx()
ax2.set_ylabel("Flu %, Mobility %, Temp (°F, Centered)")

# Legend tracking
legend_lines, legend_labels = ax.get_legend_handles_labels()

# Flu %
if "avg_flu_percent" in filtered_df.columns and filtered_df["avg_flu_percent"].notna().any():
    flu_line, = ax2.plot(
        filtered_df["year"], filtered_df["avg_flu_percent"],
        color="orange", linestyle="--", marker="s", label="Avg Flu %"
    )
    legend_lines.append(flu_line)
    legend_labels.append("Avg Flu %")

# Mobility %
if "retail_and_recreation_percent_change_from_baseline" in filtered_df.columns:
    mobility_avg = filtered_df[
        ["retail_and_recreation_percent_change_from_baseline", "grocery_and_pharmacy_percent_change_from_baseline"]
    ].mean(axis=1)

    mob_line, = ax2.plot(
        filtered_df["year"], mobility_avg,
        color="green", linestyle=":", marker="^", label="Avg Mobility % (Retail + Grocery)"
    )
    legend_lines.append(mob_line)
    legend_labels.append("Avg Mobility % (Retail + Grocery)")

# Temperature °F (only if data is there)
if has_temp:
    temp_line, = ax2.plot(
        filtered_df["year"], filtered_df["temp_centered"],
        color="red", linestyle="-.", marker="D", linewidth=2, label="Avg Temp (°F, Centered)"
    )
    legend_lines.append(temp_line)
    legend_labels.append("Avg Temp (°F, Centered)")

# Combined legend inside the chart
ax.legend(legend_lines, legend_labels, loc="upper left", fontsize="small")

# Show chart
st.pyplot(fig)

# Footer
st.markdown("*Includes Meta Prophet AI forecasts, CDC flu data, Google mobility trends, and NOAA regional temperature insights.*")
st.markdown("Created by **Naomi Oluyemi** | *Public Health × AI*")
