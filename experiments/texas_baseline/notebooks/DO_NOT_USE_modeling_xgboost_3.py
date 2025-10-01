# ============================================
# PredictUS (Texas) — Multivariate Weekly Model
# Forecast horizon: 1-week & 2-weeks ahead
# Target: ILI visit counts (ili_total) as proxy for ER respiratory burden
# Only 2 years of google mobility data 
# ============================================

!pip -q install xgboost

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBRegressor


df = pd.read_csv("predictus_tx_merged.csv", parse_dates=["date"])

# Keep only 
cols = [
    "date", "year", "week",
    "ili_total", "total_patients", "flu_percent",
    "avg_temp",
    "retail", "grocery", "parks", "transit", "workplaces", "residential"
]
df = df[cols].copy()

# Restrict to the period where all 3 sources exist (already checked)
df_full = df.dropna(subset=["ili_total", "flu_percent", "avg_temp", "retail", "grocery",
                            "parks", "transit", "workplaces", "residential"]).copy()

# Safety sort
df_full = df_full.sort_values("date").reset_index(drop=True)

print("Modeling window:", df_full["date"].min(), "to", df_full["date"].max())
print("Rows:", len(df_full))

df_full["ili_total_lag1"] = df_full["ili_total"].shift(1)
df_full["ili_total_lag2"] = df_full["ili_total"].shift(2)
df_full["ili_total_lag3"] = df_full["ili_total"].shift(3)

# lag features & targets
def add_lags(frame, cols_to_lag, lags=(1,2,3)):
    out = frame.copy()
    for c in cols_to_lag:
        for L in lags:
            out[f"{c}_lag{L}"] = out[c].shift(L)
    return out

base_feats = [
    "flu_percent", "avg_temp",
    "retail", "grocery", "parks", "transit", "workplaces", "residential",
    "ili_total"  # <- add target itself so lags are created
]

df_lag = add_lags(df_full, base_feats, lags=(1,2,3))

# Targets: 1-week ahead and 2-weeks ahead ILI counts
df_lag["y_tplus1"] = df_lag["ili_total"].shift(-1)
df_lag["y_tplus2"] = df_lag["ili_total"].shift(-2)

# Drop rows made invalid by shifting
df_lag = df_lag.dropna().reset_index(drop=True)

# Final feature set (use only lags + current levels)
feature_cols = base_feats + [f"{c}_lag{L}" for c in base_feats for L in (1,2,3)]

print("Num features:", len(feature_cols))

# Train/test split via time-aware split
# (last 20% weeks as holdout)
n = len(df_lag)
split_idx = int(n * 0.8)
train = df_lag.iloc[:split_idx].copy()
test  = df_lag.iloc[split_idx:].copy()

def fit_xgb(X_train, y_train):
    # Simple, sensible defaults; trees handle scaling automatically
    model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=500,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42
    )
    model.fit(X_train, y_train)
    return model

def eval_and_plot(model, X_train, y_train, X_test, y_test, test_dates, title_suffix):
    yhat_train = model.predict(X_train)
    yhat_test  = model.predict(X_test)

    mae = mean_absolute_error(y_test, yhat_test)
    r2  = r2_score(y_test, yhat_test)
    print(f"{title_suffix} — Test MAE: {mae:,.0f} | Test R²: {r2:.2f}")

    # Plot
    plt.figure(figsize=(12,5))
    plt.plot(test_dates, y_test, label="Actual ILI visits", lw=2)
    plt.plot(test_dates, yhat_test, "r--", label="Predicted", lw=2)
    plt.title(f"PredictUS Texas — {title_suffix}")
    plt.xlabel("Week")
    plt.ylabel("ILI visit count")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    return yhat_test, mae, r2

# 1-week ahead model
X_train_1 = train[feature_cols]; y_train_1 = train["y_tplus1"]
X_test_1  = test[feature_cols];  y_test_1  = test["y_tplus1"]

m1 = fit_xgb(X_train_1, y_train_1)
yhat1, mae1, r21 = eval_and_plot(
    m1, X_train_1, y_train_1, X_test_1, y_test_1, test["date"], "Forecast +1 week"
)

# 2-weeks ahead model
X_train_2 = train[feature_cols]; y_train_2 = train["y_tplus2"]
X_test_2  = test[feature_cols];  y_test_2  = test["y_tplus2"]

m2 = fit_xgb(X_train_2, y_train_2)
yhat2, mae2, r22 = eval_and_plot(
    m2, X_train_2, y_train_2, X_test_2, y_test_2, test["date"], "Forecast +2 weeks"
)

# Feature importance 

def plot_importance(model, cols, title, importance_type="gain", top_n=25):
    """
    Works whether XGBoost returns 'f0' style keys or real feature names.
    """
    booster = model.get_booster()
    imp = booster.get_score(importance_type=importance_type)

    if not imp:
        print("No importance info found.")
        return

    def map_key(k):
        # Case 1: index-style keys like 'f12'
        if k.startswith("f") and k[1:].isdigit():
            idx = int(k[1:])
            return cols[idx] if 0 <= idx < len(cols) else k
        # Case 2: already a real column name like 'flu_percent_lag3'
        return k

    mapped = {map_key(k): v for k, v in imp.items()}
    s = pd.Series(mapped).sort_values(ascending=True).tail(top_n)

    plt.figure(figsize=(8, 10))
    s.plot(kind="barh")
    plt.title(title)
    plt.xlabel(f"Importance ({importance_type})")
    plt.tight_layout()
    plt.show()

# Re-run
plot_importance(m1, feature_cols, "XGBoost Feature Importance (+1 week)")
plot_importance(m2, feature_cols, "XGBoost Feature Importance (+2 weeks)")


# actual forward forecasts (next 1–2 weeks) using the most recent row as the “last known week”
latest = df_lag.iloc[[-1]][feature_cols]  # last available features
fwd_1w = m1.predict(latest)[0]
fwd_2w = m2.predict(latest)[0]

print("Next-week forecast (ILI visits):", int(round(fwd_1w)))
print("Two-weeks-ahead forecast (ILI visits):", int(round(fwd_2w)))
