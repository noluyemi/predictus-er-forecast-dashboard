import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="PredictUS: ER Forecast", layout="centered")

st.title("PredictUS: U.S. Emergency Room Visit Forecast")
st.write("""
This dashboard forecasts U.S. emergency department (ED) visit trends using historical data (2016–2022) and a linear regression model.
It aims to support proactive staffing and resource planning in public health systems.
""")

# Load your cleaned data
df = pd.read_csv('data/processed/ed_visits_total_by_year.csv')

# Fit linear model
X = df[['Year']]
y = df['Estimate']
model = LinearRegression()
model.fit(X, y)

# Predict future
future_years = pd.DataFrame({'Year': list(range(2016, 2026))})
future_preds = model.predict(future_years)

# Plot
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df['Year'], df['Estimate'], label='Actual Visits', marker='o')
ax.plot(future_years['Year'], future_preds, label='Forecast (2023–2025)', linestyle='--', marker='x')
ax.set_title('Emergency Department Visits: 2016–2025')
ax.set_xlabel('Year')
ax.set_ylabel('Number of Visits')
ax.legend()
ax.grid(True)
st.pyplot(fig)

st.markdown("Created by Naomi Oluyemi | MPH Candidate | Public Health x AI")
