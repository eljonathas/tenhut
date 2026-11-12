from __future__ import annotations

from abc import ABC, abstractmethod

import pygame

from tenhut.controllers.page_id import PageId
from tenhut.game.animations import Lettering
from tenhut.game.geometry import Point
from tenhut.ui.layout import Layout
from tenhut.ui.painting import TextAlign, TextStyle, UiCanvas
from tenhut.ui.widgets import Button, ButtonRow, ButtonSpec, TextInput

from .heading import Heading
from .page_context import PageContext


class Page(ABC):
    """One screen of the chalkboard: the buttons below it, the fields on it and what is written on it."""

    HEADING_Y = 10
    HEADING_MARGIN = 8

    def __init__(self, context: PageContext) -> None:
        self._context = context
        self._buttons: list[Button] = []
        self._inputs: list[TextInput] = []

    @property
    @abstractmethod
    def page_id(self) -> PageId: ...

    @property
    def buttons(self) -> list[Button]:
        return self._buttons

    @property
    def inputs(self) -> list[TextInput]:
        return self._inputs

    def enter(self) -> None:
        """Runs when the page is opened (not when it is rebuilt after a resize)."""
        return None

    def fits(self, layout: Layout) -> bool:
        """False when the page cannot be shown in ``layout``."""
        return True

    def build(self, layout: Layout) -> None:
        self._buttons = []
        self._inputs = []
        self._populate(layout)

    def relayout(self, layout: Layout) -> None:
        """Rebuilds for a new layout keeping what was typed and which buttons were disabled."""
        typed = [(field.text, field.focused) for field in self._inputs]
        enabled = [button.enabled for button in self._buttons]
        self.build(layout)
        for field, (text, focused) in zip(self._inputs, typed):
            field.text, field.focused = text, focused
        if self._context.judge_slot.active:
            self._disable_buttons()
        elif len(enabled) == len(self._buttons):
            for button, was_enabled in zip(self._buttons, enabled):
                button.enabled = was_enabled

    def update(self, dt: float) -> None:
        for field in self._inputs:
            field.update(dt)

    def draw(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        self._draw_content(canvas, area)
        for field in self._inputs:
            field.draw(canvas)

    def draw_buttons(self, canvas: UiCanvas) -> None:
        for button in self._buttons:
            button.draw(canvas)

    def handle_widget_event(self, event: pygame.event.Event) -> bool:
        if any(button.handle_event(event) for button in list(self._buttons)):
            return True
        for field in self._inputs:
            if field.handle_event(event):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for other in self._inputs:
                        other.focused = other is field
                return True
        return False

    def click_board(self, position: tuple[int, int]) -> None:
        """A click on the chalkboard that no widget used."""
        return None

    def scroll(self, rows: int) -> None:
        """The mouse wheel turned ``rows`` notches."""
        return None

    def escape(self) -> None:
        if not self._context.judge_slot.active:
            self._context.navigation.open(PageId.MAIN)

    def press_space(self) -> bool:
        return False

    def cycle_focus(self) -> None:
        if len(self._inputs) < 2:
            return
        current = next((index for index, field in enumerate(self._inputs) if field.focused), -1)
        for field in self._inputs:
            field.focused = False
        self._inputs[(current + 1) % len(self._inputs)].focused = True

    @abstractmethod
    def _populate(self, layout: Layout) -> None:
        """Creates the buttons and fields for ``layout``."""

    @abstractmethod
    def _draw_content(self, canvas: UiCanvas, area: pygame.Rect) -> None: ...

    def _place_buttons(self, layout: Layout, specs: list[ButtonSpec]) -> list[Button]:
        placed = ButtonRow(layout.buttons).build(specs)
        self._buttons.extend(placed)
        return placed

    def _disable_buttons(self) -> None:
        for button in self._buttons:
            button.enabled = False

    def _draw_heading(self, canvas: UiCanvas, area: pygame.Rect, heading: Heading) -> None:
        font = canvas.fonts.title
        text = Lettering(font).fitted(heading.message, area.w - self.HEADING_MARGIN)
        canvas.write(
            text, Point(area.centerx, area.y + self.HEADING_Y), TextStyle(font, heading.color, TextAlign.CENTER)
        )
