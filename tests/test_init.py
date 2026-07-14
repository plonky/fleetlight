"""End-to-end: config entry -> switch entity -> services -> real light state."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.fleetlight.const import (
    CONF_AREA_ID,
    CONF_LIGHT_ENTITY_IDS,
    DOMAIN,
)


async def _setup_demo_lights(hass: HomeAssistant) -> list[str]:
    assert await async_setup_component(hass, "homeassistant", {})
    assert await async_setup_component(hass, "demo", {})
    await hass.async_block_till_done()
    return sorted(hass.states.async_entity_ids("light"))


async def _setup_zone_entry(hass: HomeAssistant, light_ids: list[str]) -> str:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Zone",
        data={CONF_AREA_ID: None, CONF_LIGHT_ENTITY_IDS: light_ids},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry.entry_id


def _fleetlight_switch_entity_id(hass: HomeAssistant, entry_id: str) -> str:
    entity_reg = er.async_get(hass)
    for entry in entity_reg.entities.values():
        if entry.domain == "switch" and entry.config_entry_id == entry_id:
            return entry.entity_id
    raise AssertionError("no fleetlight switch entity found")


async def test_switch_entity_created_and_off_by_default(hass: HomeAssistant):
    light_ids = await _setup_demo_lights(hass)
    entry_id = await _setup_zone_entry(hass, light_ids[:2])

    switch_entity_id = _fleetlight_switch_entity_id(hass, entry_id)
    assert hass.states.get(switch_entity_id).state == "off"


async def test_start_effect_service_turns_switch_on(hass: HomeAssistant):
    light_ids = await _setup_demo_lights(hass)
    entry_id = await _setup_zone_entry(hass, light_ids[:2])
    switch_entity_id = _fleetlight_switch_entity_id(hass, entry_id)

    await hass.services.async_call(
        DOMAIN,
        "start_effect",
        {
            "entity_id": switch_entity_id,
            "effect": "wave",
            "params": {"speed": 0.0},
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    assert hass.states.get(switch_entity_id).state == "on"
    assert hass.states.get(switch_entity_id).attributes["effect"] == "wave"


async def test_stop_effect_service_turns_switch_off(hass: HomeAssistant):
    light_ids = await _setup_demo_lights(hass)
    entry_id = await _setup_zone_entry(hass, light_ids[:2])
    switch_entity_id = _fleetlight_switch_entity_id(hass, entry_id)

    await hass.services.async_call(
        DOMAIN,
        "start_effect",
        {"entity_id": switch_entity_id, "effect": "wave"},
        blocking=True,
    )
    await hass.services.async_call(
        DOMAIN,
        "stop_effect",
        {"entity_id": switch_entity_id},
        blocking=True,
    )
    await hass.async_block_till_done()

    assert hass.states.get(switch_entity_id).state == "off"


async def test_native_switch_turn_on_uses_default_effect(hass: HomeAssistant):
    light_ids = await _setup_demo_lights(hass)
    entry_id = await _setup_zone_entry(hass, light_ids[:2])
    switch_entity_id = _fleetlight_switch_entity_id(hass, entry_id)

    await hass.services.async_call(
        "switch",
        "turn_on",
        {"entity_id": switch_entity_id},
        blocking=True,
    )
    await hass.async_block_till_done()

    assert hass.states.get(switch_entity_id).state == "on"
    assert hass.states.get(switch_entity_id).attributes["effect"] == "wave"


async def test_unload_entry_stops_engine(hass: HomeAssistant):
    light_ids = await _setup_demo_lights(hass)
    entry_id = await _setup_zone_entry(hass, light_ids[:2])
    switch_entity_id = _fleetlight_switch_entity_id(hass, entry_id)

    await hass.services.async_call(
        DOMAIN,
        "start_effect",
        {"entity_id": switch_entity_id, "effect": "wave"},
        blocking=True,
    )
    engine = hass.data[DOMAIN][entry_id]
    assert engine.is_running

    assert await hass.config_entries.async_unload(entry_id)
    await hass.async_block_till_done()

    assert not engine.is_running
