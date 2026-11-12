from __future__ import annotations

import contextlib

import pygame

from tenhut.controllers.window_control import WindowControl
from tenhut.ui.layout import Size


class DisplayWindow(WindowControl):
    """The operating-system window pygame draws into."""

    DEFAULT_SIZE = Size(1120, 720)
    MIN_SIZE = Size(320, 240)
    CAPTION = "Tenhut"

    def __init__(self, headless: bool = False) -> None:
        pygame.display.set_caption(self.CAPTION)
        pygame.display.set_mode(self.DEFAULT_SIZE, 0 if headless else pygame.RESIZABLE)
        with contextlib.suppress(AttributeError, pygame.error):
            pygame.Window.from_display_module().minimum_size = self.MIN_SIZE
        with contextlib.suppress(pygame.error, AttributeError):
            pygame.scrap.init()

    @property
    def surface(self) -> pygame.Surface:
        return pygame.display.get_surface()

    @property
    def size(self) -> Size:
        return Size(*self.surface.get_size())

    def minimize(self) -> None:
        with contextlib.suppress(pygame.error):
            pygame.display.iconify()
