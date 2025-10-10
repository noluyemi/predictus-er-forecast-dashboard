# --- Surge alert evaluation (parameterized) ---
import os, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

os.makedirs("media", exist_ok=True)
os.makedirs("config", exist_ok=True)

# test frame from existing model variables
df_test = pd.DataFrame({
    "date": df["date"].iloc[-len(y_test):],
    "actual": y_test.values,
    "predicted": y_pred
})

def evaluate_surge(k, y_train, df_test):
    """Compute threshold = mean + k*std (using TRAIN ONLY),
    make alerts, plot, and save metrics + fig to disk."""
    mu, sd = y_train.mean(), y_train.std()
    thr = mu + k * sd

    res = df_test.copy()
    res["actual_alert"] = (res["actual"]    > thr).astype(int)
    res["pred_alert"]   = (res["predicted"] > thr).astype(int)

    tn, fp, fn, tp = confusion_matrix(res["actual_alert"], res["pred_alert"]).ravel()
    sens = tp / (tp + fn) if (tp + fn) else np.nan
    spec = tn / (tn + fp) if (tn + fp) else np.nan
    ppv  = tp / (tp + fp) if (tp + fp) else np.nan
    npvv = tn / (tn + fn) if (tn + fn) else np.nan

    # Plot
    plt.figure(figsize=(12,6))
    plt.plot(res["date"], res["actual"],    color="red",  label="Actual ER Visits")
    plt.plot(res["date"], res["predicted"], color="blue", label="Predicted ER Visits")
    surge_dates = res.loc[res["pred_alert"]==1, "date"]
    plt.scatter(surge_dates, np.full(len(surge_dates), thr),
                color="orange", zorder=5, label="Predicted Surge")
    plt.axhline(thr, color="gray", linestyle="--", label=f"Surge Threshold (k={k:.2f})")
    plt.title(f"PredictUS-TX Surge Detection (k={k:.2f})")
    plt.xlabel("Date"); plt.ylabel("ILI Total (ER visits)"); plt.grid(True, alpha=.3)
    out_png = f"media/tx_surge_detection_k{k:.2f}.png"
    plt.savefig(out_png, dpi=300, bbox_inches="tight"); plt.close()

   # Save
    cfg = {
        "k": float(k),
        "threshold": float(thr),
        "metrics": {
            "sensitivity": float(sens),
            "specificity": float(spec),
            "ppv": float(ppv),
            "npv": float(npvv)
        }
    }
    with open(f"config/tx_threshold_k{k:.2f}.json", "w") as f:
        json.dump(cfg, f, indent=2)

    print(f"k={k:.2f}  thr={thr:.2f}  sens={sens:.2f}  spec={spec:.2f}  PPV={ppv:.2f}  NPV={npvv:.2f}  -> {out_png}")
    return cfg, res

# historical example (k=1.5) and optimized default (k=1.0)
cfg_15, _ = evaluate_surge(1.50, y_train, df_test)
cfg_10, _ = evaluate_surge(1.00, y_train, df_test)   # validated default from grid search
