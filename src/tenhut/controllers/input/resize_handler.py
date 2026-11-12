from __future__ import annotations

import pygame

from tenhut.controllers.resize_controller import ResizeController

from .event_handler import EventHandler


class ResizeHandler(EventHandler):
    """The window changed size."""

    def __init__(self, resizing: ResizeController) -> None:
        self._resizing = resizing

    @property
    def event_types(self) -> tuple[int, ...]:
        return (pygame.VIDEORESIZE, pygame.WINDOWSIZECHANGED)

    def handle(self, event: pygame.event.Event) -> None:
        self._resizing.resize()
