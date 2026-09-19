from __future__ import annotations

from .const import WINDOW_HOURS


def calculate_window(
    home_load_kW: float,
    shared_available_kW: float,
    home_solar_kW: float = 0.0,
    electricity_price_per_kwh: float = 0.0,
    distribution_price_per_kwh: float = 0.0,
) -> dict[str, float]:
    """Calculate cost allocation for a 15-minute window.

    The energy sources are prioritized in this order:
    1. external shared network
    2. local home solar production
    3. grid
    """
    home_load = max(float(home_load_kW), 0.0)
    shared_available = max(float(shared_available_kW), 0.0)
    home_solar = max(float(home_solar_kW), 0.0)

    shared_used = min(home_load, shared_available)
    remaining_after_shared = max(home_load - shared_used, 0.0)
    home_solar_used = min(remaining_after_shared, home_solar)
    grid_used = max(home_load - shared_used - home_solar_used, 0.0)

    shared_energy_kwh = shared_used * WINDOW_HOURS
    home_solar_energy_kwh = home_solar_used * WINDOW_HOURS
    grid_energy_kwh = grid_used * WINDOW_HOURS

    shared_cost = shared_energy_kwh * distribution_price_per_kwh
    grid_cost = grid_energy_kwh * (
        electricity_price_per_kwh + distribution_price_per_kwh
    )
    total_cost = shared_cost + grid_cost
    per_hour_equivalent = total_cost / WINDOW_HOURS

    return {
        "home_load_kW": home_load,
        "shared_used_kW": shared_used,
        "home_solar_used_kW": home_solar_used,
        "grid_used_kW": grid_used,
        "shared_energy_kwh": shared_energy_kwh,
        "home_solar_energy_kwh": home_solar_energy_kwh,
        "grid_energy_kwh": grid_energy_kwh,
        "shared_cost": shared_cost,
        "grid_cost": grid_cost,
        "total_cost": total_cost,
        "current_cost_per_hour": per_hour_equivalent,
    }
