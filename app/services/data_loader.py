# SmartRoute Pro — Data loading, parsing and export utilities
# Developed by Yashas D and M Shivani Kashyap | Team: TechTriad

import csv
import io
from typing import Tuple

import numpy as np
import pandas as pd

from app.utils.geo import generate_random_points


def generate_demo_data(
    n_destinations: int = 200,
    n_depots: int = 5,
    center_lat: float = 48.8566,
    center_lon: float = 2.3522,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray]:
    """Generate synthetic destinations and depots around a center coordinate."""
    destinations = generate_random_points(center_lat, center_lon, n_destinations, spread=0.5, seed=seed)
    depots = generate_random_points(center_lat, center_lon, n_depots, spread=0.3, seed=seed + 100)
    return destinations, depots


def parse_csv_upload(content: str) -> np.ndarray:
    """Parse uploaded CSV bytes into an (N, 2) lat/lon array.

    Expects columns named 'lat'/'latitude' and 'lon'/'longitude'/'lng'.
    """
    df = pd.read_csv(io.StringIO(content))

    col_map = {}
    for col in df.columns:
        lower = col.lower().strip()
        if lower in ("lat", "latitude"):
            col_map["lat"] = col
        elif lower in ("lon", "lng", "longitude"):
            col_map["lon"] = col

    if "lat" not in col_map or "lon" not in col_map:
        raise ValueError("CSV must contain 'lat'/'latitude' and 'lon'/'longitude' columns")

    return df[[col_map["lat"], col_map["lon"]]].values.astype(float)


def export_routes_csv(routes: list) -> str:
    """Serialize optimized routes to a CSV string for download."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "depot_id", "vehicle_id", "vehicle_type", "stop_number",
        "latitude", "longitude", "distance_km", "fuel_cost_usd", "co2_kg",
    ])

    for route in routes:
        for i, wp in enumerate(route.waypoints):
            writer.writerow([
                route.depot_id,
                route.vehicle_id,
                route.vehicle_type,
                i + 1,
                round(wp[0], 6),
                round(wp[1], 6),
                round(route.distance_km, 2) if i == 0 else "",
                round(route.cost.fuel_cost_usd, 2) if i == 0 else "",
                round(route.cost.co2_kg, 2) if i == 0 else "",
            ])

    return output.getvalue()
