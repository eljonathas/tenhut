from __future__ import annotations

import pygame

from tenhut.core import Profile
from tenhut.game.animations import Lettering
from tenhut.game.geometry import Point
from tenhut.i18n import t
from tenhut.ui.painting import TextAlign, TextStyle, UiCanvas, UiPalette


class RankPlate:
    """The small career plate in the corner: rank chevrons, rank name, XP and the bar to the next rank."""

    SIZE = (132, 24)
    CHEVRONS_PER_ROW = 3
    CHEVRON_X = 5
    CHEVRON_Y = 5
    CHEVRON_STEP = 4
    CHEVRON_HEIGHT = 3
    CHEVRON_WIDTH = 4
    SHADE_OFFSET = 4
    SHADE_HEIGHT = 3
    TEXT_X = 19
    BAR_SIZE = (78, 4)
    BAR_Y = 15
    XP_MARGIN = 4
    NAME_GAP = 8

    def __init__(self, profile: Profile) -> None:
        self._profile = profile

    def draw(self, canvas: UiCanvas, position: Point) -> None:
        plate = pygame.Rect(position, self.SIZE)
        shapes = canvas.shapes
        shapes.rect(UiPalette.INK, plate.move(0, 2))
        shapes.rect(UiPalette.INK, plate)
        shapes.rect(UiPalette.WOOD, plate.inflate(-2, -2))
        shapes.rect(
            UiPalette.WOOD_DARK, (plate.x + 1, plate.bottom - self.SHADE_OFFSET, plate.w - 2, self.SHADE_HEIGHT)
        )
        self._draw_chevrons(canvas, plate)
        xp_text = self._xp_text()
        self._draw_name(canvas, plate, xp_text)
        bar = pygame.Rect(plate.x + self.TEXT_X, plate.y + self.BAR_Y, *self.BAR_SIZE)
        shapes.rect(UiPalette.WOOD_DARK, bar)
        shapes.rect(UiPalette.YELLOW, (bar.x, bar.y, int(bar.w * self._profile.progress), bar.h))
        canvas.write(
            xp_text,
            Point(plate.right - self.XP_MARGIN, plate.y + 2),
            TextStyle(canvas.fonts.small, UiPalette.PLATE_TEXT, TextAlign.RIGHT),
        )

    def _xp_text(self) -> str:
        upcoming = self._profile.next_rank
        return f"{self._profile.xp}" + (f"/{upcoming.min_xp}" if upcoming else "") + " XP"

    def _draw_chevrons(self, canvas: UiCanvas, plate: pygame.Rect) -> None:
        for row in range(min(self.CHEVRONS_PER_ROW, self._profile.rank_index % self.CHEVRONS_PER_ROW + 1)):
            y = plate.y + self.CHEVRON_Y + row * self.CHEVRON_STEP
            x = plate.x + self.CHEVRON_X
            canvas.shapes.lines(
                UiPalette.YELLOW,
                [
                    (x, y + self.CHEVRON_HEIGHT),
                    (x + self.CHEVRON_WIDTH, y),
                    (x + 2 * self.CHEVRON_WIDTH, y + self.CHEVRON_HEIGHT),
                ],
                width=2,
            )

    def _draw_name(self, canvas: UiCanvas, plate: pygame.Rect, xp_text: str) -> None:
        fonts = canvas.fonts
        name = t(self._profile.rank.name_key)
        room = plate.w - self.TEXT_X - fonts.small.size(xp_text)[0] - self.NAME_GAP
        font = fonts.body if fonts.body.size(name)[0] <= room else fonts.small
        lift = 2 + (font is fonts.small)
        canvas.write(
            Lettering(font).fitted(name, room),
            Point(plate.x + self.TEXT_X, plate.y + lift),
            TextStyle(font, UiPalette.PLATE_TEXT),
        )
