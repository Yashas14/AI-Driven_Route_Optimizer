"""Tests for SmartRoute Pro optimization engine."""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.tsp_solver import (
    nearest_neighbor,
    two_opt,
    simulated_annealing,
    genetic_algorithm,
    solve_tsp,
)
from app.core.clustering import (
    assign_destinations_to_depots,
    split_by_vehicle_capacity,
    classify_near_far,
)
from app.core.cost_estimator import estimate_route_cost, total_fleet_cost
from app.core.demand_forecaster import DemandForecaster
from app.core.vrp_engine import VRPEngine
from app.utils.geo import haversine, distance_matrix, generate_random_points


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def small_dist_matrix():
    """5-city distance matrix."""
    points = np.array([
        [48.856, 2.352],   # Paris
        [48.573, 7.752],   # Strasbourg
        [43.296, 5.369],   # Marseille
        [45.764, 4.835],   # Lyon
        [47.218, -1.553],  # Nantes
    ])
    return distance_matrix(points)


@pytest.fixture
def sample_data():
    destinations = generate_random_points(48.856, 2.352, 30, seed=42)
    depots = generate_random_points(48.856, 2.352, 3, spread=0.2, seed=99)
    return destinations, depots


# ---------------------------------------------------------------------------
# Geo Utils
# ---------------------------------------------------------------------------

class TestGeoUtils:
    def test_haversine_same_point(self):
        assert haversine(48.856, 2.352, 48.856, 2.352) == 0.0

    def test_haversine_known_distance(self):
        # Paris to Lyon ~392 km
        d = haversine(48.856, 2.352, 45.764, 4.835)
        assert 380 < d < 400

    def test_distance_matrix_symmetric(self, small_dist_matrix):
        dm = small_dist_matrix
        assert dm.shape == (5, 5)
        np.testing.assert_array_almost_equal(dm, dm.T)
        np.testing.assert_array_equal(np.diag(dm), 0)


# ---------------------------------------------------------------------------
# TSP Solvers
# ---------------------------------------------------------------------------

class TestTSPSolvers:
    def test_nearest_neighbor(self, small_dist_matrix):
        route = nearest_neighbor(small_dist_matrix)
        assert len(route) == 5
        assert len(set(route)) == 5  # all cities visited

    def test_two_opt_improves(self, small_dist_matrix):
        initial = nearest_neighbor(small_dist_matrix)
        from app.utils.geo import total_route_distance
        initial_dist = total_route_distance(initial, small_dist_matrix)
        improved, improved_dist = two_opt(initial, small_dist_matrix)
        assert improved_dist <= initial_dist + 1e-6

    def test_simulated_annealing(self, small_dist_matrix):
        route, dist = simulated_annealing(small_dist_matrix)
        assert len(route) == 5
        assert dist > 0

    def test_genetic_algorithm(self, small_dist_matrix):
        route, dist = genetic_algorithm(
            small_dist_matrix, population_size=20, generations=30
        )
        assert len(route) == 5
        assert dist > 0

    def test_solve_tsp_interface(self, small_dist_matrix):
        for algo in ["nearest_neighbor", "two_opt", "simulated_annealing", "genetic_algorithm"]:
            route, dist = solve_tsp(small_dist_matrix, algorithm=algo)
            assert len(route) == 5

    def test_solve_tsp_invalid_algorithm(self, small_dist_matrix):
        with pytest.raises(ValueError):
            solve_tsp(small_dist_matrix, algorithm="invalid")


# ---------------------------------------------------------------------------
# Clustering
# ---------------------------------------------------------------------------

class TestClustering:
    def test_assign_destinations_kmeans(self, sample_data):
        dests, depots = sample_data
        assignments = assign_destinations_to_depots(dests, depots, "kmeans")
        total = sum(len(v) for v in assignments.values())
        assert total == len(dests)

    def test_assign_destinations_nearest(self, sample_data):
        dests, depots = sample_data
        assignments = assign_destinations_to_depots(dests, depots, "nearest")
        total = sum(len(v) for v in assignments.values())
        assert total == len(dests)

    def test_classify_near_far(self, sample_data):
        dests, depots = sample_data
        near, far = classify_near_far(dests, depots[0], threshold_km=30.0)
        assert len(near) + len(far) == len(dests)

    def test_split_by_vehicle_capacity(self, sample_data):
        dests, depots = sample_data
        clusters = split_by_vehicle_capacity(dests, depots[0], max_per_vehicle=10)
        total = sum(len(c) for c in clusters)
        assert total == len(dests)


# ---------------------------------------------------------------------------
# Cost Estimator
# ---------------------------------------------------------------------------

class TestCostEstimator:
    def test_estimate_route_cost(self):
        cost = estimate_route_cost(100, 10, "truck")
        assert cost.distance_km == 100
        assert cost.fuel_liters > 0
        assert cost.co2_grams > 0
        assert cost.estimated_time_hours > 0

    def test_pickup_cheaper_per_km(self):
        pickup = estimate_route_cost(100, 10, "pickup")
        truck = estimate_route_cost(100, 10, "truck")
        assert pickup.fuel_liters < truck.fuel_liters

    def test_total_fleet_cost(self):
        costs = [estimate_route_cost(100, 10, "truck") for _ in range(3)]
        fleet = total_fleet_cost(costs)
        assert fleet["total_vehicles"] == 3
        assert fleet["total_distance_km"] == 300.0


# ---------------------------------------------------------------------------
# Demand Forecaster
# ---------------------------------------------------------------------------

class TestDemandForecaster:
    def test_generate_synthetic_demand(self, sample_data):
        dests, depots = sample_data
        forecaster = DemandForecaster()
        demands = forecaster.generate_synthetic_demand(dests, depots)
        assert len(demands) == len(dests)
        assert all(d > 0 for d in demands)

    def test_fit_and_predict(self, sample_data):
        dests, depots = sample_data
        forecaster = DemandForecaster()
        predictions, metrics = forecaster.fit_and_predict(dests, depots)
        assert len(predictions) == len(dests)
        assert "cv_r2_mean" in metrics
        assert "feature_importances" in metrics


# ---------------------------------------------------------------------------
# VRP Engine (Integration)
# ---------------------------------------------------------------------------

class TestVRPEngine:
    def test_full_optimization(self, sample_data):
        dests, depots = sample_data
        engine = VRPEngine(algorithm="nearest_neighbor")
        result = engine.optimize(
            dests, depots,
            use_demand_forecast=False,
            max_per_vehicle=15,
        )
        assert len(result.routes) > 0
        assert result.fleet_cost["total_distance_km"] > 0
        summary = result.summary()
        assert "routes" in summary
        assert "fleet_cost" in summary

    def test_compare_algorithms(self, sample_data):
        dests, depots = sample_data
        engine = VRPEngine()
        results = engine.compare_algorithms(
            dests, depots,
            algorithms=["nearest_neighbor", "two_opt"],
        )
        assert len(results) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
