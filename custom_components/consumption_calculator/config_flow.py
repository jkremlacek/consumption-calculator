from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CONF_CONSUMPTION_SENSOR,
    CONF_DISTRIBUTION_PRICE,
    CONF_ELECTRICITY_PRICE,
    CONF_HOME_SOLAR_SENSOR,
    CONF_SHARING_SENSOR,
    DEFAULT_NAME,
    DOMAIN,
)


class ConsumptionCalculatorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(
                title=DEFAULT_NAME,
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CONSUMPTION_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", multiple=False)
                    ),
                    vol.Required(CONF_SHARING_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", multiple=False)
                    ),
                    vol.Optional(CONF_HOME_SOLAR_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", multiple=False)
                    ),
                    vol.Required(CONF_ELECTRICITY_PRICE): vol.Coerce(float),
                    vol.Required(CONF_DISTRIBUTION_PRICE): vol.Coerce(float),
                }
            ),
            errors=errors,
        )
