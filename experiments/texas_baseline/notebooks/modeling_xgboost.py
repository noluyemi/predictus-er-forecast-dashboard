# Flu & Temp (10 Year data)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


df = pd.read_csv("predictus_tx_flu_temp.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.dropna(subset=['flu_percent','ili_total','avg_temp']).reset_index(drop=True)

print("Dataset shape after dropping NaNs:", df.shape)
print(df.head())

# lag features
for lag in [1, 2]:
    df[f'flu_lag{lag}'] = df['flu_percent'].shift(lag)
    df[f'temp_lag{lag}'] = df['avg_temp'].shift(lag)
    df[f'ili_lag{lag}']  = df['ili_total'].shift(lag)

# Drop first few rows with NaN lags
df = df.dropna().reset_index(drop=True)

# Features and target
feature_cols = ['flu_percent','avg_temp','flu_lag1','temp_lag1','ili_lag1','flu_lag2','temp_lag2','ili_lag2']
X = df[feature_cols]
y = df['ili_total']

# Train/test split (80/20) 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Training XGBoost
model = XGBRegressor(
    objective='reg:squarederror',
    n_estimators=200,
    learning_rate=0.1,
    max_depth=3,
    random_state=42
)
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Metrics
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"Test MAE: {mae:.2f}")
print(f"Test R²: {r2:.2f}")

# actual vs predicted 
plt.figure(figsize=(10,6))
plt.plot(df['date'].iloc[len(X_train):], y_test, label="Actual ER visits", color="red")
plt.plot(df['date'].iloc[len(X_train):], y_pred, label="Predicted ER visits", color="blue")
plt.legend()
plt.title("XGBoost: Actual vs Predicted ER Visits (Texas, Flu+Temp)")
plt.xlabel("Date")
plt.ylabel("ILI Total (ER visits)")
plt.grid(True)
plt.show()
