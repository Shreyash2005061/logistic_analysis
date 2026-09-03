"""
week2_preprocessing.py

Week 2 Task: Data Collection, Cleaning, and Preprocessing for Logistics Analysis

Builds on the Week 1 dataset (data/generate_sample_data.py) and goes deeper
than the Week 1 cleaning script: this module documents and compares multiple
techniques for each preprocessing decision (not just applies one), which is
what the Week 2 report explains and justifies.

Run:
    python data/generate_sample_data.py        # from repo root, if not already run
    cd src && python week2_preprocessing.py
Input:  ../data/deliveries_raw.csv
Output: deliveries_preprocessed.csv (cleaned + both normalized variants)
"""

import pandas as pd
import numpy as np

RAW_PATH = "../data/deliveries_raw.csv"
OUT_PATH = "deliveries_preprocessed.csv"

NUMERIC_COLS = ["distance_km", "package_weight_kg", "driver_experience_years",
                 "traffic_index", "delivery_time_min", "delivery_cost_usd"]


# ---------------------------------------------------------------------------
# 1. Data quality audit — always run this BEFORE deciding how to clean.
# ---------------------------------------------------------------------------
def audit(df: pd.DataFrame) -> None:
    print("=== Data Quality Audit ===")
    print(f"Rows: {len(df)}  Columns: {len(df.columns)}")
    print("\nMissing values per column:")
    print(df.isna().sum()[df.isna().sum() > 0])
    print(f"\nExact duplicate order_ids: {df['order_id'].duplicated().sum()}")
    print(f"Negative package_weight_kg readings: {(df['package_weight_kg'] < 0).sum()}")
    print()


# ---------------------------------------------------------------------------
# 2. Duplicate removal
# ---------------------------------------------------------------------------
def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset="order_id", keep="first")
    print(f"Removed {before - len(df)} duplicate order_id rows")
    return df


# ---------------------------------------------------------------------------
# 3. Invalid-value correction
#    (sensor/entry errors, not missingness — different fix from imputation)
# ---------------------------------------------------------------------------
def fix_invalid_values(df: pd.DataFrame) -> pd.DataFrame:
    n_negative = (df["package_weight_kg"] < 0).sum()
    df["package_weight_kg"] = df["package_weight_kg"].abs()
    print(f"Corrected {n_negative} negative weight readings (took absolute value)")
    return df


# ---------------------------------------------------------------------------
# 4. Missing value handling
#    Two strategies are shown and compared, not just applied blindly:
#      - Median imputation, grouped by zone (robust to skew, keeps zone signal)
#      - Mean imputation (shown for comparison, then rejected — see report)
# ---------------------------------------------------------------------------
def handle_missing_values(df: pd.DataFrame, col: str = "driver_experience_years") -> pd.DataFrame:
    missing_before = df[col].isna().sum()

    mean_fill = df[col].mean()
    median_fill = df[col].median()
    print(f"\n{col}: {missing_before} missing values")
    print(f"  Global mean:   {mean_fill:.2f}")
    print(f"  Global median: {median_fill:.2f}  (chosen — mean is pulled up by a right-skewed distribution)")

    # Grouped median imputation preserves zone-level differences instead of
    # flattening every missing value to one global number.
    df[col] = df.groupby("zone")[col].transform(lambda s: s.fillna(s.median()))

    remaining = df[col].isna().sum()
    if remaining:
        # fallback for a zone that is entirely missing (edge case)
        df[col] = df[col].fillna(df[col].median())
    print(f"  Missing after zone-grouped median imputation: {df[col].isna().sum()}")
    return df


# ---------------------------------------------------------------------------
# 5. Outlier detection — IQR method vs. Z-score method, compared
# ---------------------------------------------------------------------------
def detect_outliers_iqr(series: pd.Series, k: float = 1.5):
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    return (series < lower) | (series > upper), lower, upper


def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0):
    z = (series - series.mean()) / series.std()
    return z.abs() > threshold


def handle_outliers(df: pd.DataFrame, col: str = "delivery_time_min") -> pd.DataFrame:
    iqr_mask, lower, upper = detect_outliers_iqr(df[col])
    z_mask = detect_outliers_zscore(df[col])

    print(f"\nOutlier detection on '{col}':")
    print(f"  IQR method:    {iqr_mask.sum()} flagged  (bounds: {lower:.1f} - {upper:.1f})")
    print(f"  Z-score method: {z_mask.sum()} flagged  (|z| > 3)")
    print("  Using IQR: right-skewed delivery-time data violates the normality")
    print("  assumption behind Z-score, so IQR is the more defensible choice here.")

    # Cap (winsorize) rather than drop — dropping loses legitimate long-distance
    # deliveries; capping keeps the row but bounds the extreme value's influence.
    df[col] = df[col].clip(lower=lower, upper=upper)
    return df


# ---------------------------------------------------------------------------
# 6. Normalization — Min-Max scaling vs. Z-score standardization, both shown
# ---------------------------------------------------------------------------
def min_max_scale(series: pd.Series) -> pd.Series:
    return (series - series.min()) / (series.max() - series.min())


def z_score_standardize(series: pd.Series) -> pd.Series:
    return (series - series.mean()) / series.std()


def normalize(df: pd.DataFrame, cols=("distance_km", "delivery_cost_usd")) -> pd.DataFrame:
    for col in cols:
        df[f"{col}_minmax"] = min_max_scale(df[col])
        df[f"{col}_zscore"] = z_score_standardize(df[col])
    print(f"\nAdded Min-Max and Z-score normalized columns for: {list(cols)}")
    print("Min-Max used for the clustering/optimization inputs (bounded [0,1],")
    print("comparable scale). Z-score kept for the regression model, which")
    print("does not require a bounded range and benefits from centered features.")
    return df


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    df = pd.read_csv(RAW_PATH)

    audit(df)
    df = remove_duplicates(df)
    df = fix_invalid_values(df)
    df = handle_missing_values(df)
    df = handle_outliers(df)
    df = normalize(df)

    print(f"\nFinal shape: {df.shape}")
    df.to_csv(OUT_PATH, index=False)
    print(f"Saved -> {OUT_PATH}")
