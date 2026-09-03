"""
eda.py

Exploratory analysis of the cleaned delivery dataset. Computes the
three KPIs defined in the strategic plan and saves summary charts.

KPIs:
    1. On-Time Delivery Rate (OTD%) = on-time deliveries / total deliveries
    2. Cost Per Delivery (CPD)      = mean delivery_cost_usd
    3. Vehicle Utilization Rate     = deliveries per vehicle type / total

Run:
    python eda.py
Input:  deliveries_clean.csv
Output: eda_summary.csv, charts/*.png
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

IN_PATH = "deliveries_clean.csv"
CHART_DIR = "charts"

os.makedirs(CHART_DIR, exist_ok=True)


def compute_kpis(df: pd.DataFrame) -> pd.DataFrame:
    otd = df.groupby("zone")["on_time"].mean().rename("on_time_delivery_rate")
    cpd = df.groupby("zone")["delivery_cost_usd"].mean().rename("avg_cost_per_delivery")
    volume = df.groupby("zone")["order_id"].count().rename("delivery_volume")

    summary = pd.concat([otd, cpd, volume], axis=1).reset_index()
    return summary


def plot_charts(df: pd.DataFrame):
    plt.figure(figsize=(7, 4))
    sns.barplot(data=df, x="zone", y="on_time_delivery_rate")
    plt.title("On-Time Delivery Rate by Zone")
    plt.ylabel("OTD Rate")
    plt.tight_layout()
    plt.savefig(f"{CHART_DIR}/otd_by_zone.png")
    plt.close()

    plt.figure(figsize=(7, 4))
    sns.barplot(data=df, x="zone", y="avg_cost_per_delivery")
    plt.title("Average Cost per Delivery by Zone")
    plt.ylabel("USD")
    plt.tight_layout()
    plt.savefig(f"{CHART_DIR}/cost_by_zone.png")
    plt.close()


if __name__ == "__main__":
    df = pd.read_csv(IN_PATH)

    summary = compute_kpis(df)
    summary.to_csv("eda_summary.csv", index=False)
    print(summary)

    # Vehicle utilization (share of total deliveries handled per vehicle type)
    util = (df["vehicle_type"].value_counts(normalize=True) * 100).round(1)
    print("\nVehicle Utilization Rate (% of deliveries):")
    print(util)

    plot_charts(summary)
    print(f"\nCharts saved to ./{CHART_DIR}/")
