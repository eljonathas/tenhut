from __future__ import annotations

import pygame

from tenhut.controllers.active_page import ActivePage
from tenhut.controllers.navigation import Navigation
from tenhut.controllers.page_id import PageId
from tenhut.controllers.resize_listener import ResizeListener
from tenhut.controllers.tickable import Tickable
from tenhut.ui.layout import LayoutProvider

from .page import Page


class PageNavigator(Navigation, ActivePage, ResizeListener, Tickable):
    """Keeps the pages, knows which one is open and rebuilds it when the layout changes."""

    def __init__(self, layouts: LayoutProvider) -> None:
        self._layouts = layouts
        self._pages: dict[PageId, Page] = {}
        self._current_id = PageId.MAIN
        self._built = False

    @property
    def current(self) -> Page:
        return self._pages[self._current_id]

    @property
    def current_id(self) -> PageId:
        return self._current_id

    @property
    def board_shown(self) -> bool:
        return self._layouts.layout.board_visible or self._current_id is not PageId.MAIN

    def register(self, page: Page) -> None:
        self._pages[page.page_id] = page

    def open(self, page_id: PageId) -> None:
        self._current_id = page_id
        self._built = True
        self.current.enter()
        self.current.build(self._layouts.layout)

    def refresh(self, page_id: PageId) -> None:
        if self._current_id is page_id:
            self.open(page_id)

    def layout_changed(self) -> None:
        if not self._built:
            return
        layout = self._layouts.layout
        if not self.current.fits(layout):
            self._current_id = PageId.MAIN
        self.current.relayout(layout)

    def tick(self, dt: float) -> None:
        self.current.update(dt)

    def handle_widget_event(self, event: pygame.event.Event) -> bool:
        return self.current.handle_widget_event(event)

    def click_board(self, position: tuple[int, int]) -> None:
        self.current.click_board(position)

    def scroll(self, rows: int) -> None:
        self.current.scroll(rows)

    def escape(self) -> None:
        self.current.escape()

    def press_space(self) -> bool:
        return self.current.press_space()

    def cycle_focus(self) -> None:
        self.current.cycle_focus()
