"""Tests for Zone light ordering: manual override vs area-derived default."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import entity_registry as er

from custom_components.fleetlight.zone import Zone


async def test_manual_order_wins_over_area(hass: HomeAssistant):
    zone = Zone(
        name="Porch",
        area_id="does-not-matter",
        manual_light_entity_ids=["light.c", "light.a", "light.b"],
    )
    assert zone.light_entity_ids(hass) == ["light.c", "light.a", "light.b"]


async def test_area_derived_order_when_no_manual_list(hass: HomeAssistant):
    area_reg = ar.async_get(hass)
    entity_reg = er.async_get(hass)

    area = area_reg.async_get_or_create("Porch")
    for object_id in ("z_light", "a_light", "m_light"):
        entity_reg.async_get_or_create(
            "light",
            "test",
            f"unique_{object_id}",
            suggested_object_id=object_id,
        )
        entity_reg.async_update_entity(
            f"light.{object_id}", area_id=area.id
        )

    zone = Zone(name="Porch", area_id=area.id)

    assert zone.light_entity_ids(hass) == [
        "light.a_light",
        "light.m_light",
        "light.z_light",
    ]


async def test_unknown_area_returns_empty(hass: HomeAssistant):
    zone = Zone(name="Nowhere", area_id="nonexistent")
    assert zone.light_entity_ids(hass) == []


async def test_no_area_no_manual_returns_empty(hass: HomeAssistant):
    zone = Zone(name="Empty")
    assert zone.light_entity_ids(hass) == []
