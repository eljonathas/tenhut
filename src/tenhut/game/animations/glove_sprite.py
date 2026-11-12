from __future__ import annotations

import math

import pygame

from tenhut.game.painting import Canvas, Palette


class GloveSprite:
    """The closed glove seen from the front, its index finger pointing at the viewer (foreshortened)."""

    SIZE = 32
    CUFF_CENTER = (16, 20)
    FIST = pygame.Rect(7, 9, 19, 18)
    THUMB = pygame.Rect(22, 14, 7, 7)
    FINGERTIP_CENTER = (15, 13)
    FINGERTIP_RADIUS = 6
    GLINT_CENTER = (13, 11)
    KNUCKLE_COLUMNS = (11, 16, 21)

    def build(self) -> pygame.Surface:
        sprite = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)
        canvas = Canvas(sprite)
        self._paint_cuff(canvas)
        self._paint_fist(canvas)
        self._paint_thumb(canvas)
        self._paint_fingertip(canvas)
        return sprite

    def _paint_cuff(self, canvas: Canvas) -> None:
        canvas.circle(Palette.OUTLINE, self.CUFF_CENTER, 14)
        canvas.circle(Palette.OLIVE, self.CUFF_CENTER, 13)
        canvas.circle(Palette.OLIVE_DARK, (16, 22), 13, border=3)
        canvas.circle(Palette.GOLD_DARK, self.CUFF_CENTER, 11)
        canvas.circle(Palette.GOLD, self.CUFF_CENTER, 10)

    def _paint_fist(self, canvas: Canvas) -> None:
        pygame.draw.rect(canvas.surface, Palette.OUTLINE, (6, 8, 21, 20), border_radius=5)
        pygame.draw.rect(canvas.surface, Palette.GLOVE, self.FIST, border_radius=4)
        for column in self.KNUCKLE_COLUMNS:
            canvas.line(Palette.GLOVE_SHADE, (column, 19), (column, 25))
        canvas.line(Palette.GLOVE_SHADE, (8, 25), (25, 25))

    def _paint_thumb(self, canvas: Canvas) -> None:
        canvas.ellipse(Palette.OUTLINE, (21, 13, 9, 9))
        canvas.ellipse(Palette.GLOVE, self.THUMB)

    def _paint_fingertip(self, canvas: Canvas) -> None:
        canvas.circle(Palette.OUTLINE, self.FINGERTIP_CENTER, self.FINGERTIP_RADIUS + 1)
        canvas.circle(Palette.GLOVE, self.FINGERTIP_CENTER, self.FINGERTIP_RADIUS)
        canvas.circle((255, 255, 255), self.GLINT_CENTER, 2)
        pygame.draw.arc(canvas.surface, Palette.GLOVE_SHADE, (10, 8, 11, 11), math.pi * 1.1, math.pi * 1.9)
