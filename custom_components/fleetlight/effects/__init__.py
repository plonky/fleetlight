"""Built-in Fleetlight effects."""

from .base import Effect, LightState
from .thunderstorm import ThunderstormEffect
from .wave import WaveEffect

EFFECTS: dict[str, type[Effect]] = {
    "wave": WaveEffect,
    "thunderstorm": ThunderstormEffect,
}

__all__ = ["Effect", "LightState", "EFFECTS"]
