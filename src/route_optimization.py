"""
route_optimization.py

Illustrates the optimization piece of the roadmap: given a depot and
a set of delivery stops for one vehicle/day, sequence the stops to
minimize total travel distance. Uses a nearest-neighbor heuristic as
a fast, explainable baseline — this is what a production system would
benchmark a real solver (e.g. Google OR-Tools VRP) against.

This is illustrative/pseudocode-adjacent, not a production router:
real routing needs road-network distances, not straight-line ones.

Run:
    python route_optimization.py
"""

import numpy as np


def nearest_neighbor_route(depot, stops):
    """
    depot: (x, y) tuple
    stops: list of (order_id, x, y) tuples
    Returns: ordered list of order_ids, total_distance
    """
    remaining = stops.copy()
    route = []
    current = depot
    total_distance = 0.0

    while remaining:
        distances = [np.hypot(current[0] - s[1], current[1] - s[2]) for s in remaining]
        nearest_idx = int(np.argmin(distances))
        nearest = remaining.pop(nearest_idx)
        total_distance += distances[nearest_idx]
        route.append(nearest[0])
        current = (nearest[1], nearest[2])

    # return to depot
    total_distance += np.hypot(current[0] - depot[0], current[1] - depot[1])
    return route, total_distance


if __name__ == "__main__":
    depot = (0.0, 0.0)
    stops = [
        (101, 2.1, 4.3),
        (102, -1.5, 3.0),
        (103, 5.0, 1.2),
        (104, 3.3, -2.8),
        (105, -4.0, -1.0),
        (106, 1.0, 0.5),
    ]

    route, dist = nearest_neighbor_route(depot, stops)
    print("Optimized stop order:", route)
    print(f"Total route distance: {dist:.2f} km (straight-line units)")

    # ---- Pseudocode for the production version ----
    # 1. Pull real road-network distance/time matrix via a mapping API
    #    (e.g. OSRM, Google Distance Matrix).
    # 2. Feed the matrix into OR-Tools RoutingModel with vehicle capacity
    #    and time-window constraints (SLA windows from the dataset).
    # 3. Solve with a metaheuristic (guided local search), time-limited
    #    to fit dispatch operations (e.g. 30s per depot per morning).
    # 4. Compare solver distance/time against this heuristic baseline
    #    to quantify optimization gains before rollout.
