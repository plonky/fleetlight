"""Config flow for Fleetlight: define a zone as an ordered set of lights."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.util import slugify

from .const import CONF_AREA_ID, CONF_LIGHT_ENTITY_IDS, DOMAIN

CONF_NAME = "name"

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Optional(CONF_AREA_ID): selector.AreaSelector(),
        vol.Optional(CONF_LIGHT_ENTITY_IDS): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="light", multiple=True)
        ),
    }
)


class FleetlightConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle creating a Fleetlight zone.

    A zone's light order defaults to the chosen Area (sorted by entity_id,
    since HA has no native physical ordering); explicitly picking lights
    here overrides that with the exact order they were picked in, which is
    what effects like the wave use to know "which light is next."
    """

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            area_id = user_input.get(CONF_AREA_ID)
            light_entity_ids = user_input.get(CONF_LIGHT_ENTITY_IDS) or []

            if not area_id and not light_entity_ids:
                errors["base"] = "no_lights"
            else:
                await self.async_set_unique_id(slugify(user_input[CONF_NAME]))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_AREA_ID: area_id,
                        CONF_LIGHT_ENTITY_IDS: light_entity_ids,
                    },
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors
        )
