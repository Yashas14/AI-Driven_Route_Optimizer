# SmartRoute Pro — ML Demand Forecasting
# Developed by Yashas D and M Shivani Kashyap | Team: TechTriad

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from typing import Tuple

from app.utils.geo import haversine


class DemandForecaster:
    """Gradient Boosting model that predicts delivery demand from geographic features."""

    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
        )
        self.scaler = StandardScaler()
        self._is_fitted = False

    def _build_features(
        self,
        destinations: np.ndarray,
        depots: np.ndarray,
        center: np.ndarray | None = None,
    ) -> np.ndarray:
        """Build feature matrix for each destination.

        Features: lat, lon, dist to nearest depot, dist to 2nd nearest depot,
        dist to centroid, bearing sin/cos to nearest depot, depot accessibility ratio.
        """
        if center is None:
            center = destinations.mean(axis=0)

        features = []
        for dest in destinations:
            dists_to_depots = [haversine(dest[0], dest[1], d[0], d[1]) for d in depots]
            sorted_dists = sorted(dists_to_depots)
            nearest_dist = sorted_dists[0]
            second_nearest = sorted_dists[1] if len(sorted_dists) > 1 else sorted_dists[0]
            dist_to_center = haversine(dest[0], dest[1], center[0], center[1])

            nearest_idx = int(np.argmin(dists_to_depots))
            dlat = depots[nearest_idx][0] - dest[0]
            dlon = depots[nearest_idx][1] - dest[1]
            angle = np.arctan2(dlon, dlat)

            features.append([
                dest[0],
                dest[1],
                nearest_dist,
                second_nearest,
                dist_to_center,
                np.sin(angle),
                np.cos(angle),
                nearest_dist / (second_nearest + 1e-6),
            ])

        return np.array(features)

    def generate_synthetic_demand(
        self,
        destinations: np.ndarray,
        depots: np.ndarray,
        seed: int = 42,
    ) -> np.ndarray:
        """Generate demand values based on proximity to depots with seasonal noise."""
        rng = np.random.RandomState(seed)
        n = len(destinations)
        demands = np.zeros(n)

        for i, dest in enumerate(destinations):
            min_dist = min(haversine(dest[0], dest[1], d[0], d[1]) for d in depots)
            base = max(10, 200 - min_dist * 3)
            noise = rng.normal(0, base * 0.2)
            seasonal = 1.0 + 0.15 * np.sin(2 * np.pi * (dest[0] % 1) * 12)
            demands[i] = max(5, base * seasonal + noise)

        return demands

    def fit(
        self,
        destinations: np.ndarray,
        depots: np.ndarray,
        demands: np.ndarray,
    ) -> dict:
        """Train the model and return cross-validation metrics and feature importances."""
        X = self._build_features(destinations, depots)
        X_scaled = self.scaler.fit_transform(X)

        cv_scores = cross_val_score(self.model, X_scaled, demands, cv=5, scoring="r2")
        self.model.fit(X_scaled, demands)
        self._is_fitted = True

        feature_names = [
            "latitude", "longitude", "dist_nearest_depot",
            "dist_2nd_depot", "dist_centroid", "bearing_sin",
            "bearing_cos", "depot_accessibility",
        ]

        return {
            "cv_r2_mean": round(float(cv_scores.mean()), 4),
            "cv_r2_std": round(float(cv_scores.std()), 4),
            "feature_importances": dict(
                zip(feature_names, [round(float(x), 4) for x in self.model.feature_importances_])
            ),
        }

    def predict(self, destinations: np.ndarray, depots: np.ndarray) -> np.ndarray:
        """Predict demand at each destination."""
        if not self._is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        X = self._build_features(destinations, depots)
        X_scaled = self.scaler.transform(X)
        return np.maximum(0, self.model.predict(X_scaled))

    def fit_and_predict(
        self,
        destinations: np.ndarray,
        depots: np.ndarray,
        seed: int = 42,
    ) -> Tuple[np.ndarray, dict]:
        """Generate synthetic demand, train the model, return predictions and metrics."""
        demands = self.generate_synthetic_demand(destinations, depots, seed)
        metrics = self.fit(destinations, depots, demands)
        predictions = self.predict(destinations, depots)
        return predictions, metrics
