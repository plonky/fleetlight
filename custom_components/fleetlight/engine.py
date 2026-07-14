"""Per-zone effect engine: ticks an Effect and dispatches light service calls."""

from __future__ import annotations

import asyncio
import logging

from homeassistant.core import HomeAssistant

from .const import MIN_COMMAND_INTERVAL
from .effects import EFFECTS, Effect, LightState
from .zone import Zone

_LOGGER = logging.getLogger(__name__)


class ZoneEngine:
    """Runs one Effect against one Zone until stopped.

    Dispatch is serialized with a small delay between individual
    `light.turn_on` calls (`MIN_COMMAND_INTERVAL`) rather than fired
    concurrently, to avoid flooding a Zigbee/WiFi mesh. On a zone with many
    lights that change every tick, this naturally caps the effective frame
    rate below `Effect.TICK_INTERVAL` — real-time accurate, just lower
    frame rate. If that turns out to look bad in practice, revisit with
    batched/concurrent dispatch and a proper rate limiter.
    """

    def __init__(self, hass: HomeAssistant, zone: Zone) -> None:
        self.hass = hass
        self.zone = zone
        self._task: asyncio.Task | None = None
        self._effect: Effect | None = None
        self._effect_name: str | None = None
        self._last_states: dict[str, LightState] = {}

    @property
    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    @property
    def effect_name(self) -> str | None:
        return self._effect_name

    async def async_start(self, effect_name: str, params: dict | None = None) -> None:
        effect_cls = EFFECTS.get(effect_name)
        if effect_cls is None:
            raise ValueError(f"Unknown effect '{effect_name}'")

        await self.async_stop()
        self._effect = effect_cls(params)
        self._effect_name = effect_name
        self._task = self.hass.async_create_background_task(
            self._run(), name=f"fleetlight-{self.zone.name}"
        )

    async def async_stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        self._effect = None
        self._effect_name = None
        self._last_states = {}

    async def _run(self) -> None:
        assert self._effect is not None
        effect = self._effect
        start = self.hass.loop.time()
        while True:
            light_ids = self.zone.light_entity_ids(self.hass)
            if light_ids:
                t = self.hass.loop.time() - start
                states = effect.step(t, len(light_ids))
                await self._dispatch(light_ids, states)
            await asyncio.sleep(effect.TICK_INTERVAL)

    async def _dispatch(
        self, light_ids: list[str], states: list[LightState]
    ) -> None:
        for entity_id, state in zip(light_ids, states):
            if self._last_states.get(entity_id) == state:
                continue
            self._last_states[entity_id] = state
            await self._call_light(entity_id, state)
            if MIN_COMMAND_INTERVAL:
                await asyncio.sleep(MIN_COMMAND_INTERVAL)

    async def _call_light(self, entity_id: str, state: LightState) -> None:
        if not state.on:
            await self.hass.services.async_call(
                "light", "turn_off", {"entity_id": entity_id}, blocking=False
            )
            return

        data: dict = {"entity_id": entity_id}
        if state.brightness is not None:
            data["brightness"] = state.brightness
        if state.rgb_color is not None:
            data["rgb_color"] = list(state.rgb_color)
        await self.hass.services.async_call(
            "light", "turn_on", data, blocking=False
        )
