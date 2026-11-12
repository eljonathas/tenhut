from __future__ import annotations

import pygame

from tenhut.controllers.calibration import CalibrationController
from tenhut.controllers.page_id import PageId
from tenhut.game.animations import Lettering
from tenhut.game.geometry import Point
from tenhut.i18n import t
from tenhut.ui.layout import Layout
from tenhut.ui.painting import TextAlign, TextStyle, TextWrapper, UiCanvas, UiPalette
from tenhut.ui.widgets import ButtonSpec, ButtonStyle

from .page import Page
from .page_context import PageContext
from .step_state import StepState


class CalibrationPage(Page):
    """Camera calibration: the poses to hold, a countdown, and what the camera sees."""

    SIDE_MARGIN = 6
    FIRST_STEP_Y = 30
    LINE_HEIGHT = 12
    STEP_GAP = 4
    STATUS_GAP = 6
    STATUS_MAX_TOP = 170
    STATUS_BOTTOM_RESERVE = 76
    COUNT_Y = 44
    CAPTURING_Y = 24
    PROGRESS_BAR = (20, 36, 40, 8)
    PROGRESS_FILL = (21, 37, 42, 6)
    SUMMARY_LIFT = 12

    def __init__(self, context: PageContext, calibration: CalibrationController) -> None:
        super().__init__(context)
        self._calibration = calibration

    @property
    def page_id(self) -> PageId:
        return PageId.CALIBRATION

    def escape(self) -> None:
        self._calibration.cancel()

    def press_space(self) -> bool:
        self._calibration.capture()
        return True

    def _populate(self, layout: Layout) -> None:
        self._place_buttons(
            layout,
            [
                ButtonSpec(t("button.capture"), self._calibration.capture, ButtonStyle.YELLOW),
                ButtonSpec(t("button.cancel"), self._calibration.cancel, ButtonStyle.TAN),
            ],
        )

    def _draw_content(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        title = canvas.fonts.title
        canvas.write(
            t("calibration.calibrate_camera"),
            Point(area.centerx, area.y + self.HEADING_Y),
            TextStyle(title, UiPalette.YELLOW, TextAlign.CENTER),
        )
        bottom = self._draw_steps(canvas, area)
        top = max(bottom + self.STATUS_GAP, min(area.y + self.STATUS_MAX_TOP, area.bottom - self.STATUS_BOTTOM_RESERVE))
        self._draw_camera_status(canvas, area, top)
        self._draw_sides(canvas, area)

    def _draw_steps(self, canvas: UiCanvas, area: pygame.Rect) -> int:
        font = canvas.fonts.small
        plan = self._calibration.plan
        y = area.y + self.FIRST_STEP_Y
        for index, step in enumerate(plan.steps):
            state = StepState.of(index, plan.index)
            for line in TextWrapper(font).lines(state.mark + step.prompt, area.w - 2 * self.SIDE_MARGIN):
                canvas.write(line, Point(area.x + self.SIDE_MARGIN, y), TextStyle(font, state.color))
                y += self.LINE_HEIGHT
            y += self.STEP_GAP
        return y

    def _draw_camera_status(self, canvas: UiCanvas, area: pygame.Rect, top: int) -> None:
        fonts = canvas.fonts
        watcher = self._calibration.holder.watcher
        left = Point(area.x + self.SIDE_MARGIN, top)
        if watcher is None or (not watcher.ready and not watcher.error):
            canvas.write(t("calibration.status.starting_camera"), left, TextStyle(fonts.body, UiPalette.CHALK))
        elif watcher.error:
            for index, line in enumerate(TextWrapper(fonts.small).lines(watcher.error, area.w - 2 * self.SIDE_MARGIN)):
                canvas.write(line, left.moved(dy=index * self.LINE_HEIGHT), TextStyle(fonts.small, UiPalette.CORAL))
        else:
            pose = watcher.angles()
            message = (
                t("calibration.status.face_detected", yaw=pose.yaw, pitch=pose.pitch)
                if pose
                else t("calibration.status.searching_face")
            )
            canvas.write(message, left, TextStyle(fonts.small, UiPalette.CHALK if pose else UiPalette.CORAL))
            self._draw_capture(canvas, area, top)

    def _draw_capture(self, canvas: UiCanvas, area: pygame.Rect, top: int) -> None:
        capture = self._calibration.capture_window
        now = self._context.clock.now()
        fonts = canvas.fonts
        if capture.counting_down:
            canvas.write(
                str(capture.seconds_left(now)),
                Point(area.centerx, top + self.COUNT_Y),
                TextStyle(fonts.big, UiPalette.YELLOW, TextAlign.CENTER),
            )
        elif capture.sampling:
            canvas.write(
                t("calibration.status.capturing"),
                Point(area.centerx, top + self.CAPTURING_Y),
                TextStyle(fonts.body, UiPalette.YELLOW, TextAlign.CENTER),
            )
            self._draw_sampling_bar(canvas, area, top)

    def _draw_sampling_bar(self, canvas: UiCanvas, area: pygame.Rect, top: int) -> None:
        progress = self._calibration.capture_window.progress(self._context.clock.now())
        x, y, width, height = self.PROGRESS_BAR
        canvas.shapes.rect(UiPalette.BOARD_DARK, (area.x + x, top + y, area.w - width, height))
        fill_x, fill_y, fill_width, fill_height = self.PROGRESS_FILL
        filled = int((area.w - fill_width) * progress)
        canvas.shapes.rect(UiPalette.YELLOW, (area.x + fill_x, top + fill_y, filled, fill_height))

    def _draw_sides(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        font = canvas.fonts.small
        described = [
            f"{t(side.label_key)}: {', '.join(names)}" for side, names in self._calibration.sides.items() if names
        ]
        summary = t("calibration.sides.summary", names="; ".join(described or [t("calibration.sides.none")]))
        canvas.write(
            Lettering(font).fitted(summary, area.w - 2 * self.SIDE_MARGIN),
            Point(area.x + self.SIDE_MARGIN, area.bottom - self.SUMMARY_LIFT),
            TextStyle(font, UiPalette.CHALK_DIM),
        )
