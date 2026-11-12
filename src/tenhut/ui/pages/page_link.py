from __future__ import annotations

from tenhut.controllers.navigation import Navigation
from tenhut.controllers.page_id import PageId


class PageLink:
    """A button action that opens a page."""

    def __init__(self, navigation: Navigation, target: PageId) -> None:
        self._navigation = navigation
        self._target = target

    def __call__(self) -> None:
        self._navigation.open(self._target)
