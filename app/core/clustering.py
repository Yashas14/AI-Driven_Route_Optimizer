# SmartRoute Pro — Destination clustering and depot assignment
# Developed by Yashas D and M Shivani Kashyap | Team: TechTriad

import numpy as np
from sklearn.cluster import KMeans
from typing import Dict, List, Tuple

from app.utils.geo import haversine


def assign_destinations_to_depots(
    destinations: np.ndarray,
    depots: np.ndarray,
    method: str = "kmeans",
) -> Dict[int, np.ndarray]:
    """Assign each destination to a depot index.

    Returns a dict mapping depot_index -> (K, 2) array of assigned destinations.
    Method is 'kmeans' (weighted) or 'nearest' (simple nearest-depot).
    """
    n_depots = depots.shape[0]

    if method == "kmeans":
        combined = np.vstack([destinations, np.tile(depots, (15, 1))])
        kmeans = KMeans(n_clusters=n_depots, random_state=0, n_init=10).fit(combined)
        labels = kmeans.labels_[: len(destinations)]

        depot_labels = kmeans.predict(depots)
        label_map = {}
        for depot_idx, cluster_label in enumerate(depot_labels):
            label_map[cluster_label] = depot_idx

        for cl in np.unique(labels):
            if cl not in label_map:
                cluster_center = kmeans.cluster_centers_[cl]
                dists = [haversine(cluster_center[0], cluster_center[1], d[0], d[1]) for d in depots]
                label_map[cl] = int(np.argmin(dists))

        mapped_labels = np.array([label_map[l] for l in labels])

    elif method == "nearest":
        mapped_labels = np.zeros(len(destinations), dtype=int)
        for i, dest in enumerate(destinations):
            dists = [haversine(dest[0], dest[1], d[0], d[1]) for d in depots]
            mapped_labels[i] = int(np.argmin(dists))
    else:
        raise ValueError(f"Unknown method: {method}")

    result: Dict[int, np.ndarray] = {}
    for depot_idx in range(n_depots):
        mask = mapped_labels == depot_idx
        if mask.any():
            result[depot_idx] = destinations[mask]

    return result


def split_by_vehicle_capacity(
    destinations: np.ndarray,
    depot: np.ndarray,
    max_per_vehicle: int = 50,
    demands: np.ndarray | None = None,
    vehicle_capacity: float = 2000.0,
) -> List[np.ndarray]:
    """Split destinations into vehicle-sized clusters using KMeans.

    Returns a list of (S, 2) arrays, one per vehicle.
    """
    n = len(destinations)
    if n == 0:
        return []

    if demands is not None:
        n_vehicles = max(1, int(np.ceil(demands.sum() / vehicle_capacity)))
    else:
        n_vehicles = max(1, int(np.ceil(n / max_per_vehicle)))

    if n_vehicles == 1:
        return [destinations]

    augmented = np.vstack([destinations, np.tile(depot, (5, 1))])
    kmeans = KMeans(n_clusters=n_vehicles, random_state=0, n_init=10).fit(augmented)
    labels = kmeans.labels_[:n]

    clusters = []
    for v in range(n_vehicles):
        mask = labels == v
        if mask.any():
            clusters.append(destinations[mask])

    return clusters


def classify_near_far(
    destinations: np.ndarray,
    depot: np.ndarray,
    threshold_km: float = 40.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Split destinations into near and far groups relative to a depot.

    Returns (near_points, far_points).
    """
    dists = np.array([haversine(d[0], d[1], depot[0], depot[1]) for d in destinations])
    near_mask = dists < threshold_km
    near = destinations[near_mask] if near_mask.any() else np.empty((0, 2))
    far = destinations[~near_mask] if (~near_mask).any() else np.empty((0, 2))
    return near, far
