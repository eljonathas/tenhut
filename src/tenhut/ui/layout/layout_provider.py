from __future__ import annotations

from abc import ABC, abstractmethod

from .layout import Layout


class LayoutProvider(ABC):
    """Gives whoever draws or reacts to the screen the current layout, which changes when the window is resized."""

    @property
    @abstractmethod
    def layout(self) -> Layout: ...

    @abstractmethod
    def to_logical(self, position: tuple[int, int]) -> tuple[int, int]:
        """Window pixels to logical pixels."""
