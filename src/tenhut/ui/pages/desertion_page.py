from __future__ import annotations

import pygame

from tenhut.controllers.page_id import PageId
from tenhut.game.geometry import Point
from tenhut.i18n import t
from tenhut.services.judge import RequestKind
from tenhut.ui.painting import TextStyle, TextWrapper, UiCanvas, UiPalette

from .heading import Heading
from .request_form_page import RequestFormPage


class DesertionPage(RequestFormPage):
    """Asks the general for permission to abandon the mission."""

    JUSTIFICATION_Y = 59
    JUSTIFICATION_RESERVE = 8
    MAX_JUSTIFICATION_HEIGHT = 140
    SIDE_MARGIN = 6
    WARNING_Y = 26
    LINE_HEIGHT = 12
    LABEL_Y = 46

    @property
    def page_id(self) -> PageId:
        return PageId.DESERTION

    @property
    def kind(self) -> RequestKind:
        return RequestKind.DESERTION

    def _field_top(self) -> int:
        return self.JUSTIFICATION_Y

    def _field_height(self, area: pygame.Rect) -> int:
        return max(
            self.MIN_FIELD_HEIGHT,
            min(self.MAX_JUSTIFICATION_HEIGHT, area.h - self.JUSTIFICATION_Y - self.JUSTIFICATION_RESERVE),
        )

    def _focus_justification(self) -> bool:
        return True

    def _draw_content(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        fonts = canvas.fonts
        self._draw_heading(canvas, area, Heading(t("board.desertion.title"), UiPalette.SALMON))
        lines = TextWrapper(fonts.small).lines(t("board.desertion.warning"), area.w - 2 * self.SIDE_MARGIN)
        for index, line in enumerate(lines):
            canvas.write(
                line,
                Point(area.x + self.SIDE_MARGIN, area.y + self.WARNING_Y + index * self.LINE_HEIGHT),
                TextStyle(fonts.small, UiPalette.CHALK_DIM),
            )
        canvas.write(
            t("board.desertion.justification_label"),
            Point(area.x + self.SIDE_MARGIN, area.y + self.LABEL_Y),
            TextStyle(fonts.body, UiPalette.CHALK),
        )
