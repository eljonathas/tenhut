from __future__ import annotations

from abc import ABC, abstractmethod


class ResizeListener(ABC):
    """Told after the layout changed, to rebuild whatever depends on it."""

    @abstractmethod
    def layout_changed(self) -> None: ...
