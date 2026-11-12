from __future__ import annotations

import pygame

from tenhut.controllers.mission_controller import MissionController
from tenhut.controllers.page_id import PageId
from tenhut.game.animations import Lettering
from tenhut.game.geometry import Point
from tenhut.i18n import t
from tenhut.ui.layout import Layout
from tenhut.ui.painting import TextStyle, UiCanvas, UiPalette
from tenhut.ui.widgets import (
    Button,
    ButtonSpec,
    ButtonStyle,
    Chalkboard,
    RemoveMarker,
    TaskArea,
    TaskList,
    TaskScroll,
    TextInput,
)

from .heading import Heading
from .page import Page
from .page_context import PageContext
from .page_links import PageLinks


class MissionPage(Page):
    """Where the soldier writes the mission's tasks."""

    FIELD_OFFSET = (5, 35)
    FIELD_HEIGHT = 20
    FIELD_RIGHT_RESERVE = 36
    MAX_TASK_LENGTH = 90
    ADD_BUTTON_OFFSET = (27, 33)
    ADD_BUTTON_SIZE = 22
    HINT_Y = 58
    LIST_Y = 74
    LIST_MARGIN = 6
    LIST_RESERVE = 80
    ROW_HEIGHT = 15

    def __init__(
        self, context: PageContext, mission: MissionController, scroll: TaskScroll, *, links: PageLinks
    ) -> None:
        super().__init__(context)
        self._mission = mission
        self._scroll = scroll
        self._links = links
        self._tasks = TaskList(context.session, RemoveMarker(), scroll, on_press=self._remove_task)
        self._start_button: Button | None = None

    @property
    def page_id(self) -> PageId:
        return PageId.MISSION

    def add_task(self) -> None:
        field = self._inputs[0]
        field.focused = True
        if self._mission.add_task(field.text.strip()):
            field.clear()
            if self._start_button:
                self._start_button.enabled = True

    def click_board(self, position: tuple[int, int]) -> None:
        self._tasks.click(position)

    def scroll(self, rows: int) -> None:
        self._scroll.by(rows)

    def _populate(self, layout: Layout) -> None:
        area = Chalkboard.writing_area(layout.board)
        self._inputs = [self._task_field(area)]
        self._buttons.append(self._add_button(area))
        self._start_button = None
        if self._context.session.in_mission:
            done = ButtonSpec(t("button.done"), self._links.to(PageId.MAIN), ButtonStyle.GREEN)
            self._place_buttons(layout, [done])
            return
        enabled = bool(self._context.session.tasks)
        start = ButtonSpec(t("button.start_mission"), self._mission.start_mission, ButtonStyle.GREEN, enabled)
        back = ButtonSpec(t("button.back"), self._links.to(PageId.MAIN), ButtonStyle.TAN)
        self._start_button = self._place_buttons(layout, [start, back])[0]

    def _task_field(self, area: pygame.Rect) -> TextInput:
        field_x, field_y = self.FIELD_OFFSET
        field = TextInput(
            (area.x + field_x, area.y + field_y, area.w - self.FIELD_RIGHT_RESERVE, self.FIELD_HEIGHT),
            t("field.task.placeholder"),
            self.MAX_TASK_LENGTH,
        )
        field.focused = True
        field.on_submit(self.add_task)
        return field

    def _add_button(self, area: pygame.Rect) -> Button:
        add_x, add_y = self.ADD_BUTTON_OFFSET
        rect = (area.right - add_x, area.y + add_y, self.ADD_BUTTON_SIZE, self.ADD_BUTTON_SIZE)
        return Button(rect, ButtonSpec("+", self.add_task, ButtonStyle.GREEN))

    def _remove_task(self, index: int) -> None:
        self._mission.remove_task(index)
        if self._start_button:
            self._start_button.enabled = bool(self._context.session.tasks)

    def _draw_content(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        fonts, session = canvas.fonts, self._context.session
        title = t("board.mission.reinforce_title") if session.in_mission else t("board.mission.define_title")
        self._draw_heading(canvas, area, Heading(title, UiPalette.YELLOW))
        hint = t("hint.mission.add") + ("" if session.in_mission else t("hint.mission.remove"))
        hint = Lettering(fonts.small).fitted(hint, area.w - 2 * self.LIST_MARGIN)
        canvas.write(
            hint, Point(area.x + self.LIST_MARGIN, area.y + self.HINT_Y), TextStyle(fonts.small, UiPalette.YELLOW)
        )
        rows = (area.h - self.LIST_RESERVE) // self.ROW_HEIGHT
        origin = Point(area.x + self.LIST_MARGIN, area.y + self.LIST_Y)
        self._tasks.draw(canvas, TaskArea(origin, area.w - 2 * self.LIST_MARGIN, rows))
