"""Config flow tests: creating a zone, and the no-lights-at-all guard."""

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.fleetlight.const import (
    CONF_AREA_ID,
    CONF_LIGHT_ENTITY_IDS,
    DOMAIN,
)


async def test_create_zone_with_manual_lights(hass: HomeAssistant):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Living Room",
            CONF_LIGHT_ENTITY_IDS: ["light.a", "light.b"],
        },
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Living Room"
    assert result["data"][CONF_LIGHT_ENTITY_IDS] == ["light.a", "light.b"]
    assert result["data"][CONF_AREA_ID] is None


async def test_requires_area_or_lights(hass: HomeAssistant):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": "Empty Zone"}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "no_lights"}


async def test_duplicate_zone_name_aborts(hass: HomeAssistant):
    for _ in range(2):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"name": "Living Room", CONF_LIGHT_ENTITY_IDS: ["light.a"]},
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"
