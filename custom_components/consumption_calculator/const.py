from __future__ import annotations

DOMAIN = "consumption_calculator"
PLATFORMS = ["sensor"]

CONF_CONSUMPTION_SENSOR = "consumption_sensor"
CONF_SHARING_SENSOR = "sharing_sensor"
CONF_HOME_SOLAR_SENSOR = "home_solar_sensor"
CONF_ELECTRICITY_PRICE = "electricity_price"
CONF_DISTRIBUTION_PRICE = "distribution_price"

DEFAULT_NAME = "Consumption Calculator"
WINDOW_HOURS = 15 / 60

SENSOR_ICONS = {
    "energy_from_grid_kW": "mdi:transmission-tower",
    "energy_from_shared_network_kW": "mdi:solar-power",
    "energy_from_home_solar_kW": "mdi:solar-panel",
    "grid_energy_15min_kwh": "mdi:meter-electric",
    "shared_energy_15min_kwh": "mdi:flash",
    "home_solar_energy_15min_kwh": "mdi:weather-sunny",
    "current_15min_cost": "mdi:cash",
    "current_cost_per_hour": "mdi:currency-usd",
}
