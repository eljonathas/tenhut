from __future__ import annotations

from ..geometry import Point
from .facade import Facade
from .perspective_grid import PerspectiveGrid
from .side import Side
from .street_life import StreetLife


class Streetscape:
    """The painted street: its facades, the crowd in front of them and the banners hanging from them."""

    def __init__(self, grid: PerspectiveGrid, facades: list[Facade], life: StreetLife) -> None:
        self._grid = grid
        self._facades = facades
        self._life = life

    @property
    def life(self) -> StreetLife:
        return self._life

    def roof_y(self, depth: float, side: Side) -> float:
        """Height of the cornice on ``side`` at ``depth``; the horizon where no building stands."""
        for facade in self._facades:
            if facade.side is side and facade.covers(depth):
                return facade.roof_y(depth)
        return self._grid.horizon_y

    def roof_corner(self, side: Side, near_depth: float) -> Point:
        """The near top corner of the building on ``side`` whose near edge is at ``near_depth``."""
        facade = next(facade for facade in self._facades if facade.side is side and facade.near == near_depth)
        return facade.near_roof_corner()
