from __future__ import annotations

import pygame

from tenhut.controllers.page_id import PageId
from tenhut.i18n import t
from tenhut.ui.layout import Layout
from tenhut.ui.painting import UiCanvas
from tenhut.ui.widgets import ButtonSpec, ButtonStyle, MissionBoard, TaskScroll

from .page import Page
from .page_context import PageContext
from .page_links import PageLinks


class BoardPage(Page):
    """The main board opened over the scene of the mini layout."""

    def __init__(self, context: PageContext, board: MissionBoard, scroll: TaskScroll, *, links: PageLinks) -> None:
        super().__init__(context)
        self._board = board
        self._scroll = scroll
        self._links = links

    @property
    def page_id(self) -> PageId:
        return PageId.BOARD

    def fits(self, layout: Layout) -> bool:
        return layout.compact

    def click_board(self, position: tuple[int, int]) -> None:
        self._board.click(position)

    def scroll(self, rows: int) -> None:
        self._scroll.by(rows)

    def _populate(self, layout: Layout) -> None:
        specs = [ButtonSpec(t("button.back"), self._links.to(PageId.MAIN), ButtonStyle.TAN)]
        if self._context.session.in_mission:
            specs.insert(0, ButtonSpec(t("button.add_task"), self._links.to(PageId.MISSION), ButtonStyle.TAN))
        self._place_buttons(layout, specs)

    def _draw_content(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        self._board.draw(canvas, area)
