"""The Fleetlight integration: a device-agnostic lighting effects engine for Home Assistant."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_AREA_ID, CONF_LIGHT_ENTITY_IDS, DOMAIN, PLATFORMS
from .engine import ZoneEngine
from .zone import Zone


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    zone = Zone(
        name=entry.title,
        area_id=entry.data.get(CONF_AREA_ID),
        manual_light_entity_ids=entry.data.get(CONF_LIGHT_ENTITY_IDS, []),
    )
    engine = ZoneEngine(hass, zone)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = engine

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        engine: ZoneEngine = hass.data[DOMAIN].pop(entry.entry_id)
        await engine.async_stop()
    return unloaded
