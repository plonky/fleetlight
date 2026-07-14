"""Engine tests against real (demo) light entities: effect -> service call -> state."""

import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.fleetlight.engine import ZoneEngine
from custom_components.fleetlight.zone import Zone


async def _setup_demo_lights(hass: HomeAssistant) -> list[str]:
    assert await async_setup_component(hass, "homeassistant", {})
    assert await async_setup_component(hass, "demo", {})
    await hass.async_block_till_done()
    return sorted(hass.states.async_entity_ids("light"))


async def test_engine_start_drives_first_light_to_peak_brightness(
    hass: HomeAssistant,
):
    light_ids = await _setup_demo_lights(hass)
    zone = Zone(name="Test Zone", manual_light_entity_ids=light_ids[:3])
    engine = ZoneEngine(hass, zone)

    # speed=0 freezes the wave center at index 0, so light_ids[0] should
    # settle at max_brightness and stay there.
    await engine.async_start("wave", {"speed": 0.0, "max_brightness": 200})
    await asyncio.sleep(0.25)
    await hass.async_block_till_done()

    assert engine.is_running
    first_light = hass.states.get(light_ids[0])
    assert first_light.attributes.get("brightness") == 200


async def test_engine_stop_halts_further_updates(hass: HomeAssistant):
    light_ids = await _setup_demo_lights(hass)
    zone = Zone(name="Test Zone", manual_light_entity_ids=light_ids[:3])
    engine = ZoneEngine(hass, zone)

    await engine.async_start("wave", {"speed": 5.0})
    await asyncio.sleep(0.2)
    await hass.async_block_till_done()

    await engine.async_stop()
    assert not engine.is_running

    state_after_stop = hass.states.get(light_ids[0])
    await asyncio.sleep(0.2)
    await hass.async_block_till_done()

    assert hass.states.get(light_ids[0]) == state_after_stop


async def test_engine_unknown_effect_raises(hass: HomeAssistant):
    zone = Zone(name="Test Zone", manual_light_entity_ids=[])
    engine = ZoneEngine(hass, zone)

    try:
        await engine.async_start("not-a-real-effect")
        assert False, "expected ValueError"
    except ValueError:
        pass
    assert not engine.is_running
