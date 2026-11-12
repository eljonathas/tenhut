from __future__ import annotations

from abc import abstractmethod

import pygame

from tenhut.controllers.judge_controller import JudgeController
from tenhut.controllers.page_id import PageId
from tenhut.controllers.request_form import RequestForm
from tenhut.i18n import t
from tenhut.services.judge import RequestKind
from tenhut.ui.layout import Layout
from tenhut.ui.widgets import ButtonSpec, ButtonStyle, Chalkboard, MultilineTextInput

from .page import Page
from .page_context import PageContext
from .page_links import PageLinks


class RequestFormPage(Page):
    """A page where the soldier writes a justification for the judge; the buttons lock while the judge thinks."""

    FIELD_X = 5
    FIELD_MARGIN = 10
    MAX_JUSTIFICATION = 600
    MIN_FIELD_HEIGHT = 36

    def __init__(self, context: PageContext, judge: JudgeController, links: PageLinks) -> None:
        super().__init__(context)
        self._judge = judge
        self._links = links

    @property
    @abstractmethod
    def kind(self) -> RequestKind: ...

    @abstractmethod
    def _field_top(self) -> int: ...

    @abstractmethod
    def _field_height(self, area: pygame.Rect) -> int: ...

    @abstractmethod
    def _focus_justification(self) -> bool: ...

    def update(self, dt: float) -> None:
        super().update(dt)
        if self._context.judge_slot.active:
            self._disable_buttons()

    def submit(self) -> None:
        self._judge.submit(RequestForm(self.kind, self._target(), self._inputs[-1].text.strip()))

    def _target(self) -> str:
        return ""

    def _populate(self, layout: Layout) -> None:
        area = Chalkboard.writing_area(layout.board)
        self._add_leading_fields(area)
        field = MultilineTextInput(
            (area.x + self.FIELD_X, area.y + self._field_top(), area.w - self.FIELD_MARGIN, self._field_height(area)),
            t("field.justification.placeholder"),
            self.MAX_JUSTIFICATION,
        )
        field.focused = self._focus_justification()
        self._inputs.append(field)
        label = t("button.send_short") if layout.compact else t("button.send_to_general")
        self._place_buttons(
            layout,
            [
                ButtonSpec(label, self.submit, ButtonStyle.YELLOW),
                ButtonSpec(t("button.cancel"), self._links.to(PageId.MAIN), ButtonStyle.TAN),
            ],
        )

    def _add_leading_fields(self, area: pygame.Rect) -> None:
        """Fields above the justification."""
