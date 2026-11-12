from __future__ import annotations

from abc import ABC, abstractmethod

from .page_id import PageId


class Navigation(ABC):
    """Which page is open, and how controllers change it."""

    @property
    @abstractmethod
    def current_id(self) -> PageId: ...

    @property
    @abstractmethod
    def board_shown(self) -> bool:
        """Whether the chalkboard is on screen (always on big layouts; only on request in the mini one)."""

    @abstractmethod
    def open(self, page_id: PageId) -> None: ...

    @abstractmethod
    def refresh(self, page_id: PageId) -> None:
        """Rebuilds the page if it is the one being shown."""
