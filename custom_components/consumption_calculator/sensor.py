from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EUR, UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_CONSUMPTION_SENSOR,
    CONF_DISTRIBUTION_PRICE,
    CONF_ELECTRICITY_PRICE,
    CONF_HOME_SOLAR_SENSOR,
    CONF_SHARING_SENSOR,
    DOMAIN,
    SENSOR_ICONS,
)
from .logic import calculate_window

ENTITY_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="energy_from_grid_kW",
        translation_key="energy_from_grid_kW",
        icon=SENSOR_ICONS["energy_from_grid_kW"],
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="energy_from_shared_network_kW",
        translation_key="energy_from_shared_network_kW",
        icon=SENSOR_ICONS["energy_from_shared_network_kW"],
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="energy_from_home_solar_kW",
        translation_key="energy_from_home_solar_kW",
        icon=SENSOR_ICONS["energy_from_home_solar_kW"],
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="grid_energy_15min_kwh",
        translation_key="grid_energy_15min_kwh",
        icon=SENSOR_ICONS["grid_energy_15min_kwh"],
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=3,
    ),
    SensorEntityDescription(
        key="shared_energy_15min_kwh",
        translation_key="shared_energy_15min_kwh",
        icon=SENSOR_ICONS["shared_energy_15min_kwh"],
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=3,
    ),
    SensorEntityDescription(
        key="home_solar_energy_15min_kwh",
        translation_key="home_solar_energy_15min_kwh",
        icon=SENSOR_ICONS["home_solar_energy_15min_kwh"],
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=3,
    ),
    SensorEntityDescription(
        key="current_15min_cost",
        translation_key="current_15min_cost",
        icon=SENSOR_ICONS["current_15min_cost"],
        native_unit_of_measurement=CURRENCY_EUR,
        suggested_display_precision=4,
    ),
    SensorEntityDescription(
        key="current_cost_per_hour",
        translation_key="current_cost_per_hour",
        icon=SENSOR_ICONS["current_cost_per_hour"],
        native_unit_of_measurement=CURRENCY_EUR,
        suggested_display_precision=4,
    ),
)


class ConsumptionCalculatorSensor(SensorEntity):
    """Expose one calculated value for the current 15-minute settlement window."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: dict[str, Any],
        description: SensorEntityDescription,
    ) -> None:
        self.hass = hass
        self.entity_description = description
        self._config = config
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_name = description.translation_key

    @property
    def native_value(self) -> float | None:
        values = self._compute_values()
        key_map = {
            "energy_from_grid_kW": "grid_used_kW",
            "energy_from_shared_network_kW": "shared_used_kW",
            "energy_from_home_solar_kW": "home_solar_used_kW",
            "grid_energy_15min_kwh": "grid_energy_kwh",
            "shared_energy_15min_kwh": "shared_energy_kwh",
            "home_solar_energy_15min_kwh": "home_solar_energy_kwh",
            "current_15min_cost": "total_cost",
            "current_cost_per_hour": "current_cost_per_hour",
        }
        return values.get(key_map.get(self.entity_description.key, self.entity_description.key))

    def _compute_values(self) -> dict[str, float]:
        home_load = _read_numeric_state(self.hass, self._config[CONF_CONSUMPTION_SENSOR])
        shared_available = _read_numeric_state(self.hass, self._config[CONF_SHARING_SENSOR])
        home_solar = _read_numeric_state(
            self.hass,
            self._config.get(CONF_HOME_SOLAR_SENSOR, ""),
        )
        return calculate_window(
            home_load_kW=home_load,
            shared_available_kW=shared_available,
            home_solar_kW=home_solar,
            electricity_price_per_kwh=float(self._config[CONF_ELECTRICITY_PRICE]),
            distribution_price_per_kwh=float(self._config[CONF_DISTRIBUTION_PRICE]),
        )

    @property
    def extra_state_attributes(self) -> dict[str, float]:
        values = self._compute_values()
        return {
            "shared_used_kW": values["shared_used_kW"],
            "home_solar_used_kW": values["home_solar_used_kW"],
            "grid_used_kW": values["grid_used_kW"],
        }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entities = [
        ConsumptionCalculatorSensor(hass, entry.data, description)
        for description in ENTITY_DESCRIPTIONS
    ]
    async_add_entities(entities)


def _read_numeric_state(hass: HomeAssistant, entity_id: str) -> float:
    if not entity_id:
        return 0.0

    state = hass.states.get(entity_id)
    if state is None:
        return 0.0

    try:
        return float(state.state)
    except (TypeError, ValueError):
        return 0.0
