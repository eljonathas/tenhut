from __future__ import annotations

import pygame

from tenhut.controllers.active_page import ActivePage

from .event_handler import EventHandler


class WheelHandler(EventHandler):
    """The mouse wheel scrolls the task list."""

    def __init__(self, page: ActivePage) -> None:
        self._page = page

    @property
    def event_types(self) -> tuple[int, ...]:
        return (pygame.MOUSEWHEEL,)

    def handle(self, event: pygame.event.Event) -> None:
        self._page.scroll(event.y)
