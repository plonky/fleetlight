"""Wave effect: a brightness wave that propagates along a zone's light order."""

from __future__ import annotations

import math

from .base import Effect, LightState


class WaveEffect(Effect):
    """A brightness peak that travels along the zone, looping continuously.

    The wave's width scales with the number of lights (`width_fraction`),
    so it looks like one coherent wave whether the zone has 3 lights or 30,
    rather than staying a fixed number of lights wide.
    """

    DEFAULT_PARAMS = {
        "speed": 3.0,  # positions per second
        "width_fraction": 0.25,  # wave width as a fraction of zone length
        "color": (255, 200, 120),  # warm white
        "min_brightness": 20,
        "max_brightness": 255,
    }
    TICK_INTERVAL = 0.1

    def step(self, t: float, light_count: int) -> list[LightState]:
        if light_count <= 0:
            return []

        speed = self.params["speed"]
        width_fraction = self.params["width_fraction"]
        color = tuple(self.params["color"])
        min_b = self.params["min_brightness"]
        max_b = self.params["max_brightness"]

        center = (t * speed) % light_count
        width = max(1.0, light_count * width_fraction)

        states = []
        for i in range(light_count):
            raw_distance = abs(i - center)
            distance = min(raw_distance, light_count - raw_distance)
            falloff = math.exp(-0.5 * (distance / width) ** 2)
            brightness = round(min_b + (max_b - min_b) * falloff)
            states.append(
                LightState(on=True, brightness=brightness, rgb_color=color)
            )
        return states
