from __future__ import annotations

from tenhut.controllers.navigation import Navigation
from tenhut.controllers.page_id import PageId

from .page_link import PageLink


class PageLinks:
    """Makes the actions that open each page."""

    def __init__(self, navigation: Navigation) -> None:
        self._navigation = navigation

    def to(self, target: PageId) -> PageLink:
        return PageLink(self._navigation, target)
