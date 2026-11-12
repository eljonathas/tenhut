from __future__ import annotations

import pygame

from tenhut.controllers.run_state import RunState

from .event_handler import EventHandler


class VisibilityHandler(EventHandler):
    """The window was hidden or minimised (``hides``), or came back."""

    def __init__(self, state: RunState, types: tuple[int, ...], hides: bool) -> None:
        self._state = state
        self._types = types
        self._hides = hides

    @classmethod
    def hiding(cls, state: RunState) -> VisibilityHandler:
        return cls(state, (pygame.WINDOWMINIMIZED, pygame.WINDOWHIDDEN), True)

    @classmethod
    def showing(cls, state: RunState) -> VisibilityHandler:
        types = (pygame.WINDOWRESTORED, pygame.WINDOWSHOWN, pygame.WINDOWEXPOSED, pygame.WINDOWMAXIMIZED)
        return cls(state, types, False)

    @property
    def event_types(self) -> tuple[int, ...]:
        return self._types

    def handle(self, event: pygame.event.Event) -> None:
        self._state.hide(self._hides)
