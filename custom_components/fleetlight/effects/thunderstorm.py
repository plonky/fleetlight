"""Thunderstorm effect: stormy blue flicker with occasional lightning flashes."""

from __future__ import annotations

import math
import random
import time

from .base import Effect, LightState


class ThunderstormEffect(Effect):
    """Most lights flicker dim blue in a stormy rhythm; lights occasionally
    flash white/pale yellow at random, simulating lightning.

    Each light flickers on its own independent phase/frequency (derived from
    a per-run random seed) so the storm doesn't look synchronized across the
    zone. Lightning is a per-light, per-time-bucket coin flip, so the number
    of simultaneous flashes scales with light count instead of staying a
    fixed absolute number.
    """

    DEFAULT_PARAMS = {
        "seed": None,  # None -> randomize per run; set explicitly for reproducible tests
        "base_color": (80, 130, 220),
        "flash_color": (255, 250, 220),
        "min_brightness": 15,
        "max_brightness": 90,
        "flash_brightness": 255,
        "flicker_speed": 1.5,  # base flicker frequency (rad/s-ish)
        "jitter_speed": 6.0,  # faster secondary jitter frequency
        "jitter_amount": 0.35,  # jitter's relative weight against base flicker
        "flash_interval": 0.4,  # seconds per lightning-chance time bucket
        "flash_probability": 0.12,  # chance a given light starts a flash in a bucket
        "flash_duration": 0.25,  # seconds for a flash to decay back to base
    }
    TICK_INTERVAL = 0.1

    def __init__(self, params: dict | None = None) -> None:
        super().__init__(params)
        self._seed = self.params["seed"]
        if self._seed is None:
            self._seed = time.time()
        self._light_phases: dict[int, tuple[float, float, float, float]] = {}

    def _phases_for(self, i: int) -> tuple[float, float, float, float]:
        cached = self._light_phases.get(i)
        if cached is not None:
            return cached
        rng = random.Random(f"{self._seed}:{i}")
        phases = (
            rng.uniform(0, 2 * math.pi),  # base flicker phase
            rng.uniform(0, 2 * math.pi),  # jitter phase
            self.params["flicker_speed"] * rng.uniform(0.85, 1.15),
            self.params["jitter_speed"] * rng.uniform(0.85, 1.15),
        )
        self._light_phases[i] = phases
        return phases

    def step(self, t: float, light_count: int) -> list[LightState]:
        if light_count <= 0:
            return []

        base_color = tuple(self.params["base_color"])
        flash_color = tuple(self.params["flash_color"])
        min_b = self.params["min_brightness"]
        max_b = self.params["max_brightness"]
        flash_b = self.params["flash_brightness"]
        flash_interval = self.params["flash_interval"]
        flash_probability = self.params["flash_probability"]
        flash_duration = self.params["flash_duration"]

        states = []
        for i in range(light_count):
            base_phase, jitter_phase, base_freq, jitter_freq = self._phases_for(i)

            base_wave = 0.5 + 0.5 * math.sin(t * base_freq + base_phase)
            jitter_wave = 0.5 + 0.5 * math.sin(t * jitter_freq + jitter_phase)
            flicker_frac = (base_wave + self.params["jitter_amount"] * jitter_wave) / (
                1 + self.params["jitter_amount"]
            )
            brightness = min_b + (max_b - min_b) * flicker_frac
            color = base_color

            bucket = math.floor(t / flash_interval)
            bucket_rng = random.Random(f"{self._seed}:{i}:{bucket}")
            if bucket_rng.random() < flash_probability:
                t_in_bucket = t - bucket * flash_interval
                if t_in_bucket < flash_duration:
                    decay = 1 - (t_in_bucket / flash_duration)
                    brightness = flash_b * decay + brightness * (1 - decay)
                    color = flash_color if decay > 0.5 else base_color

            states.append(
                LightState(on=True, brightness=round(brightness), rgb_color=color)
            )
        return states
