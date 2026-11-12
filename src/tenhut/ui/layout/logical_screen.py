from __future__ import annotations

import pygame

from tenhut.game.geometry import Point
from tenhut.ui.fonts import FontSet
from tenhut.ui.painting import UiCanvas

from .layout import Layout
from .layout_factory import LayoutFactory
from .layout_provider import LayoutProvider
from .size import Size
from .window_scaler import WindowScaler


class LogicalScreen(LayoutProvider):
    """The small canvas everything is drawn on, scaled up to the window by whole pixels."""

    def __init__(
        self, fonts: FontSet, scaler: WindowScaler | None = None, factory: LayoutFactory | None = None
    ) -> None:
        self._fonts = fonts
        self._scaler = scaler or WindowScaler()
        self._factory = factory or LayoutFactory()
        self._surface: pygame.Surface | None = None
        self._layout: Layout | None = None
        self._canvas: UiCanvas | None = None

    @property
    def canvas(self) -> UiCanvas:
        assert self._canvas is not None, "resize() must run first"
        return self._canvas

    @property
    def layout(self) -> Layout:
        assert self._layout is not None, "resize() must run first"
        return self._layout

    @property
    def surface(self) -> pygame.Surface:
        assert self._surface is not None, "resize() must run first"
        return self._surface

    @property
    def scale(self) -> int:
        return self._scaler.scale

    @property
    def offset(self) -> Point:
        return self._scaler.offset

    def to_logical(self, position: tuple[int, int]) -> tuple[int, int]:
        return self._scaler.to_logical(position)

    def resize(self, window: Size, *, force: bool = False) -> bool:
        """Adapts to the window; False when nothing changed. A change makes a new surface and layout."""
        if not self._scaler.resize(window, force=force or self._surface is None):
            return False
        self._surface = pygame.Surface(self._scaler.logical_size)
        self._canvas = UiCanvas(self._surface, self._fonts)
        self._layout = self._factory.create(self._scaler.logical_size)
        return True
