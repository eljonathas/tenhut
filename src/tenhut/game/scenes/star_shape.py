from __future__ import annotations

import math


class StarShape:
    """The outline of a five-pointed star, point up."""

    POINTS = 5

    def __init__(self, outer_radius: float, inner_radius: float) -> None:
        self._outer = outer_radius
        self._inner = inner_radius

    def vertices(self, center_x: float, center_y: float) -> list[tuple[float, float]]:
        vertices = []
        for index in range(2 * self.POINTS):
            radius = self._outer if index % 2 == 0 else self._inner
            angle = -math.pi / 2 + index * math.pi / self.POINTS
            vertices.append((center_x + radius * math.cos(angle), center_y + radius * math.sin(angle)))
        return vertices
