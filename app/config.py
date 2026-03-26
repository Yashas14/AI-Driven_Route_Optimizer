# SmartRoute Pro — Application configuration
# Developed by Yashas D and M Shivani Kashyap | Team: TechTriad

import os
from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


@dataclass
class VehicleConfig:
    """Default vehicle fleet configuration."""

    PICKUP_CAPACITY_KG: float = 500.0
    TRUCK_CAPACITY_KG: float = 2000.0
    PICKUP_FUEL_RATE_L_PER_KM: float = 0.10
    TRUCK_FUEL_RATE_L_PER_KM: float = 0.18
    PICKUP_CO2_G_PER_KM: float = 230.0
    TRUCK_CO2_G_PER_KM: float = 410.0
    PICKUP_SPEED_KMH: float = 60.0
    TRUCK_SPEED_KMH: float = 45.0
    FUEL_PRICE_PER_LITER: float = 1.75


@dataclass
class OptimizerConfig:
    """Optimization algorithm parameters."""

    # Genetic Algorithm
    GA_POPULATION_SIZE: int = 100
    GA_GENERATIONS: int = 300
    GA_MUTATION_RATE: float = 0.02
    GA_CROSSOVER_RATE: float = 0.85
    GA_ELITISM_COUNT: int = 5

    # Simulated Annealing
    SA_INITIAL_TEMP: float = 10000.0
    SA_COOLING_RATE: float = 0.9995
    SA_MIN_TEMP: float = 1.0

    # 2-Opt
    TWO_OPT_MAX_ITERATIONS: int = 1000

    # Clustering
    NEAR_THRESHOLD_KM: float = 40.0
    MAX_WAYPOINTS_PER_VEHICLE: int = 50


@dataclass
class AppConfig:
    """Main application configuration."""

    APP_NAME: str = "SmartRoute Pro"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Dashboard
    DASHBOARD_PORT: int = 8501

    # Map defaults
    DEFAULT_LAT: float = 48.8566
    DEFAULT_LON: float = 2.3522
    DEFAULT_ZOOM: int = 7

    # Sub-configs
    vehicle: VehicleConfig = field(default_factory=VehicleConfig)
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables."""
        return cls(
            DEBUG=os.getenv("DEBUG", "false").lower() == "true",
            API_HOST=os.getenv("API_HOST", "0.0.0.0"),
            API_PORT=int(os.getenv("API_PORT", "8000")),
            DASHBOARD_PORT=int(os.getenv("DASHBOARD_PORT", "8501")),
        )


config = AppConfig.from_env()
