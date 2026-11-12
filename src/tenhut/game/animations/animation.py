from __future__ import annotations

from abc import ABC, abstractmethod

import pygame


class Animation(ABC):
    """A timed visual effect: advanced every tick, drawn on a surface, discarded once finished."""

    @property
    @abstractmethod
    def finished(self) -> bool: ...

    @abstractmethod
    def update(self, dt: float) -> None: ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None: ...
