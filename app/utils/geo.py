# SmartRoute Pro — Geographic utilities
# Developed by Yashas D and M Shivani Kashyap | Team: TechTriad

import numpy as np
from typing import Sequence

EARTH_RADIUS_KM = 6371.0


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two lat/lon points."""
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def distance_matrix(points: np.ndarray) -> np.ndarray:
    """Symmetric (N×N) distance matrix in km for an array of (lat, lon) points."""
    n = len(points)
    mat = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = haversine(points[i, 0], points[i, 1], points[j, 0], points[j, 1])
            mat[i, j] = d
            mat[j, i] = d
    return mat


def total_route_distance(route: Sequence[int], dist_matrix: np.ndarray) -> float:
    """Total round-trip distance for a route given a distance matrix."""
    total = 0.0
    for i in range(len(route)):
        total += dist_matrix[route[i], route[(i + 1) % len(route)]]
    return total


def generate_random_points(
    center_lat: float,
    center_lon: float,
    n: int,
    spread: float = 0.5,
    seed: int = 42,
) -> np.ndarray:
    """Generate n random (lat, lon) points around a center using a radial distribution."""
    rng = np.random.RandomState(seed)
    rho = np.sqrt(np.abs(rng.normal(0, spread, n)))
    phi = rng.uniform(0, 2 * np.pi, n)
    lats = rho * np.cos(phi) + center_lat
    lons = rho * np.sin(phi) * 1.5 + center_lon
    return np.column_stack([lats, lons])
