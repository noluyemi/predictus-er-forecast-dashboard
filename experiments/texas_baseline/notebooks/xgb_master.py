
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score, confusion_matrix, f1_score
from sklearn.model_selection import TimeSeriesSplit

# output folders
os.makedirs("media", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

df = pd.read_csv("predictus_tx_flu_temp.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)
df = df.dropna(subset=['flu_percent', 'ili_total', 'avg_temp']).copy()

print("Dataset shape after dropping NaNs:", df.shape)
print(df.head())

# ===== FEATURE ENGINEERING =====
# seasonal features
df['week_of_year'] = df['date'].dt.isocalendar().week.astype(int)
df['month'] = df['date'].dt.month

# lagged features (using only historical data)
for lag in [1, 2]:
    df[f'flu_lag{lag}'] = df['flu_percent'].shift(lag)
    df[f'temp_lag{lag}'] = df['avg_temp'].shift(lag)
    df[f'ili_lag{lag}'] = df['ili_total'].shift(lag)

df = df.dropna().reset_index(drop=True)

# =====  PREPARE FEATURES AND TARGET =====
feature_cols = [
    'flu_lag1', 'temp_lag1', 'ili_lag1',
    'flu_lag2', 'temp_lag2', 'ili_lag2',
    'week_of_year', 'month'
]

X = df[feature_cols]

# Standardized ILI total (better for detecting surges)
y_standardized = ((df['ili_total'] - df['ili_total'].mean()) / df['ili_total'].std()).values

#  Raw flu percent (more interpretable)
y_raw = df['flu_percent'].values

y = y_standardized 
dates = df['date'].values

print(f"\nRows after lagging: {len(df)}")
print(f"Feature columns: {feature_cols}")

# ===== TIME SERIES CROSS-VALIDATION =====
tscv = TimeSeriesSplit(n_splits=5)
fold_metrics = []
oof_predictions = np.full(len(y), np.nan)
last_fold_data = None

for fold, (train_idx, test_idx) in enumerate(tscv.split(X), start=1):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    # Train model with robust hyperparameters
    model = XGBRegressor(
        objective='reg:squarederror',
        n_estimators=300,
        learning_rate=0.05,
        max_depth=3,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Calculate metrics
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    fold_metrics.append({
        'fold': fold,
        'n_train': len(train_idx),
        'n_test': len(test_idx),
        'MAE': mae,
        'R2': r2
    })

    oof_predictions[test_idx] = y_pred
    last_fold_data = (train_idx, test_idx, model, y_pred, y_test)

# Display results
metrics_df = pd.DataFrame(fold_metrics)
print("\n" + "="*60)
print("TIME SERIES CROSS-VALIDATION RESULTS")
print("="*60)
print(metrics_df.to_string(index=False))
print(f"\nAverage MAE: {metrics_df['MAE'].mean():.4f}")
print(f"Average R²: {metrics_df['R2'].mean():.4f}")

# Save metrics
metrics_df.to_csv("data/processed/tx_timeseriescv_metrics.csv", index=False)

# =====  VISUALIZE LAST FOLD =====
_, test_idx, model, y_pred_last, y_test_last = last_fold_data
dates_test = df['date'].iloc[test_idx]

plt.figure(figsize=(12, 6))
plt.plot(dates_test, y_test_last, label="Actual", color="red", linewidth=2)
plt.plot(dates_test, y_pred_last, label="Predicted", color="blue", linewidth=2, alpha=0.7)
plt.title("Texas: Walk-Forward Last Fold — Actual vs Predicted ILI", fontsize=14, fontweight='bold')
plt.xlabel("Date", fontsize=12)
plt.ylabel("Standardized ILI" if y is y_standardized else "Flu Percent", fontsize=12)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("media/tx_xgb_lastfold.png", dpi=200)
plt.show()

# =====  SURGE THRESHOLD OPTIMIZATION  =====
print("\n" + "="*60)
print("SURGE THRESHOLD OPTIMIZATION")
print("="*60)

train_idx, test_idx, *_ = last_fold_data
y_train_fold = y[train_idx]
mean_train = y_train_fold.mean()
std_train = y_train_fold.std()

k_values = np.arange(1.0, 2.6, 0.25)
threshold_results = []

for k in k_values:
    threshold = mean_train + k * std_train

    # Binary classification: Is it a surge?
    y_true_binary = (y_test_last > threshold).astype(int)
    y_pred_binary = (y_pred_last > threshold).astype(int)

    # confusion matrix metrics
    tn, fp, fn, tp = confusion_matrix(y_true_binary, y_pred_binary).ravel()

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0
    f1 = f1_score(y_true_binary, y_pred_binary) if (tp + fp) > 0 and (tp + fn) > 0 else 0
    youden = sensitivity + specificity - 1

    threshold_results.append({
        'k': round(k, 2),
        'Threshold': round(threshold, 2),
        'Sensitivity': round(sensitivity, 2),
        'Specificity': round(specificity, 2),
        'PPV': round(ppv, 2),
        'NPV': round(npv, 2),
        'F1_Score': round(f1, 2),
        'Youden_Index': round(youden, 2)
    })

threshold_df = pd.DataFrame(threshold_results)
optimal_youden = threshold_df.loc[threshold_df['Youden_Index'].idxmax()]
optimal_f1 = threshold_df.loc[threshold_df['F1_Score'].idxmax()]

print(threshold_df.to_string(index=False))
print("\nOptimal by Youden Index:")
print(optimal_youden.to_string())
print("\nOptimal by F1 Score:")
print(optimal_f1.to_string())

threshold_df.to_csv("data/processed/tx_threshold_optimization.csv", index=False)

# Plot threshold optimization
plt.figure(figsize=(10, 6))
plt.plot(threshold_df['k'], threshold_df['Youden_Index'], marker='o', label='Youden Index', linewidth=2)
plt.plot(threshold_df['k'], threshold_df['F1_Score'], marker='s', label='F1 Score', linewidth=2)
plt.axvline(optimal_youden['k'], color='gray', linestyle='--', alpha=0.7,
            label=f'Optimal k={optimal_youden["k"]:.2f}')
plt.title("Surge Detection Threshold Optimization", fontsize=14, fontweight='bold')
plt.xlabel("k (multiplier of standard deviation)", fontsize=12)
plt.ylabel("Score", fontsize=12)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("media/tx_threshold_optimization.png", dpi=200)
plt.show()

# =====  FEATURE IMPORTANCE =====
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n" + "="*60)
print("FEATURE IMPORTANCE")
print("="*60)
print(feature_importance.to_string(index=False))

plt.figure(figsize=(10, 6))
plt.barh(feature_importance['feature'], feature_importance['importance'])
plt.xlabel('Importance', fontsize=12)
plt.ylabel('Feature', fontsize=12)
plt.title('XGBoost Feature Importance', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig("media/tx_feature_importance.png", dpi=200)
plt.show()

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)
print("All outputs saved to 'media/' and 'data/processed/' folders")



# =====  SURGE VISUALIZATION =====
import numpy as np
import matplotlib.pyplot as plt


# Calculate threshold
threshold = mean_train + optimal_youden['k'] * std_train

# Identify surge weeks
actual_surges = y_test_last > threshold
predicted_surges = y_pred_last > threshold

# Classify predictions
true_positive = actual_surges & predicted_surges  # Correctly predicted surge
false_positive = (~actual_surges) & predicted_surges  # False alarm
false_negative = actual_surges & (~predicted_surges)  # Missed surge
true_negative = (~actual_surges) & (~predicted_surges)  # Correctly predicted normal

# ===== VERSION 1: Clean visualization with shaded regions =====
plt.figure(figsize=(14, 7))

# Plot actual and predicted lines
plt.plot(dates_test, y_test_last, label="Actual ILI", color="darkred", linewidth=2.5, zorder=3)
plt.plot(dates_test, y_pred_last, label="Predicted ILI", color="steelblue", linewidth=2, alpha=0.8, zorder=2)

# Plot threshold line
plt.axhline(threshold, color="black", linestyle="--", linewidth=2,
            label=f"Surge Threshold (k={optimal_youden['k']:.2f})", zorder=1)

# Shade actual surge periods
surge_periods = np.where(actual_surges)[0]
if len(surge_periods) > 0:
    plt.fill_between(dates_test, threshold, y_test_last,
                     where=actual_surges, alpha=0.2, color='red',
                     label='Actual Surge Period', zorder=0)

# Highlight prediction accuracy with scatter points
if np.any(true_positive):
    tp_dates = dates_test[true_positive]
    tp_values = y_pred_last[true_positive]
    plt.scatter(tp_dates, tp_values, color='green', s=100, marker='o',
                label=f'Correct Surge Alert (n={np.sum(true_positive)})',
                edgecolors='darkgreen', linewidth=2, zorder=5)

if np.any(false_positive):
    fp_dates = dates_test[false_positive]
    fp_values = y_pred_last[false_positive]
    plt.scatter(fp_dates, fp_values, color='orange', s=100, marker='X',
                label=f'False Alarm (n={np.sum(false_positive)})',
                edgecolors='darkorange', linewidth=2, zorder=5)

if np.any(false_negative):
    fn_dates = dates_test[false_negative]
    fn_values = y_pred_last[false_negative]
    plt.scatter(fn_dates, fn_values, color='purple', s=100, marker='v',
                label=f'Missed Surge (n={np.sum(false_negative)})',
                edgecolors='darkviolet', linewidth=2, zorder=5)

plt.title("Texas ER Flu Surge Detection — Optimal Threshold Performance",
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel("Date", fontsize=13)
plt.ylabel("Standardized ILI", fontsize=13)
plt.legend(loc='best', fontsize=10, framealpha=0.9)
plt.grid(True, linestyle="--", alpha=0.3)
plt.tight_layout()
plt.savefig("media/tx_surge_detection_performance.png", dpi=200, bbox_inches='tight')
plt.show()

# ===== VERSION 2: Alternative - Side-by-side comparison =====
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# Top panel: Actual values
ax1.plot(dates_test, y_test_last, color="darkred", linewidth=2.5, label="Actual ILI")
ax1.axhline(threshold, color="black", linestyle="--", linewidth=2, label="Threshold")
ax1.fill_between(dates_test, threshold, y_test_last, where=actual_surges,
                 alpha=0.3, color='red', label='Actual Surge')
ax1.set_ylabel("Standardized ILI", fontsize=12)
ax1.set_title("Actual ILI Values & Surge Periods", fontsize=14, fontweight='bold')
ax1.legend(loc='best', fontsize=10)
ax1.grid(True, alpha=0.3)

# Bottom panel: Predicted values with classification
ax2.plot(dates_test, y_pred_last, color="steelblue", linewidth=2.5, label="Predicted ILI")
ax2.axhline(threshold, color="black", linestyle="--", linewidth=2, label="Threshold")

# Color-code predictions by accuracy
if np.any(true_positive):
    ax2.scatter(dates_test[true_positive], y_pred_last[true_positive],
                color='green', s=120, marker='o', label='Correct Alert',
                edgecolors='darkgreen', linewidth=2, zorder=5)
if np.any(false_positive):
    ax2.scatter(dates_test[false_positive], y_pred_last[false_positive],
                color='orange', s=120, marker='X', label='False Alarm',
                edgecolors='darkorange', linewidth=2, zorder=5)
if np.any(false_negative):
    ax2.scatter(dates_test[false_negative], y_pred_last[false_negative],
                color='purple', s=120, marker='v', label='Missed Surge',
                edgecolors='darkviolet', linewidth=2, zorder=5)

ax2.set_xlabel("Date", fontsize=12)
ax2.set_ylabel("Standardized ILI", fontsize=12)
ax2.set_title("Predicted ILI Values & Alert Classification", fontsize=14, fontweight='bold')
ax2.legend(loc='best', fontsize=10)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("media/tx_surge_detection_comparison.png", dpi=200, bbox_inches='tight')
plt.show()

# =====  SUMMARY STATISTICS =====
print("\n" + "="*60)
print("SURGE DETECTION PERFORMANCE SUMMARY")
print("="*60)
print(f"Threshold value: {threshold:.4f}")
print(f"Total test weeks: {len(dates_test)}")
print(f"\nActual surge weeks: {np.sum(actual_surges)}")
print(f"Predicted surge weeks: {np.sum(predicted_surges)}")
print(f"\nTrue Positives (Correct alerts): {np.sum(true_positive)}")
print(f"False Positives (False alarms): {np.sum(false_positive)}")
print(f"False Negatives (Missed surges): {np.sum(false_negative)}")
print(f"True Negatives (Correct normal): {np.sum(true_negative)}")

# Calculate metrics
sensitivity = np.sum(true_positive) / np.sum(actual_surges) if np.sum(actual_surges) > 0 else 0
specificity = np.sum(true_negative) / np.sum(~actual_surges) if np.sum(~actual_surges) > 0 else 0
ppv = np.sum(true_positive) / np.sum(predicted_surges) if np.sum(predicted_surges) > 0 else 0

print(f"\nSensitivity (Recall): {sensitivity:.2%}")
print(f"Specificity: {specificity:.2%}")
print(f"Positive Predictive Value (Precision): {ppv:.2%}")
print("="*60)
