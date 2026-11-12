from __future__ import annotations

from abc import ABC, abstractmethod

import pygame

from tenhut.ui.painting import UiCanvas


class Widget(ABC):
    """Something on screen that reacts to events, advances with time and draws itself."""

    @property
    @abstractmethod
    def rect(self) -> pygame.Rect: ...

    def handle_event(self, event: pygame.event.Event) -> bool:
        """True when the widget used the event, so nobody else should."""
        return False

    def update(self, dt: float) -> None:
        return None

    @abstractmethod
    def draw(self, canvas: UiCanvas) -> None: ...
