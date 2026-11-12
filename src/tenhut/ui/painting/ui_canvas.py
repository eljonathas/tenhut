from __future__ import annotations

import pygame

from tenhut.game.geometry import Point
from tenhut.game.painting import Canvas
from tenhut.ui.fonts import FontSet

from .text_painter import TextPainter
from .text_style import TextStyle


class UiCanvas:
    """A surface with the shape painter, the text painter and the fonts every widget draws with."""

    def __init__(self, surface: pygame.Surface, fonts: FontSet) -> None:
        self._surface = surface
        self._shapes = Canvas(surface)
        self._text = TextPainter(surface)
        self._fonts = fonts

    @property
    def surface(self) -> pygame.Surface:
        return self._surface

    @property
    def shapes(self) -> Canvas:
        return self._shapes

    @property
    def fonts(self) -> FontSet:
        return self._fonts

    def write(self, text: str, position: Point, style: TextStyle) -> pygame.Rect:
        return self._text.draw(text, position, style)
