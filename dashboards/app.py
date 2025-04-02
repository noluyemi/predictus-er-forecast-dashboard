import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="PredictUS: ER Forecast", layout="centered")

df = pd.read_csv("data/processed/ed_visits_total_by_year.csv")

# Sidebar filters
st.sidebar.header("📅 Filter by Year Range")
start_year = st.sidebar.selectbox("Start Year", sorted(df["Year"].unique()), index=0)
end_year = st.sidebar.selectbox("End Year", sorted(df["Year"].unique()), index=len(df["Year"].unique()) - 1)

# Validate selection
if start_year > end_year:
    st.warning("⚠️ Start year must be before end year.")
else:
        # Prophet forecast
    forecast_df = pd.read_csv("data/processed/prophet_forecast_2016_2025.csv")

    # Filter actual and forecasted data
    actual_df = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]
    forecast_filtered = forecast_df[
        (forecast_df["Year"] >= start_year) & (forecast_df["Year"] <= end_year + 2)
    ]

    # Display dashboard
    st.title("PredictUS: U.S. Emergency Room Forecast")
    st.write(
        "This interactive dashboard uses Prophet (Meta/Facebook's AI model) to forecast U.S. ER visits based on real CDC and HHS data."
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(actual_df["Year"], actual_df["Estimate"], label="Actual Visits", marker="o")
    ax.plot(forecast_filtered["Year"], forecast_filtered["Forecast"], label="Prophet Forecast", linestyle="--", marker="x")
    ax.fill_between(forecast_filtered["Year"],
                    forecast_filtered["Lower Bound"],
                    forecast_filtered["Upper Bound"],
                    alpha=0.3, color='gray', label="Forecast Range")

    ax.set_title(f"ER Visits Forecast ({start_year}–{end_year + 2})")
    ax.set_xlabel("Year")
    ax.set_ylabel("Estimated ER Visits")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.markdown("Created by Naomi Oluyemi | MPH Candidate | Public Health x AI")
