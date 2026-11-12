from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Palette, Rgb
from .viewport import Viewport


class Podium:
    """The wooden reviewing stand in front of the general, hung with scalloped red, white and gold bunting."""

    WOOD: ClassVar[Rgb] = Rgb(150, 96, 52)
    PLANK_SEAM: ClassVar[Rgb] = Rgb(112, 68, 36)
    EDGE: ClassVar[Rgb] = Rgb(186, 128, 76)
    SCALLOPS: ClassVar[tuple[Rgb, ...]] = (Rgb(200, 50, 52), Rgb(245, 240, 230), Palette.GOLD)
    PLANK_HEIGHT: ClassVar[int] = 6
    SCALLOP_MIN_RADIUS: ClassVar[int] = 6
    TASSEL_RADIUS: ClassVar[int] = 2

    def draw(self, canvas: Canvas, viewport: Viewport) -> None:
        desk_y, width, height = viewport.desk_y, viewport.width, viewport.height
        canvas.rect(Palette.OUTLINE, (0, desk_y - 2, width, height - desk_y + 2))
        canvas.rect(self.WOOD, (0, desk_y, width, height - desk_y))
        canvas.rect(self.EDGE, (0, desk_y, width, 2))
        for seam_y in range(desk_y + self.PLANK_HEIGHT, height, self.PLANK_HEIGHT):
            canvas.line(self.PLANK_SEAM, (0, seam_y), (width, seam_y))
        self._draw_scallops(canvas, viewport)

    def _draw_scallops(self, canvas: Canvas, viewport: Viewport) -> None:
        desk_y, width = viewport.desk_y, viewport.width
        radius = max(self.SCALLOP_MIN_RADIUS, viewport.desk_height // 3)
        for layer, color in enumerate(self.SCALLOPS):
            for x in range(-radius, width + radius, radius * 2):
                canvas.lower_half_circle(color, (x + radius, desk_y + 1 + layer * 2), radius - layer * 2)
        for x in range(0, width + radius * 2, radius * 2):
            canvas.circle(Palette.GOLD, (x, desk_y + 2), self.TASSEL_RADIUS)
