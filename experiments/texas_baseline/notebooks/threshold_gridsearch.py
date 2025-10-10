import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, f1_score

os.makedirs("media", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
os.makedirs("config", exist_ok=True)

# Baseline stats 
mean_val = y_test.mean()
std_val = y_test.std()

# Range of k values to test
k_values = np.arange(1.0, 2.6, 0.25)
results = []

for k in k_values:
    threshold = mean_val + k * std_val
    y_true = (y_test > threshold).astype(int)
    y_pred_bin = (y_pred > threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred_bin).ravel()

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0
    f1 = f1_score(y_true, y_pred_bin)
    youden = sensitivity + specificity - 1

    results.append({
        "k": round(k, 2),
        "Threshold": round(threshold, 2),
        "Sensitivity": round(sensitivity, 2),
        "Specificity": round(specificity, 2),
        "PPV": round(ppv, 2),
        "NPV": round(npv, 2),
        "F1_Score": round(f1, 2),
        "Youden": round(youden, 2)
    })

results_df = pd.DataFrame(results)
results_df.to_csv("data/processed/tx_threshold_gridsearch.csv", index=False)

# best cutoffs
opt_youden = results_df.loc[results_df["Youden"].idxmax()]
opt_f1 = results_df.loc[results_df["F1_Score"].idxmax()]

print("=== Threshold Optimization Results ===")
print(results_df)
print("\nBest by Youden Index:\n", opt_youden)
print("\nBest by F1 Score:\n", opt_f1)

# saving best result as config
import json
best_result = {
    "best_youden": opt_youden.to_dict(),
    "best_f1": opt_f1.to_dict()
}
with open("config/tx_threshold_best.json", "w") as f:
    json.dump(best_result, f, indent=2)

# Plot Youden Index & F1-score vs Threshold multiplier (k)
plt.figure(figsize=(10,6))
plt.plot(results_df["k"], results_df["Youden"], marker="o", label="Youden Index", linewidth=2)
plt.plot(results_df["k"], results_df["F1_Score"], marker="s", label="F1 Score", linewidth=2)

best_k = opt_youden["k"]
plt.axvline(best_k, color="gray", linestyle="--", label=f"Optimal k = {best_k:.2f}")

plt.title("Threshold Optimization for Surge Alerts (PredictUS-TX)")
plt.xlabel("Threshold (Mean + k × SD)")
plt.ylabel("Score")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig("media/threshold_optimization_plot.png", dpi=300, bbox_inches="tight")
plt.show()
