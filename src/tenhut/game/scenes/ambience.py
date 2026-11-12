from __future__ import annotations

from tenhut.core import Phase, Theme

from ..random_source import RandomSource
from .ambient_frame import AmbientFrame
from .birds import Birds
from .clouds import Clouds
from .confetti_burst import ConfettiBurst
from .firework_show import FireworkShow
from .sky import Sky
from .sky_factory import SkyFactory
from .smoke_drift import SmokeDrift
from .starfield import Starfield


class Ambience:
    """Everything shared by all scenes that lives on its own clock: time, clouds, birds, smoke, fireworks, confetti."""

    DEFAULT_WORLD = (280, 180)
    BURST_SHARE = 0.3

    def __init__(self, randomness: RandomSource) -> None:
        self._randomness = randomness
        self._elapsed = 0.0
        self._world = self.DEFAULT_WORLD
        self._clouds = Clouds(randomness)
        self._starfield = Starfield(randomness)
        self._birds = Birds()
        self._smoke = SmokeDrift()
        self._fireworks = FireworkShow()
        self._confetti = ConfettiBurst()
        self._skies = SkyFactory(self._starfield)

    @property
    def randomness(self) -> RandomSource:
        return self._randomness

    @property
    def elapsed(self) -> float:
        return self._elapsed

    @property
    def world(self) -> tuple[int, int]:
        return self._world

    @property
    def clouds(self) -> Clouds:
        return self._clouds

    @property
    def birds(self) -> Birds:
        return self._birds

    @property
    def smoke(self) -> SmokeDrift:
        return self._smoke

    @property
    def fireworks(self) -> FireworkShow:
        return self._fireworks

    @property
    def confetti(self) -> ConfettiBurst:
        return self._confetti

    def frame(self) -> AmbientFrame:
        return AmbientFrame(self._elapsed, self._world[0], self._world[1], self._randomness)

    def sky(self, theme: Theme, phase: Phase) -> Sky:
        return self._skies.create(theme, phase)

    def resize(self, world: tuple[int, int]) -> None:
        self._world = world

    def burst(self, center_x: float | None = None) -> None:
        center = self._world[0] * self.BURST_SHARE if center_x is None else center_x
        self._confetti.throw(center, self._randomness)

    def update(self, dt: float) -> None:
        self._elapsed += dt
        self._clouds.drift(dt, self._world[0])
        self._confetti.fall(dt, self._world[1])
        self._birds.fly(dt, self.frame())
        self._smoke.rise(dt)
        self._fireworks.update(dt, self.frame())
