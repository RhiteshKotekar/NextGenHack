# train.py
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from lightgbm import LGBMRegressor

# Prophet (optional)
try:
    from prophet import Prophet

    PROPHET_AVAILABLE = True
except Exception:
    PROPHET_AVAILABLE = False

# VADER for reviews
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

DATA_DIR = Path(__file__).parent / "data"
MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)


def limit_rows(df, rows):
    return df.head(rows) if rows is not None else df


# -------------------------------------------------------------
# ORDERS MODEL — Train using Q1–Q3 only
# -------------------------------------------------------------
def train_orders(rows=None):
    df = pd.read_csv(
        DATA_DIR / "orders_sample.csv", parse_dates=["order_date", "delivery_date"]
    )
    df = limit_rows(df, rows)

    df["order_month"] = df["order_date"].dt.month
    df["order_dow"] = df["order_date"].dt.dayofweek

    # Encode categoricals
    for c in ["city", "warehouse_id", "category", "courier_partner", "route_id"]:
        df[c] = pd.factorize(df[c].astype(str))[0]

    # Q1–Q3 filtering
    df = df[df["order_month"] <= 9].copy()
    print(f"[ORDERS] Training on {len(df)} rows from Q1–Q3")

    X = df[
        [
            "order_month",
            "order_dow",
            "city",
            "warehouse_id",
            "category",
            "courier_partner",
            "route_id",
        ]
    ].fillna(0)

    y = df["order_value_inr"].fillna(0)

    # Split inside Q1–Q3 data only
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LGBMRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    rmse = np.sqrt(mean_squared_error(y_test, model.predict(X_test)))
    print(f"[ORDERS] Q1–Q3 RMSE: {rmse:.2f}")

    joblib.dump(model, MODELS_DIR / "model_orders.pkl")
    print("Saved model_orders.pkl\n")


# -------------------------------------------------------------
# SEASONAL MODEL — Train using Q1–Q3 only
# -------------------------------------------------------------
def train_seasonal(rows=None):
    df = pd.read_csv(DATA_DIR / "seasonal_demand.csv", parse_dates=["date"])
    df = limit_rows(df, rows)

    df["month"] = df["date"].dt.month

    # Q1–Q3 filtering
    df = df[df["month"] <= 9].copy()
    print(f"[SEASONAL] Training on {len(df)} rows from Q1–Q3")

    agg = (
        df.groupby("date")["demand_index"]
        .mean()
        .reset_index()
        .rename(columns={"date": "ds", "demand_index": "y"})
    )

    if PROPHET_AVAILABLE:
        m = Prophet(yearly_seasonality=True)
        m.fit(agg)
        joblib.dump(m, MODELS_DIR / "model_seasonal_prophet.pkl")
        print("Saved model_seasonal_prophet.pkl\n")
    else:
        agg["month"] = agg["ds"].dt.month
        agg["dow"] = agg["ds"].dt.dayofweek
        X = agg[["month", "dow"]]
        y = agg["y"]

        model = LGBMRegressor(n_estimators=200, random_state=42)
        model.fit(X, y)
        joblib.dump(model, MODELS_DIR / "model_seasonal_lgbm.pkl")
        print("Saved model_seasonal_lgbm.pkl\n")


# -------------------------------------------------------------
# WAREHOUSE MODEL — Train using Q1–Q3 only
# -------------------------------------------------------------
def train_warehouse(rows=None):
    df = pd.read_csv(DATA_DIR / "warehouse_ops_sample.csv", parse_dates=["date"])
    df = limit_rows(df, rows)

    df["month"] = df["date"].dt.month

    df = df[df["month"] <= 9].copy()
    print(f"[WAREHOUSE] Training on {len(df)} rows from Q1–Q3")

    for c in ["warehouse_id", "shifts"]:
        df[c] = pd.factorize(df[c].astype(str))[0]

    X = df[
        [
            "month",
            "warehouse_id",
            "workforce_available",
            "shifts",
            "storage_cost_per_pallet_inr",
        ]
    ].fillna(0)

    y = df["avg_processing_time_hours"].fillna(df["avg_processing_time_hours"].mean())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LGBMRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    rmse = np.sqrt(mean_squared_error(y_test, model.predict(X_test)))
    print(f"[WAREHOUSE] Q1–Q3 RMSE: {rmse:.2f}")

    joblib.dump(model, MODELS_DIR / "model_warehouse.pkl")
    print("Saved model_warehouse.pkl\n")


# -------------------------------------------------------------
# TRANSPORT MODEL — Train using Q1–Q3 only
# -------------------------------------------------------------
def train_transport(rows=None):
    df = pd.read_csv(DATA_DIR / "transportations_sample.csv")
    df = limit_rows(df, rows)

    # If dataset has NO date column, we cannot filter by month
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.month
        df = df[df["month"] <= 9].copy()
        print(f"[TRANSPORT] Training on {len(df)} rows from Q1–Q3")
    else:
        print(
            "[TRANSPORT] ⚠ No date column → cannot Q1–Q3 filter. Training on ALL rows."
        )

    for c in ["warehouse_id", "city", "courier_partner"]:
        df[c] = pd.factorize(df[c].astype(str))[0]

    X = df[
        [
            "warehouse_id",
            "city",
            "distance_km",
            "fuel_cost_per_km_inr",
            "courier_partner",
            "courier_on_time_rate",
        ]
    ].fillna(0)

    y = df["estimated_transit_hours"].fillna(df["estimated_transit_hours"].mean())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LGBMRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    rmse = np.sqrt(mean_squared_error(y_test, model.predict(X_test)))
    print(f"[TRANSPORT] Q1–Q3 RMSE: {rmse:.2f}")

    joblib.dump(model, MODELS_DIR / "model_transport.pkl")
    print("Saved model_transport.pkl\n")


# -------------------------------------------------------------
# REVIEWS MODEL — No Q1–Q3 filtering needed (sentiment is not seasonal)
# -------------------------------------------------------------
def train_reviews(rows=None):
    df = pd.read_csv(
        DATA_DIR / "customer_reviews_Sample.csv", parse_dates=["review_date"]
    )
    df = limit_rows(df, rows)

    analyzer = SentimentIntensityAnalyzer()
    df["sentiment"] = (
        df["review_text"]
        .fillna("")
        .apply(lambda t: analyzer.polarity_scores(str(t))["compound"])
    )
    agg = df.groupby("review_date")["sentiment"].mean().reset_index()

    joblib.dump(agg, MODELS_DIR / "model_reviews_agg.pkl")
    print("Saved model_reviews_agg.pkl (daily aggregated sentiments)\n")


# -------------------------------------------------------------
# DISPATCHER
# -------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python train.py <model> [rows]")
        print("models: orders, seasonal, warehouse, transport, reviews")
        sys.exit(1)

    model = sys.argv[1]
    rows = int(sys.argv[2]) if len(sys.argv) >= 3 else None

    if model == "orders":
        train_orders(rows)
    elif model == "seasonal":
        train_seasonal(rows)
    elif model == "warehouse":
        train_warehouse(rows)
    elif model == "transport":
        train_transport(rows)
    elif model == "reviews":
        train_reviews(rows)
    else:
        print("Unknown model:", model)


if __name__ == "__main__":
    main()
