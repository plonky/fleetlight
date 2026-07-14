"""Base classes shared by all Fleetlight effects."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LightState:
    """Desired state for a single light at a single tick."""

    on: bool = True
    brightness: int | None = None  # 0-255
    rgb_color: tuple[int, int, int] | None = None


class Effect(ABC):
    """A procedural lighting effect that adapts to however many lights it runs across.

    Subclasses implement `step()`, which is pure and stateless with respect
    to wall-clock time: given "seconds since the effect started" and the
    number of lights in the zone, it returns the target state for every
    light, in zone order. The engine owns timing/dispatch; effects only
    describe the pattern.
    """

    #: Default parameter values; overridden per-instance by the `params`
    #: dict passed to `fleetlight.start_effect`.
    DEFAULT_PARAMS: dict[str, Any] = {}

    #: How often, in seconds, the engine should call `step()`.
    TICK_INTERVAL = 0.2

    def __init__(self, params: dict[str, Any] | None = None) -> None:
        self.params = {**self.DEFAULT_PARAMS, **(params or {})}

    @abstractmethod
    def step(self, t: float, light_count: int) -> list[LightState]:
        """Return the target state for each light, in zone order.

        Args:
            t: seconds elapsed since the effect started.
            light_count: number of lights currently in the zone.
        """
