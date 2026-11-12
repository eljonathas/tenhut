from __future__ import annotations

import pygame

from tenhut.controllers.page_id import PageId
from tenhut.ui.layout import Layout
from tenhut.ui.painting import UiCanvas
from tenhut.ui.widgets import MissionBoard, TaskScroll

from .main_button_plan import MainButtonPlan
from .page import Page
from .page_context import PageContext


class MainPage(Page):
    """The clock, the mission and the buttons that fit the current phase."""

    def __init__(
        self, context: PageContext, board: MissionBoard, plans: list[MainButtonPlan], *, scroll: TaskScroll
    ) -> None:
        super().__init__(context)
        self._board = board
        self._plans = plans
        self._scroll = scroll

    @property
    def page_id(self) -> PageId:
        return PageId.MAIN

    def click_board(self, position: tuple[int, int]) -> None:
        self._board.click(position)

    def scroll(self, rows: int) -> None:
        self._scroll.by(rows)

    def escape(self) -> None:
        """Already on the main page: nothing to close."""

    def _populate(self, layout: Layout) -> None:
        session = self._context.session
        plan = next(p for p in self._plans if p.applies(session.phase, session.pending_count()))
        self._place_buttons(layout, plan.specs(layout.compact))

    def _draw_content(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        self._board.draw(canvas, area)
