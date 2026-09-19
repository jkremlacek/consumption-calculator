from __future__ import annotations

from typing import Any

try:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
except ImportError:  # pragma: no cover - only needed outside a Home Assistant runtime
    ConfigEntry = Any

    class HomeAssistant:  # type: ignore[override]
        pass

from .const import DOMAIN, PLATFORMS


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the component when it is loaded from YAML."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Consumption Calculator from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
