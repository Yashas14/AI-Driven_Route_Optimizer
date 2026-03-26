# SmartRoute Pro — API request/response schemas
# Developed by Yashas D and M Shivani Kashyap | Team: TechTriad

from pydantic import BaseModel, Field
from typing import List, Optional


class Location(BaseModel):
    """A geographic location."""

    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")
    name: Optional[str] = Field(None, description="Location name")
    demand: Optional[float] = Field(None, ge=0, description="Demand weight")


class OptimizationRequest(BaseModel):
    """Request body for route optimization."""

    destinations: List[Location] = Field(..., min_length=2, description="Delivery destinations")
    depots: List[Location] = Field(..., min_length=1, description="Source depots / warehouses")
    algorithm: str = Field("genetic_algorithm", description="TSP algorithm to use")
    clustering_method: str = Field("kmeans", description="Depot assignment method")
    vehicle_capacity: float = Field(2000.0, gt=0, description="Max demand per vehicle (kg)")
    max_stops_per_vehicle: int = Field(50, gt=0, description="Max stops per vehicle")
    near_threshold_km: float = Field(40.0, gt=0, description="Near/far threshold in km")
    use_demand_forecast: bool = Field(True, description="Run ML demand forecasting")

    model_config = {"json_schema_extra": {
        "example": {
            "destinations": [
                {"lat": 48.88, "lon": 2.35, "name": "Paris Central"},
                {"lat": 49.05, "lon": 2.35, "name": "CDG Area"},
            ],
            "depots": [{"lat": 48.85, "lon": 2.35, "name": "Main Depot"}],
            "algorithm": "genetic_algorithm",
        }
    }}


class CompareRequest(BaseModel):
    """Request body for algorithm comparison."""

    destinations: List[Location] = Field(..., min_length=2)
    depots: List[Location] = Field(..., min_length=1)
    algorithms: Optional[List[str]] = Field(None, description="Algorithms to compare (all if None)")


class RouteResponse(BaseModel):
    """Single vehicle route in the response."""

    depot_id: int
    vehicle_id: int
    vehicle_type: str
    num_stops: int
    distance_km: float
    cost: dict
    waypoints: List[List[float]]


class OptimizationResponse(BaseModel):
    """API response for optimization."""

    algorithm: str
    optimization_time_seconds: float
    num_depots: int
    num_destinations: int
    num_vehicles: int
    fleet_cost: dict
    demand_forecast: Optional[dict]
    routes: List[RouteResponse]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str
    algorithms_available: List[str]


class GeocodingRequest(BaseModel):
    """Request to geocode an address."""

    address: str = Field(..., min_length=2, description="Address to geocode")


class GeocodingResponse(BaseModel):
    """Geocoding result."""

    address: str
    lat: float
    lon: float
    display_name: str
