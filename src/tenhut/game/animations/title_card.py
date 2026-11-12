from __future__ import annotations

import pygame

from tenhut.core import Clock
from tenhut.game.painting import Canvas, Palette

from .animation_palette import AnimationPalette
from .clocked_animation import ClockedAnimation
from .easing import Easing
from .lettering import Lettering
from .title_card_content import TitleCardContent
from .title_card_fonts import TitleCardFonts
from .title_card_placement import TitleCardPlacement


class TitleCard(ClockedAnimation):
    """The wooden sign that drops from the top of the scene to announce a new stage, holds, then rises."""

    DURATION = 4.0
    DROP_SECONDS = 0.35
    HOLD_UNTIL = 3.5
    RISE_SECONDS = 0.5
    HEIGHT = 34
    SIDE_MARGIN = 8
    TEXT_PADDING = 30
    HIDDEN_Y = -40
    TRAVEL = 48
    LEFT_ROPE_INSET = 10
    RIGHT_ROPE_INSET = 12

    def __init__(
        self, content: TitleCardContent, fonts: TitleCardFonts, clock: Clock, *, placement: TitleCardPlacement
    ) -> None:
        super().__init__(clock, self.DURATION)
        self._title = content.title
        self._subtitle = content.subtitle
        self._title_lettering = Lettering(fonts.title)
        self._subtitle_lettering = Lettering(fonts.subtitle)
        self._placement = placement

    def place(self, placement: TitleCardPlacement) -> None:
        self._placement = placement

    def draw(self, surface: pygame.Surface) -> None:
        sign = self._sign_rect()
        canvas = Canvas(surface)
        for rope_x in (sign.x + self.LEFT_ROPE_INSET, sign.right - self.RIGHT_ROPE_INSET):
            canvas.line(Palette.OUTLINE, (rope_x, self._placement.scene.y), (rope_x, sign.y), width=2)
        self._draw_board(canvas, sign)
        text_width = sign.w - 12
        self._title_lettering.draw_centered(
            surface,
            self._title_lettering.fitted(self._title, text_width),
            (sign.centerx, sign.y + 11),
            AnimationPalette.YELLOW,
        )
        self._subtitle_lettering.draw_centered(
            surface,
            self._subtitle_lettering.fitted(self._subtitle, text_width),
            (sign.centerx, sign.y + 24),
            AnimationPalette.CREAM,
        )

    def _sign_rect(self) -> pygame.Rect:
        scene, region = self._placement.scene, self._placement.region
        content = max(self._title_lettering.width(self._title), self._subtitle_lettering.width(self._subtitle))
        width = min(scene.w - 2 * self.SIDE_MARGIN, content + self.TEXT_PADDING)
        left = max(self.SIDE_MARGIN, region.x + (region.w - width) // 2)
        return pygame.Rect(left, scene.y + self.vertical_offset(), width, self.HEIGHT)

    def vertical_offset(self) -> int:
        age = self.age
        if age < self.HOLD_UNTIL:
            drop = min(1.0, age / self.DROP_SECONDS)
        else:
            drop = max(0.0, 1 - (age - self.HOLD_UNTIL) / self.RISE_SECONDS)
        return int(self.HIDDEN_Y + self.TRAVEL * Easing.out_cubic(drop))

    def _draw_board(self, canvas: Canvas, sign: pygame.Rect) -> None:
        canvas.rect(Palette.OUTLINE, sign.move(0, 2))
        canvas.rect(Palette.OUTLINE, sign)
        canvas.rect(AnimationPalette.WOOD, sign.inflate(-2, -2))
        canvas.line(AnimationPalette.WOOD_LIGHT, (sign.x + 2, sign.y + 2), (sign.right - 3, sign.y + 2))
        canvas.rect(AnimationPalette.WOOD_DARK, (sign.x + 1, sign.bottom - 4, sign.w - 2, 3))
