from __future__ import annotations

import pygame

from tenhut.controllers.active_page import ActivePage
from tenhut.controllers.attention_controller import AttentionController

from .event_handler import EventHandler
from .pointer_translator import PointerTranslator


class MouseMotionHandler(EventHandler):
    """The pointer moved: the general notices, and buttons light up under it."""

    def __init__(self, page: ActivePage, attention: AttentionController, translator: PointerTranslator) -> None:
        self._page = page
        self._attention = attention
        self._translator = translator

    @property
    def event_types(self) -> tuple[int, ...]:
        return (pygame.MOUSEMOTION,)

    def handle(self, event: pygame.event.Event) -> None:
        self._attention.pointer_moved()
        self._page.handle_widget_event(self._translator.translate(event))
