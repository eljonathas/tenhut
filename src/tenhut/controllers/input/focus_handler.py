from __future__ import annotations

import pygame

from tenhut.controllers.run_state import RunState

from .event_handler import EventHandler


class FocusHandler(EventHandler):
    """The window gained or lost the keyboard focus."""

    def __init__(self, state: RunState) -> None:
        self._state = state

    @property
    def event_types(self) -> tuple[int, ...]:
        return (pygame.WINDOWFOCUSGAINED, pygame.WINDOWFOCUSLOST)

    def handle(self, event: pygame.event.Event) -> None:
        self._state.focus(event.type == pygame.WINDOWFOCUSGAINED)
