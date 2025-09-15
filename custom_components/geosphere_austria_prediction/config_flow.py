"""Config flow for the GeoSphere Austria Prediction integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.zone import DOMAIN as ZONE_DOMAIN
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ZONE
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ZONE): EntitySelector(
            EntitySelectorConfig(domain=ZONE_DOMAIN),
        ),
    }
)


class GeoSphereAustriaPredictionConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GeoSphere Austria Prediction."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_ZONE])
            self._abort_if_unique_id_configured()

            state = self.hass.states.get(user_input[CONF_ZONE])
            return self.async_create_entry(
                title=state.name if state else "GeoSphere-Austria-Prediction",
                data={CONF_ZONE: user_input[CONF_ZONE]},
            )

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)
