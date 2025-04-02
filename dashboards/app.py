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
    filtered_df = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

    # Forecast model
    X = filtered_df[["Year"]]
    y = filtered_df["Estimate"]
    model = LinearRegression()
    model.fit(X, y)

    future_years = pd.DataFrame({"Year": list(range(start_year, end_year + 3))})
    future_preds = model.predict(future_years)

    # Display dashboard
    st.title("PredictUS: U.S. Emergency Room Forecast")
    st.write(
        "This interactive dashboard forecasts U.S. ER visits using national public health data and AI modeling."
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(filtered_df["Year"], filtered_df["Estimate"], label="Actual Visits", marker="o")
    ax.plot(future_years["Year"], future_preds, label="Forecast", linestyle="--", marker="x")
    ax.set_title(f"ER Visits Forecast ({start_year}–{end_year + 2})")
    ax.set_xlabel("Year")
    ax.set_ylabel("Estimated ER Visits")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.markdown("Created by Naomi Oluyemi | MPH Candidate | Public Health x AI")
