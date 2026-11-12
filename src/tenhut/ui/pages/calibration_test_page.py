from __future__ import annotations

from typing import ClassVar

import pygame

from tenhut.controllers.calibration import CalibrationController
from tenhut.controllers.camera import GazeStatusKind
from tenhut.controllers.page_id import PageId
from tenhut.game.animations import Lettering
from tenhut.game.geometry import Point
from tenhut.i18n import t
from tenhut.ui.layout import Layout
from tenhut.ui.painting import TextAlign, TextStyle, TextWrapper, UiCanvas, UiPalette
from tenhut.ui.widgets import ButtonSpec, ButtonStyle

from .calibration_reading import CalibrationReading
from .heading import Heading
from .page import Page
from .page_context import PageContext


class CalibrationTestPage(Page):
    """Lets the soldier try the calibration before it goes live: look around and see the verdict."""

    ALLOWED = UiPalette.MINT
    INFRACTION = UiPalette.SCARLET
    READINGS: ClassVar[dict[GazeStatusKind, CalibrationReading]] = {
        GazeStatusKind.WATCHING: CalibrationReading(
            "calibration.test.on_screen", ALLOWED, "calibration.test.verdict.allowed"
        ),
        GazeStatusKind.OTHER_MONITOR: CalibrationReading(
            "calibration.test.other_monitor", ALLOWED, "calibration.test.verdict.allowed_monitor"
        ),
        GazeStatusKind.LOOKING_DOWN: CalibrationReading(
            "calibration.test.looking_down", INFRACTION, "calibration.test.verdict.infraction"
        ),
        GazeStatusKind.FACE_VANISHED: CalibrationReading(
            "calibration.test.looking_down", INFRACTION, "calibration.test.verdict.infraction_face_vanished"
        ),
        GazeStatusKind.LOOKING_AWAY: CalibrationReading(
            "calibration.test.looking_away", INFRACTION, "calibration.test.verdict.infraction_no_monitor"
        ),
        GazeStatusKind.NO_FACE: CalibrationReading(
            "calibration.test.no_face", UiPalette.CHALK_DIM, "calibration.test.verdict.absent"
        ),
    }
    UNKNOWN = CalibrationReading("calibration.test.no_face", UiPalette.CHALK_DIM, None)
    SIDE_MARGIN = 6
    INSTRUCTIONS_Y = 26
    LINE_HEIGHT = 12
    LABEL_ZOOM = 2
    LABEL_MIN_Y = 60
    LABEL_MAX_Y = 96
    LABEL_HALF_HEIGHT_LIFT = 30
    VERDICT_GAP = 28
    ANGLES_GAP = 52
    RULES_LIFT = 42

    def __init__(self, context: PageContext, calibration: CalibrationController) -> None:
        super().__init__(context)
        self._calibration = calibration

    @property
    def page_id(self) -> PageId:
        return PageId.CALIBRATION_TEST

    def escape(self) -> None:
        self._calibration.cancel()

    def _populate(self, layout: Layout) -> None:
        self._place_buttons(
            layout,
            [
                ButtonSpec(t("button.activate"), self._calibration.finish, ButtonStyle.GREEN),
                ButtonSpec(t("button.redo"), self._calibration.start, ButtonStyle.YELLOW),
                ButtonSpec(t("button.cancel"), self._calibration.cancel, ButtonStyle.TAN),
            ],
        )

    def _draw_content(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        fonts = canvas.fonts
        self._draw_heading(canvas, area, Heading(t("calibration.test.title"), UiPalette.YELLOW))
        self._draw_lines(
            canvas, t("calibration.test.instructions"), self._text_region(area, area.y + self.INSTRUCTIONS_Y)
        )
        self._draw_label(canvas, area, self.READINGS.get(self._calibration.holder.status.kind, self.UNKNOWN))
        self._draw_angles(canvas, area, fonts.small)
        self._draw_lines(canvas, self._combat_rules(), self._text_region(area, area.bottom - self.RULES_LIFT))

    def _text_region(self, area: pygame.Rect, top: int) -> pygame.Rect:
        return pygame.Rect(area.x + self.SIDE_MARGIN, top, area.w - 2 * self.SIDE_MARGIN, 0)

    def _draw_lines(self, canvas: UiCanvas, text: str, region: pygame.Rect) -> None:
        font = canvas.fonts.small
        for index, line in enumerate(TextWrapper(font).lines(text, region.w)):
            canvas.write(
                line,
                Point(region.x, region.y + index * self.LINE_HEIGHT),
                TextStyle(font, UiPalette.CHALK_DIM),
            )

    def _combat_rules(self) -> str:
        return t("calibration.test.combat_rules", tol=self._context.settings.current.camera.tolerance_seconds)

    def _label_center_y(self, area: pygame.Rect) -> int:
        return area.y + min(self.LABEL_MAX_Y, max(self.LABEL_MIN_Y, area.h // 2 - self.LABEL_HALF_HEIGHT_LIFT))

    def _draw_label(self, canvas: UiCanvas, area: pygame.Rect, reading: CalibrationReading) -> None:
        fonts, center_y = canvas.fonts, self._label_center_y(area)
        image = fonts.title.render(t(reading.label_key), False, reading.color)
        image = pygame.transform.scale_by(image, self.LABEL_ZOOM)
        canvas.surface.blit(image, image.get_rect(center=(area.centerx, center_y)))
        verdict = t(reading.verdict_key) if reading.verdict_key else ""
        canvas.write(
            Lettering(fonts.body).fitted(verdict, area.w - self.HEADING_MARGIN),
            Point(area.centerx, center_y + self.VERDICT_GAP),
            TextStyle(fonts.body, reading.color, TextAlign.CENTER),
        )

    def _draw_angles(self, canvas: UiCanvas, area: pygame.Rect, font: pygame.font.Font) -> None:
        watcher = self._calibration.holder.watcher
        pose = watcher.angles() if watcher else None
        if not pose:
            return
        base = self._calibration.base_pose
        message = t("calibration.test.angles", yaw=pose.yaw - base.yaw, pitch=pose.pitch - base.pitch)
        canvas.write(
            Lettering(font).fitted(message, area.w - self.HEADING_MARGIN),
            Point(area.centerx, self._label_center_y(area) + self.ANGLES_GAP),
            TextStyle(font, UiPalette.CHALK_DIM, TextAlign.CENTER),
        )
