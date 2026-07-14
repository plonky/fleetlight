"""Zone model: an ordered sequence of light entities that effects run across."""

from __future__ import annotations

from dataclasses import dataclass, field

from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er


@dataclass
class Zone:
    """An ordered list of light entities belonging to one Fleetlight config entry.

    Manual ordering (explicit entity_id list, set via the config flow) always
    wins. If no manual list is given, the order falls back to every light in
    the chosen HA Area, sorted by entity_id for a stable-but-arbitrary order —
    HA has no native concept of physical position within an area.
    """

    name: str
    area_id: str | None = None
    manual_light_entity_ids: list[str] = field(default_factory=list)

    def light_entity_ids(self, hass: HomeAssistant) -> list[str]:
        if self.manual_light_entity_ids:
            return list(self.manual_light_entity_ids)
        if self.area_id:
            return _lights_in_area(hass, self.area_id)
        return []


def _lights_in_area(hass: HomeAssistant, area_id: str) -> list[str]:
    entity_reg = er.async_get(hass)
    area_reg = ar.async_get(hass)

    if area_reg.async_get_area(area_id) is None:
        return []

    entity_ids = [
        entry.entity_id
        for entry in entity_reg.entities.values()
        if entry.domain == "light" and _entity_area_id(hass, entry) == area_id
    ]
    return sorted(entity_ids)


def _entity_area_id(hass: HomeAssistant, entry: er.RegistryEntry) -> str | None:
    if entry.area_id:
        return entry.area_id
    if entry.device_id:
        device_reg = dr.async_get(hass)
        device = device_reg.async_get(entry.device_id)
        if device:
            return device.area_id
    return None
