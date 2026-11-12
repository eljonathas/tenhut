from __future__ import annotations

from abc import ABC, abstractmethod


class ActivePage(ABC):
    """What the input router asks of the page being shown."""

    @abstractmethod
    def handle_widget_event(self, event: object) -> bool:
        """Lets the page's buttons and fields react; True when one of them used the event."""

    @abstractmethod
    def click_board(self, position: tuple[int, int]) -> None: ...

    @abstractmethod
    def scroll(self, rows: int) -> None: ...

    @abstractmethod
    def escape(self) -> None: ...

    @abstractmethod
    def press_space(self) -> bool:
        """True when the page used the space bar."""

    @abstractmethod
    def cycle_focus(self) -> None: ...
