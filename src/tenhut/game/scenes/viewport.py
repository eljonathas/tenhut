from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class Viewport:
    """The world canvas size plus the two lines every scene is built around: where the soldier looks."""

    width: int
    height: int
    vanishing_x: int
    horizon_y: int

    DESK_MIN_HEIGHT: ClassVar[int] = 18
    DESK_HEIGHT_FRACTION: ClassVar[float] = 0.2

    @staticmethod
    def desk_height_for(world_height: int) -> int:
        return max(Viewport.DESK_MIN_HEIGHT, int(world_height * Viewport.DESK_HEIGHT_FRACTION))

    @staticmethod
    def desk_top_for(world_height: int) -> int:
        return world_height - Viewport.desk_height_for(world_height)

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height

    @property
    def desk_height(self) -> int:
        return self.desk_height_for(self.height)

    @property
    def desk_y(self) -> int:
        return self.desk_top_for(self.height)

    @property
    def span(self) -> int:
        """Half of the visible width around the vanishing line (the narrower side)."""
        return min(self.vanishing_x, self.width - self.vanishing_x)

    def fitted_to(self, size: tuple[int, int]) -> Viewport:
        return Viewport(size[0], size[1], self.vanishing_x, self.horizon_y)
