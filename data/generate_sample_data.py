"""
generate_sample_data.py

Generates a synthetic last-mile delivery dataset for a mid-size
e-commerce logistics operation. Public real-world datasets for this
exact scenario are limited/restricted (carrier data is proprietary),
so this script builds a realistic stand-in with the same statistical
structure analysts would expect: skewed delivery distances, peak-hour
delay effects, and driver/vehicle variability.

Run:
    python generate_sample_data.py
Output:
    deliveries_raw.csv  (10,000 rows)
"""

import numpy as np
import pandas as pd

np.random.seed(42)

N = 10_000

zones = ["North", "South", "East", "West", "Central"]
vehicle_types = ["Bike", "Van-Small", "Van-Large", "Truck"]

df = pd.DataFrame({
    "order_id": np.arange(100000, 100000 + N),
    "zone": np.random.choice(zones, N, p=[0.22, 0.2, 0.18, 0.18, 0.22]),
    "vehicle_type": np.random.choice(vehicle_types, N, p=[0.3, 0.35, 0.25, 0.1]),
    "distance_km": np.round(np.random.gamma(shape=2.2, scale=3.5, size=N), 2),
    "package_weight_kg": np.round(np.random.exponential(scale=4.0, size=N) + 0.2, 2),
    "dispatch_hour": np.random.choice(range(6, 22), N),
    "driver_experience_years": np.round(np.random.exponential(scale=3.0, size=N), 1),
    "traffic_index": np.round(np.random.uniform(0.5, 3.0, N), 2),  # 1 = normal, >1 = congested
})

# Peak-hour congestion effect (8-10am, 5-8pm)
peak_mask = df["dispatch_hour"].isin([8, 9, 17, 18, 19])
df.loc[peak_mask, "traffic_index"] *= np.random.uniform(1.2, 1.6, peak_mask.sum())

# Simulate delivery time (minutes) as a function of distance, traffic,
# vehicle type, and package weight, plus noise.
vehicle_speed_factor = df["vehicle_type"].map({
    "Bike": 1.4, "Van-Small": 1.0, "Van-Large": 0.85, "Truck": 0.7
})

base_time = (df["distance_km"] * 3.2) / vehicle_speed_factor
traffic_penalty = df["traffic_index"] * 6
weight_penalty = df["package_weight_kg"] * 0.4
experience_bonus = np.clip(df["driver_experience_years"] * -0.5, -8, 0)
noise = np.random.normal(0, 5, N)

df["delivery_time_min"] = np.round(
    base_time + traffic_penalty + weight_penalty + experience_bonus + noise, 1
).clip(lower=5)

# Promised SLA window (minutes) — used to compute on-time delivery
df["sla_window_min"] = np.select(
    [df["distance_km"] <= 5, df["distance_km"] <= 12, df["distance_km"] <= 20],
    [30, 55, 90],
    default=120,
)

df["on_time"] = (df["delivery_time_min"] <= df["sla_window_min"]).astype(int)

# Cost per delivery: fixed dispatch cost + distance cost + vehicle overhead
vehicle_cost_factor = df["vehicle_type"].map({
    "Bike": 0.5, "Van-Small": 0.9, "Van-Large": 1.3, "Truck": 1.8
})
df["delivery_cost_usd"] = np.round(
    2.5 + df["distance_km"] * 0.35 * vehicle_cost_factor
    + np.random.normal(0, 0.4, N).clip(min=-1), 2
)

# Introduce realistic messiness for the cleaning step
missing_idx = np.random.choice(df.index, size=150, replace=False)
df.loc[missing_idx, "driver_experience_years"] = np.nan

dup_rows = df.sample(30, random_state=1)
df = pd.concat([df, dup_rows], ignore_index=True)

neg_idx = np.random.choice(df.index, size=10, replace=False)
df.loc[neg_idx, "package_weight_kg"] *= -1  # bad sensor readings

df.to_csv("deliveries_raw.csv", index=False)
print(f"Generated {len(df)} rows -> deliveries_raw.csv")
