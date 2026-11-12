from __future__ import annotations

import pygame

from tenhut.controllers.page_id import PageId
from tenhut.game.animations import Lettering
from tenhut.game.geometry import Point
from tenhut.i18n import t
from tenhut.services.judge import RequestKind
from tenhut.ui.painting import TextAlign, TextStyle, TextWrapper, UiCanvas, UiPalette
from tenhut.ui.widgets import TextInput

from .heading import Heading
from .request_form_page import RequestFormPage


class RequestPage(RequestFormPage):
    """Asks the general for temporary access to a blocked site."""

    TARGET_FIELD_Y = 47
    TARGET_FIELD_HEIGHT = 20
    MAX_TARGET = 60
    JUSTIFICATION_Y = 95
    JUSTIFICATION_RESERVE = 52
    MAX_JUSTIFICATION_HEIGHT = 120
    SUBTITLE_Y = 26
    TARGET_LABEL_Y = 32
    REASON_LABEL_Y = 80
    SIDE_MARGIN = 6
    GROUPS_GAP = 6
    GROUPS_LINE = 12
    DEFAULT_GROUPS_Y = 220

    @property
    def page_id(self) -> PageId:
        return PageId.REQUEST

    @property
    def kind(self) -> RequestKind:
        return RequestKind.ACCESS

    def _target(self) -> str:
        return self._inputs[0].text.strip()

    def _field_top(self) -> int:
        return self.JUSTIFICATION_Y

    def _field_height(self, area: pygame.Rect) -> int:
        return max(
            self.MIN_FIELD_HEIGHT,
            min(self.MAX_JUSTIFICATION_HEIGHT, area.h - self.JUSTIFICATION_Y - self.JUSTIFICATION_RESERVE),
        )

    def _focus_justification(self) -> bool:
        return False

    def _add_leading_fields(self, area: pygame.Rect) -> None:
        field = TextInput(
            (area.x + self.FIELD_X, area.y + self.TARGET_FIELD_Y, area.w - self.FIELD_MARGIN, self.TARGET_FIELD_HEIGHT),
            t("field.access_target.placeholder"),
            self.MAX_TARGET,
        )
        field.focused = True
        self._inputs.append(field)

    def _draw_content(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        fonts = canvas.fonts
        self._draw_heading(canvas, area, Heading(t("board.request.title"), UiPalette.YELLOW))
        backend = self._judge.backend
        judge_name = t(backend.name_key)
        subtitle = t("board.request.judged_by", judge=judge_name) if backend.uses_ai else t("board.request.no_ai")
        canvas.write(
            Lettering(fonts.small).fitted(subtitle, area.w - self.HEADING_MARGIN),
            Point(area.centerx, area.y + self.SUBTITLE_Y),
            TextStyle(fonts.small, UiPalette.CHALK_DIM, TextAlign.CENTER),
        )
        for label, offset in (
            (t("board.request.target_label"), self.TARGET_LABEL_Y),
            (t("board.request.reason_label"), self.REASON_LABEL_Y),
        ):
            canvas.write(
                Lettering(fonts.body).fitted(label, area.w - 2 * self.SIDE_MARGIN),
                Point(area.x + self.SIDE_MARGIN, area.y + offset),
                TextStyle(fonts.body, UiPalette.CHALK),
            )
        self._draw_blocked_groups(canvas, area)

    def _draw_blocked_groups(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        font = canvas.fonts.small
        groups = ", ".join(self._context.settings.current.block_list.names)
        top = self._inputs[-1].rect.bottom + self.GROUPS_GAP if self._inputs else area.y + self.DEFAULT_GROUPS_Y
        room = max(0, (area.bottom - top) // self.GROUPS_LINE)
        lines = TextWrapper(font).lines(t("board.request.blocked_groups", groups=groups), area.w - 2 * self.SIDE_MARGIN)
        for index, line in enumerate(lines[:room]):
            canvas.write(
                line,
                Point(area.x + self.SIDE_MARGIN, top + index * self.GROUPS_LINE),
                TextStyle(font, UiPalette.CHALK_DIM),
            )
