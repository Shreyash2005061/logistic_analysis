"""
data_cleaning.py

Cleans the raw delivery dataset:
- drops exact duplicates
- fixes invalid (negative) weight readings
- imputes missing driver experience with the zone-level median
- flags and removes outlier delivery times (>99.5th percentile) as
  likely data entry errors rather than true operational events

Run:
    python data_cleaning.py
Input:  ../data/deliveries_raw.csv
Output: deliveries_clean.csv
"""

import pandas as pd

RAW_PATH = "../data/deliveries_raw.csv"
OUT_PATH = "deliveries_clean.csv"


def clean(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset="order_id", keep="first")
    print(f"Dropped {before - len(df)} duplicate rows")

    # Fix negative/invalid weights (sensor error -> take absolute value)
    df["package_weight_kg"] = df["package_weight_kg"].abs()

    # Impute missing driver experience with the zone median
    df["driver_experience_years"] = df.groupby("zone")["driver_experience_years"] \
        .transform(lambda s: s.fillna(s.median()))

    # Remove extreme delivery-time outliers (data entry errors, not real trips)
    cap = df["delivery_time_min"].quantile(0.995)
    outliers = df[df["delivery_time_min"] > cap]
    print(f"Removing {len(outliers)} outlier rows above {cap:.1f} min")
    df = df[df["delivery_time_min"] <= cap]

    return df.reset_index(drop=True)


if __name__ == "__main__":
    df = pd.read_csv(RAW_PATH)
    clean_df = clean(df)
    clean_df.to_csv(OUT_PATH, index=False)
    print(f"Saved {len(clean_df)} clean rows -> {OUT_PATH}")
