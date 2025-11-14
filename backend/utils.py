# utils.py
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

MODELS_DIR = Path(__file__).parent / "models"


def load_model(name):
    p = MODELS_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"Model {name} not found at {p}")
    return joblib.load(p)


# orders prediction wrapper
def predict_orders_df(df_features):
    model = load_model("model_orders.pkl")
    preds = model.predict(df_features)
    return preds


# seasonal wrapper (Prophet or LGBM)
def predict_seasonal(future_df):
    # tries prophet first
    try:
        m = load_model("model_seasonal_prophet.pkl")
        forecast = m.predict(future_df)  # expects df with ds column
        return forecast[["ds", "yhat"]]
    except Exception:
        m = load_model("model_seasonal_lgbm.pkl")
        # feature columns: month, dow
        future_df["month"] = future_df["ds"].dt.month
        future_df["dow"] = future_df["ds"].dt.dayofweek
        return m.predict(future_df[["month", "dow"]])


# simple insight generator: if predicted increase > threshold => recommend x% stock increase
def generate_stock_insights(predicted_vals, baseline_vals, surge_pct=0.0):
    """
    predicted_vals: array-like predicted order values for next period
    baseline_vals: array-like baseline (e.g., current) order values
    surge_pct: float (0.2 for +20% surge scenario)
    """
    # compute percent change
    baseline = np.array(baseline_vals) + 1e-6
    pred = np.array(predicted_vals) * (1 + surge_pct)
    pct_change = (pred - baseline) / baseline
    # recommend: increase stock by pct_change * 100 (rounded)
    recommendations = []
    for i, change in enumerate(pct_change):
        rec = {"index": i, "predicted_change_pct": float(change * 100)}
        if change > 0.10:
            rec["action"] = f"Increase stock by {round(change*100)}%"
        else:
            rec["action"] = "No urgent change"
        recommendations.append(rec)
    return recommendations
