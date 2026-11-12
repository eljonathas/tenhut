from __future__ import annotations

from abc import ABC, abstractmethod

from tenhut.ui.layout import Size


class WindowControl(ABC):
    """What the controllers may ask of the operating-system window."""

    @property
    @abstractmethod
    def size(self) -> Size: ...

    @abstractmethod
    def minimize(self) -> None: ...
