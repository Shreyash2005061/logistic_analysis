"""
clustering.py

Uses K-Means to segment deliveries into operational clusters based on
distance, traffic exposure, and cost — independent of the pre-labeled
zone field. The goal is to discover natural groupings (e.g. "short,
low-traffic, cheap" vs "long, congested, expensive") that can inform
resource allocation, separate from administrative zone boundaries.

Run:
    python clustering.py
Input:  deliveries_clean.csv
Output: deliveries_with_clusters.csv, charts/cluster_scatter.png
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

IN_PATH = "deliveries_clean.csv"
FEATURES = ["distance_km", "traffic_index", "delivery_cost_usd", "delivery_time_min"]


def find_best_k(X_scaled, k_range=range(2, 8)):
    scores = {}
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X_scaled)
        scores[k] = silhouette_score(X_scaled, km.labels_)
    best_k = max(scores, key=scores.get)
    print("Silhouette scores by k:", {k: round(v, 3) for k, v in scores.items()})
    print(f"Selected k = {best_k}")
    return best_k


if __name__ == "__main__":
    df = pd.read_csv(IN_PATH)
    X = df[FEATURES]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    best_k = find_best_k(X_scaled)
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(X_scaled)

    print("\nCluster profile (mean feature values):")
    print(df.groupby("cluster")[FEATURES].mean().round(2))

    df.to_csv("deliveries_with_clusters.csv", index=False)

    plt.figure(figsize=(7, 5))
    plt.scatter(df["distance_km"], df["delivery_cost_usd"], c=df["cluster"], cmap="viridis", alpha=0.5, s=10)
    plt.xlabel("Distance (km)")
    plt.ylabel("Delivery Cost (USD)")
    plt.title(f"Delivery Clusters (k={best_k})")
    plt.tight_layout()
    plt.savefig("charts/cluster_scatter.png")
    print("Saved deliveries_with_clusters.csv and charts/cluster_scatter.png")
