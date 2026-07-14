"""Built-in Fleetlight effects."""

from .base import Effect, LightState
from .wave import WaveEffect

EFFECTS: dict[str, type[Effect]] = {
    "wave": WaveEffect,
}

__all__ = ["Effect", "LightState", "EFFECTS"]
