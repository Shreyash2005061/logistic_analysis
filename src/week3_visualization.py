"""
week3_visualization.py

Week 3 Task: Advanced Data Analysis and Visualization in Logistics

Runs a deeper EDA on the cleaned/preprocessed delivery dataset (Week 1/2
pipeline) and produces the visualizations used in the Week 3 report.
Each chart type is chosen for a specific reason — see the printed
justification next to each save call, and the fuller explanation in
the report.

Run:
    cd data && python generate_sample_data.py
    cd ../src && python data_cleaning.py && python week3_visualization.py
Input:  deliveries_clean.csv (produced by data_cleaning.py)
Output: charts_week3/*.png, week3_summary_stats.csv
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

IN_PATH = "deliveries_clean.csv"
CHART_DIR = "charts_week3"
os.makedirs(CHART_DIR, exist_ok=True)

sns.set_style("whitegrid")
NUMERIC_COLS = ["distance_km", "package_weight_kg", "driver_experience_years",
                 "traffic_index", "delivery_time_min", "delivery_cost_usd"]


# ---------------------------------------------------------------------------
# 1. Descriptive statistics
# ---------------------------------------------------------------------------
def descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    stats = df[NUMERIC_COLS].agg(["mean", "median", "std", "min", "max", "skew"]).T
    stats.to_csv("week3_summary_stats.csv")
    print("=== Descriptive Statistics ===")
    print(stats.round(2))
    return stats


# ---------------------------------------------------------------------------
# 2. Correlation matrix
# ---------------------------------------------------------------------------
def correlation_heatmap(df: pd.DataFrame):
    corr = df[NUMERIC_COLS].corr()
    print("\n=== Correlation Matrix ===")
    print(corr.round(2))

    plt.figure(figsize=(7, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, square=True)
    plt.title("Correlation Matrix — Delivery Metrics")
    plt.tight_layout()
    plt.savefig(f"{CHART_DIR}/01_correlation_heatmap.png", dpi=150)
    plt.close()
    return corr


# ---------------------------------------------------------------------------
# 3. Distribution — histogram + KDE
# ---------------------------------------------------------------------------
def distribution_plot(df: pd.DataFrame):
    plt.figure(figsize=(7, 4.5))
    sns.histplot(df["delivery_time_min"], kde=True, bins=40, color="#4C72B0")
    plt.axvline(df["delivery_time_min"].mean(), color="red", linestyle="--", label="Mean")
    plt.axvline(df["delivery_time_min"].median(), color="green", linestyle="--", label="Median")
    plt.title("Distribution of Delivery Time")
    plt.xlabel("Delivery Time (minutes)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{CHART_DIR}/02_delivery_time_distribution.png", dpi=150)
    plt.close()


# ---------------------------------------------------------------------------
# 4. Distribution across categories — boxplot
# ---------------------------------------------------------------------------
def boxplot_by_zone(df: pd.DataFrame):
    plt.figure(figsize=(7, 4.5))
    sns.boxplot(data=df, x="zone", y="delivery_time_min", hue="zone",
                palette="Set2", legend=False)
    plt.title("Delivery Time Spread by Zone")
    plt.ylabel("Delivery Time (minutes)")
    plt.tight_layout()
    plt.savefig(f"{CHART_DIR}/03_delivery_time_by_zone_boxplot.png", dpi=150)
    plt.close()


# ---------------------------------------------------------------------------
# 5. Relationship between two continuous variables — scatter
# ---------------------------------------------------------------------------
def scatter_distance_cost(df: pd.DataFrame):
    plt.figure(figsize=(7, 4.5))
    sns.scatterplot(data=df, x="distance_km", y="delivery_cost_usd",
                     hue="vehicle_type", alpha=0.5, s=15, palette="deep")
    plt.title("Delivery Cost vs. Distance by Vehicle Type")
    plt.xlabel("Distance (km)")
    plt.ylabel("Delivery Cost (USD)")
    plt.tight_layout()
    plt.savefig(f"{CHART_DIR}/04_cost_vs_distance_scatter.png", dpi=150)
    plt.close()


# ---------------------------------------------------------------------------
# 6. Categorical comparison — bar chart
# ---------------------------------------------------------------------------
def bar_cost_by_vehicle(df: pd.DataFrame):
    avg_cost = df.groupby("vehicle_type")["delivery_cost_usd"].mean().sort_values()
    plt.figure(figsize=(7, 4.5))
    avg_cost.plot(kind="barh", color="#55A868")
    plt.title("Average Delivery Cost by Vehicle Type")
    plt.xlabel("Average Cost (USD)")
    plt.tight_layout()
    plt.savefig(f"{CHART_DIR}/05_avg_cost_by_vehicle_bar.png", dpi=150)
    plt.close()


# ---------------------------------------------------------------------------
# 7. Trend over time-of-day — line chart
# ---------------------------------------------------------------------------
def hourly_trend(df: pd.DataFrame):
    hourly = df.groupby("dispatch_hour").agg(
        avg_delivery_time=("delivery_time_min", "mean"),
        on_time_rate=("on_time", "mean"),
        volume=("order_id", "count"),
    ).reset_index()

    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax2 = ax1.twinx()
    ax1.plot(hourly["dispatch_hour"], hourly["avg_delivery_time"], color="#C44E52", marker="o", label="Avg delivery time")
    ax2.plot(hourly["dispatch_hour"], hourly["on_time_rate"] * 100, color="#4C72B0", marker="s", linestyle="--", label="On-time rate %")
    ax1.set_xlabel("Dispatch Hour")
    ax1.set_ylabel("Avg Delivery Time (min)", color="#C44E52")
    ax2.set_ylabel("On-Time Rate (%)", color="#4C72B0")
    plt.title("Delivery Performance by Dispatch Hour")
    fig.tight_layout()
    plt.savefig(f"{CHART_DIR}/06_hourly_trend.png", dpi=150)
    plt.close()
    return hourly


if __name__ == "__main__":
    df = pd.read_csv(IN_PATH)

    descriptive_stats(df)
    correlation_heatmap(df)
    distribution_plot(df)
    boxplot_by_zone(df)
    scatter_distance_cost(df)
    bar_cost_by_vehicle(df)
    hourly = hourly_trend(df)

    print("\n=== Hourly performance table ===")
    print(hourly.round(2))
    print(f"\nAll charts saved to ./{CHART_DIR}/")
