from __future__ import annotations

import pygame

from tenhut.ui.layout import LayoutProvider


class PointerTranslator:
    """Rewrites mouse events from window pixels to logical pixels."""

    def __init__(self, layouts: LayoutProvider) -> None:
        self._layouts = layouts

    def translate(self, event: pygame.event.Event) -> pygame.event.Event:
        return pygame.event.Event(event.type, {**event.__dict__, "pos": self._layouts.to_logical(event.pos)})
