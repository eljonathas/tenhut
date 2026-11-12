from __future__ import annotations

import pygame

from .event_handler import EventHandler


class InputRouter:
    """Hands every input event to the handler registered for its type."""

    def __init__(self, handlers: list[EventHandler]) -> None:
        self._by_type = {event_type: handler for handler in handlers for event_type in handler.event_types}

    def dispatch(self, event: pygame.event.Event) -> None:
        handler = self._by_type.get(event.type)
        if handler is not None:
            handler.handle(event)
