"""
regression_model.py

Predicts delivery_time_min using a linear regression baseline and a
Random Forest for comparison. The predicted time is then compared
against each order's SLA window to flag deliveries at risk of
breaching the promised SLA before dispatch — this is the model a
dispatcher could act on.

Run:
    python regression_model.py
Input:  deliveries_clean.csv
Output: prints model metrics + feature importance
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

IN_PATH = "deliveries_clean.csv"

NUMERIC = ["distance_km", "package_weight_kg", "dispatch_hour",
           "driver_experience_years", "traffic_index"]
CATEGORICAL = ["zone", "vehicle_type"]
TARGET = "delivery_time_min"


def build_pipeline(model):
    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
    ], remainder="passthrough")
    return Pipeline([("prep", preprocessor), ("model", model)])


if __name__ == "__main__":
    df = pd.read_csv(IN_PATH)
    X = df[NUMERIC + CATEGORICAL]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = {
        "LinearRegression": build_pipeline(LinearRegression()),
        "RandomForest": build_pipeline(RandomForestRegressor(n_estimators=200, random_state=42)),
    }

    for name, pipe in models.items():
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        print(f"{name}: MAE={mae:.2f} min, R2={r2:.3f}")

    # Use the best-performing model to flag at-risk deliveries in the test set
    best_model = models["RandomForest"]
    test_df = X_test.copy()
    test_df["actual_time"] = y_test
    test_df["predicted_time"] = best_model.predict(X_test)
    test_df["sla_window_min"] = df.loc[X_test.index, "sla_window_min"]
    test_df["predicted_breach_risk"] = test_df["predicted_time"] > test_df["sla_window_min"]

    risk_rate = test_df["predicted_breach_risk"].mean() * 100
    print(f"\nPredicted SLA breach risk rate on held-out orders: {risk_rate:.1f}%")
    print("Sample flagged orders:")
    print(test_df[test_df["predicted_breach_risk"]].head(5))
