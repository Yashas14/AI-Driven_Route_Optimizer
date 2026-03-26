# SmartRoute Pro — FastAPI backend
# Developed by Yashas D and M Shivani Kashyap | Team: TechTriad

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import config
from app.core.tsp_solver import ALGORITHMS
from app.core.vrp_engine import VRPEngine
from app.models.schemas import (
    CompareRequest,
    HealthResponse,
    OptimizationRequest,
    OptimizationResponse,
    RouteResponse,
)

app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="AI-driven multi-depot vehicle route optimizer with ML demand forecasting.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_engine = VRPEngine()


@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        version=config.APP_VERSION,
        algorithms_available=list(ALGORITHMS.keys()),
    )


@app.post("/optimize", response_model=OptimizationResponse)
def optimize(request: OptimizationRequest):
    import numpy as np

    destinations = np.array([[loc.lat, loc.lon] for loc in request.destinations])
    depots = np.array([[loc.lat, loc.lon] for loc in request.depots])

    try:
        result = _engine.optimize(
            destinations=destinations,
            depots=depots,
            algorithm=request.algorithm,
            clustering_method=request.clustering_method,
            vehicle_capacity=request.vehicle_capacity,
            max_stops_per_vehicle=request.max_stops_per_vehicle,
            near_threshold_km=request.near_threshold_km,
            use_demand_forecast=request.use_demand_forecast,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    routes = [
        RouteResponse(
            depot_id=r.depot_id,
            vehicle_id=r.vehicle_id,
            vehicle_type=r.vehicle_type,
            num_stops=r.num_stops,
            distance_km=r.distance_km,
            cost=r.cost.__dict__,
            waypoints=r.waypoints.tolist() if hasattr(r.waypoints, "tolist") else r.waypoints,
        )
        for r in result.routes
    ]

    return OptimizationResponse(
        algorithm=result.algorithm,
        optimization_time_seconds=result.optimization_time_seconds,
        num_depots=result.num_depots,
        num_destinations=result.num_destinations,
        num_vehicles=result.num_vehicles,
        fleet_cost=result.fleet_cost.__dict__,
        demand_forecast=result.demand_forecast,
        routes=routes,
    )


@app.post("/compare")
def compare_algorithms(request: CompareRequest):
    import numpy as np

    destinations = np.array([[loc.lat, loc.lon] for loc in request.destinations])
    depots = np.array([[loc.lat, loc.lon] for loc in request.depots])

    try:
        comparison = _engine.compare_algorithms(
            destinations=destinations,
            depots=depots,
            algorithms=request.algorithms,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return comparison
