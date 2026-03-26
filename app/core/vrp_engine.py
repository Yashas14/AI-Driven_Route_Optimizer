# SmartRoute Pro — VRP Engine
# Developed by Yashas D and M Shivani Kashyap | Team: TechTriad
#
# Orchestrates the full multi-depot vehicle routing pipeline:
#   Phase 1 — Demand forecasting (optional, Gradient Boosting ML)
#   Phase 2 — Assign destinations to depots (KMeans / nearest)
#   Phase 3 — Classify near vs far per depot (pickup vs truck)
#   Phase 4 — Split into per-vehicle clusters (capacity-aware KMeans)
#   Phase 5 — Solve TSP per vehicle (NN / 2-Opt / SA / GA)
#   Phase 6 — Estimate fuel cost and CO₂ emissions

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from app.core.clustering import (
    assign_destinations_to_depots,
    classify_near_far,
    split_by_vehicle_capacity,
)
from app.core.cost_estimator import RouteCost, estimate_route_cost, total_fleet_cost
from app.core.demand_forecaster import DemandForecaster
from app.core.tsp_solver import ALGORITHMS, solve_tsp
from app.utils.geo import distance_matrix


@dataclass
class VehicleRoute:
    depot_id: int
    vehicle_id: int
    vehicle_type: str
    waypoints: np.ndarray
    route_indices: List[int]
    distance_km: float
    cost: RouteCost
    depot_location: np.ndarray


@dataclass
class OptimizationResult:
    routes: List[VehicleRoute]
    fleet_cost: dict
    depots: np.ndarray
    destinations: np.ndarray
    depot_assignments: Dict[int, np.ndarray]
    algorithm_used: str
    optimization_time_seconds: float
    demand_metrics: Optional[dict] = None
    demand_predictions: Optional[np.ndarray] = None

    def summary(self) -> dict:
        return {
            "algorithm": self.algorithm_used,
            "optimization_time_seconds": round(self.optimization_time_seconds, 3),
            "num_depots": len(self.depots),
            "num_destinations": len(self.destinations),
            "num_vehicles": len(self.routes),
            "fleet_cost": self.fleet_cost,
            "demand_forecast": self.demand_metrics,
            "routes": [
                {
                    "depot_id": r.depot_id,
                    "vehicle_id": r.vehicle_id,
                    "vehicle_type": r.vehicle_type,
                    "num_stops": len(r.waypoints),
                    "distance_km": round(r.distance_km, 2),
                    "cost": r.cost.to_dict(),
                    "waypoints": r.waypoints.tolist(),
                }
                for r in self.routes
            ],
        }


class VRPEngine:
    """Multi-depot vehicle routing solver with pluggable TSP algorithms."""

    def __init__(self, algorithm: str = "genetic_algorithm"):
        if algorithm not in ALGORITHMS:
            raise ValueError(f"Unknown algorithm: {algorithm}. Choose from {list(ALGORITHMS.keys())}")
        self.algorithm = algorithm
        self.forecaster = DemandForecaster()

    def optimize(
        self,
        destinations: np.ndarray,
        depots: np.ndarray,
        clustering_method: str = "kmeans",
        vehicle_capacity: float = 2000.0,
        max_per_vehicle: int = 50,
        near_threshold_km: float = 40.0,
        use_demand_forecast: bool = True,
    ) -> OptimizationResult:
        """Run the full VRP pipeline and return an OptimizationResult."""
        t0 = time.time()

        demand_metrics = None
        demand_predictions = None
        if use_demand_forecast and len(destinations) > 10:
            demand_predictions, demand_metrics = self.forecaster.fit_and_predict(
                destinations, depots
            )

        depot_assignments = assign_destinations_to_depots(
            destinations, depots, method=clustering_method
        )

        all_routes: List[VehicleRoute] = []
        global_vehicle_id = 0

        for depot_idx in sorted(depot_assignments.keys()):
            depot_dests = depot_assignments[depot_idx]
            depot_loc = depots[depot_idx]
            near, far = classify_near_far(depot_dests, depot_loc, near_threshold_km)

            for group, group_type in [(near, "pickup"), (far, "truck")]:
                if len(group) == 0:
                    continue

                vehicle_clusters = split_by_vehicle_capacity(
                    group, depot_loc, max_per_vehicle, vehicle_capacity=vehicle_capacity
                )

                for cluster_points in vehicle_clusters:
                    if len(cluster_points) < 2:
                        route = VehicleRoute(
                            depot_id=depot_idx,
                            vehicle_id=global_vehicle_id,
                            vehicle_type=group_type,
                            waypoints=cluster_points,
                            route_indices=[0],
                            distance_km=0.0,
                            cost=estimate_route_cost(0, 1, group_type, depot_idx, global_vehicle_id),
                            depot_location=depot_loc,
                        )
                        all_routes.append(route)
                        global_vehicle_id += 1
                        continue

                    all_points = np.vstack([depot_loc.reshape(1, -1), cluster_points])
                    dm = distance_matrix(all_points)
                    route_order, dist = solve_tsp(dm, algorithm=self.algorithm)

                    depot_pos = route_order.index(0)
                    route_order = route_order[depot_pos:] + route_order[:depot_pos]
                    ordered_points = all_points[route_order[1:]]

                    cost = estimate_route_cost(
                        dist, len(cluster_points), group_type, depot_idx, global_vehicle_id
                    )
                    route = VehicleRoute(
                        depot_id=depot_idx,
                        vehicle_id=global_vehicle_id,
                        vehicle_type=group_type,
                        waypoints=ordered_points,
                        route_indices=route_order,
                        distance_km=dist,
                        cost=cost,
                        depot_location=depot_loc,
                    )
                    all_routes.append(route)
                    global_vehicle_id += 1

        fleet = total_fleet_cost([r.cost for r in all_routes])
        elapsed = time.time() - t0

        return OptimizationResult(
            routes=all_routes,
            fleet_cost=fleet,
            depots=depots,
            destinations=destinations,
            depot_assignments=depot_assignments,
            algorithm_used=self.algorithm,
            optimization_time_seconds=elapsed,
            demand_metrics=demand_metrics,
            demand_predictions=demand_predictions,
        )

    def compare_algorithms(
        self,
        destinations: np.ndarray,
        depots: np.ndarray,
        algorithms: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, dict]:
        """Run optimization with several algorithms on the same data and return summaries."""
        if algorithms is None:
            algorithms = list(ALGORITHMS.keys())

        results = {}
        for algo in algorithms:
            engine = VRPEngine(algorithm=algo)
            result = engine.optimize(destinations, depots, use_demand_forecast=False, **kwargs)
            results[algo] = result.summary()

        return results
