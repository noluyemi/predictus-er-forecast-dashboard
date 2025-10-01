import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

df = pd.read_csv("predictus_tx_flu_temp.csv")
df['date'] = pd.to_datetime(df['date'])

df = df.dropna(subset=['flu_percent', 'avg_temp', 'ili_total'])

# Features (flu + weather)
X = df[['flu_percent', 'avg_temp']]
y = df['ili_total']

# Train-test split (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Fit linear regression
linreg = LinearRegression()
linreg.fit(X_train, y_train)

# Predictions
y_pred = linreg.predict(X_test)

# Evaluate
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("Linear Regression Test MAE:", mae)
print("Linear Regression Test R²:", r2)

# actual vs predicted
import matplotlib.pyplot as plt

plt.figure(figsize=(12,6))
plt.plot(df['date'].iloc[-len(y_test):], y_test, label="Actual ER visits (ILI)", color="red")
plt.plot(df['date'].iloc[-len(y_test):], y_pred, label="Predicted ER visits (Linear Regression)", color="blue")
plt.legend()
plt.title("PredictUS Baseline: Linear Regression (Flu + Temp)")
plt.xlabel("Date")
plt.ylabel("ILI Visits")
plt.show()
