from __future__ import annotations

from abc import ABC, abstractmethod

import pygame

from tenhut.ui.painting import UiCanvas


class TaskMarker(ABC):
    """The little box in front of a task."""

    @abstractmethod
    def draw(self, canvas: UiCanvas, box: pygame.Rect, done: bool) -> None: ...
