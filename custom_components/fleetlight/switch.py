"""Switch platform: one switch entity per Fleetlight zone.

Turning the switch on/off starts/stops whatever effect was last used (or the
default effect, the first time). `fleetlight.start_effect` additionally lets
you pick the effect and pass tuning params; it's how you actually choose
what plays.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_EFFECT,
    ATTR_PARAMS,
    DEFAULT_EFFECT,
    DOMAIN,
    SERVICE_START_EFFECT,
    SERVICE_STOP_EFFECT,
)
from .effects import EFFECTS
from .engine import ZoneEngine


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    engine: ZoneEngine = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FleetlightZoneSwitch(entry, engine)])

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_START_EFFECT,
        {
            vol.Required(ATTR_EFFECT): vol.In(sorted(EFFECTS)),
            vol.Optional(ATTR_PARAMS, default={}): dict,
        },
        "async_start_effect",
    )
    platform.async_register_entity_service(
        SERVICE_STOP_EFFECT,
        {},
        "async_stop_effect",
    )


class FleetlightZoneSwitch(SwitchEntity):
    """Represents whether an effect is currently running on a zone."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, engine: ZoneEngine) -> None:
        self._entry = entry
        self._engine = engine
        self._attr_unique_id = f"{entry.entry_id}_effect"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Fleetlight",
            model="Zone",
        )
        self._last_effect = DEFAULT_EFFECT
        self._last_params: dict[str, Any] = {}

    @property
    def is_on(self) -> bool:
        return self._engine.is_running

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "effect": self._engine.effect_name,
            "light_count": len(self._engine.zone.light_entity_ids(self.hass)),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.async_start_effect(self._last_effect, self._last_params)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_stop_effect()

    async def async_start_effect(self, effect: str, params: dict[str, Any]) -> None:
        await self._engine.async_start(effect, params)
        self._last_effect = effect
        self._last_params = params
        self.async_write_ha_state()

    async def async_stop_effect(self) -> None:
        await self._engine.async_stop()
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        await self._engine.async_stop()
