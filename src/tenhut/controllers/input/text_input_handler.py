from __future__ import annotations

import pygame

from tenhut.controllers.active_page import ActivePage

from .event_handler import EventHandler


class TextInputHandler(EventHandler):
    """Typed text goes to the focused field."""

    def __init__(self, page: ActivePage) -> None:
        self._page = page

    @property
    def event_types(self) -> tuple[int, ...]:
        return (pygame.TEXTINPUT,)

    def handle(self, event: pygame.event.Event) -> None:
        self._page.handle_widget_event(event)
