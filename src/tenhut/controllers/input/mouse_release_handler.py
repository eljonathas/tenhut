from __future__ import annotations

import pygame

from tenhut.controllers.active_page import ActivePage

from .event_handler import EventHandler
from .pointer_translator import PointerTranslator


class MouseReleaseHandler(EventHandler):
    """A mouse button was released: buttons run their action."""

    def __init__(self, page: ActivePage, translator: PointerTranslator) -> None:
        self._page = page
        self._translator = translator

    @property
    def event_types(self) -> tuple[int, ...]:
        return (pygame.MOUSEBUTTONUP,)

    def handle(self, event: pygame.event.Event) -> None:
        self._page.handle_widget_event(self._translator.translate(event))
