"""Cost, time, and CO₂ emissions estimator for route plans."""

from dataclasses import dataclass
from typing import List

from app.config import config


@dataclass
class RouteCost:
    """Estimated costs for a single vehicle route."""

    vehicle_id: int
    depot_id: int
    vehicle_type: str
    distance_km: float
    fuel_liters: float
    fuel_cost_usd: float
    co2_grams: float
    estimated_time_hours: float
    num_stops: int

    @property
    def co2_kg(self) -> float:
        return self.co2_grams / 1000.0

    def to_dict(self) -> dict:
        return {
            "vehicle_id": self.vehicle_id,
            "depot_id": self.depot_id,
            "vehicle_type": self.vehicle_type,
            "distance_km": round(self.distance_km, 2),
            "fuel_liters": round(self.fuel_liters, 2),
            "fuel_cost_usd": round(self.fuel_cost_usd, 2),
            "co2_kg": round(self.co2_kg, 2),
            "estimated_time_hours": round(self.estimated_time_hours, 2),
            "num_stops": self.num_stops,
        }


def estimate_route_cost(
    distance_km: float,
    num_stops: int,
    vehicle_type: str = "truck",
    depot_id: int = 0,
    vehicle_id: int = 0,
    stop_time_minutes: float = 10.0,
) -> RouteCost:
    """Estimate cost, time, and emissions for a route.

    Parameters
    ----------
    distance_km : total travel distance
    num_stops : number of delivery stops
    vehicle_type : 'pickup' or 'truck'
    stop_time_minutes : average time spent per stop
    """
    vc = config.vehicle

    if vehicle_type == "pickup":
        fuel_rate = vc.PICKUP_FUEL_RATE_L_PER_KM
        co2_rate = vc.PICKUP_CO2_G_PER_KM
        speed = vc.PICKUP_SPEED_KMH
    else:
        fuel_rate = vc.TRUCK_FUEL_RATE_L_PER_KM
        co2_rate = vc.TRUCK_CO2_G_PER_KM
        speed = vc.TRUCK_SPEED_KMH

    fuel = distance_km * fuel_rate
    cost = fuel * vc.FUEL_PRICE_PER_LITER
    co2 = distance_km * co2_rate
    travel_hours = distance_km / speed
    stop_hours = (num_stops * stop_time_minutes) / 60.0

    return RouteCost(
        vehicle_id=vehicle_id,
        depot_id=depot_id,
        vehicle_type=vehicle_type,
        distance_km=distance_km,
        fuel_liters=fuel,
        fuel_cost_usd=cost,
        co2_grams=co2,
        estimated_time_hours=travel_hours + stop_hours,
        num_stops=num_stops,
    )


def total_fleet_cost(routes: List[RouteCost]) -> dict:
    """Aggregate costs across all vehicles in the fleet."""
    return {
        "total_vehicles": len(routes),
        "total_distance_km": round(sum(r.distance_km for r in routes), 2),
        "total_fuel_liters": round(sum(r.fuel_liters for r in routes), 2),
        "total_fuel_cost_usd": round(sum(r.fuel_cost_usd for r in routes), 2),
        "total_co2_kg": round(sum(r.co2_kg for r in routes), 2),
        "total_time_hours": round(sum(r.estimated_time_hours for r in routes), 2),
        "total_stops": sum(r.num_stops for r in routes),
        "avg_distance_per_vehicle_km": round(
            sum(r.distance_km for r in routes) / max(len(routes), 1), 2
        ),
    }
