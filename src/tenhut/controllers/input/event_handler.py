from __future__ import annotations

from abc import ABC, abstractmethod

import pygame


class EventHandler(ABC):
    """Reacts to one or more kinds of input events."""

    @property
    @abstractmethod
    def event_types(self) -> tuple[int, ...]: ...

    @abstractmethod
    def handle(self, event: pygame.event.Event) -> None: ...
