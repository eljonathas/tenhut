from __future__ import annotations

import pygame

from tenhut.controllers.page_id import PageId
from tenhut.controllers.settings import EditorKind, SettingRow, SettingsController
from tenhut.game.animations import Lettering
from tenhut.game.geometry import Point
from tenhut.i18n import t
from tenhut.ui.layout import Layout
from tenhut.ui.painting import TextAlign, TextStyle, UiCanvas, UiPalette
from tenhut.ui.widgets import ButtonSpec, ButtonStyle

from .action_bar import ActionBar
from .click_target import ClickTarget
from .heading import Heading
from .page import Page
from .page_context import PageContext
from .row_entry import RowEntry
from .row_frame import RowFrame
from .setting_control import SettingControl


class SettingsPage(Page):
    """The settings list: rows with controls, then the camera calibration and the blocking installer."""

    FIRST_ROW_Y = 28
    MIN_ROW_HEIGHT = 12
    MAX_ROW_HEIGHT = 19
    MAX_CONTROL_HEIGHT = 15
    FOOTER_RESERVE = 52
    INSTALL_RESERVE = 20
    SIDE_MARGIN = 6
    BAR_HEIGHT = 16
    BAR_GAP = 4
    LOCKED_HINT_GAP = 12
    ACTION_FIT_MARGIN = 6

    def __init__(
        self, context: PageContext, settings: SettingsController, controls: dict[EditorKind, SettingControl]
    ) -> None:
        super().__init__(context)
        self._settings = settings
        self._controls = controls
        self._targets: list[ClickTarget] = []

    @property
    def page_id(self) -> PageId:
        return PageId.SETTINGS

    def enter(self) -> None:
        self._settings.begin_draft()

    def click_board(self, position: tuple[int, int]) -> None:
        for target in self._targets:
            if target.rect.collidepoint(position):
                target.action()
                return

    def _populate(self, layout: Layout) -> None:
        json_label = "JSON" if layout.compact else t("button.open_json")
        self._place_buttons(
            layout,
            [
                ButtonSpec(t("button.save"), self._settings.save, ButtonStyle.GREEN),
                ButtonSpec(json_label, self._settings.open_config_file, ButtonStyle.TAN),
                ButtonSpec(t("button.back"), self._settings.cancel, ButtonStyle.TAN),
            ],
        )

    def _draw_content(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        self._draw_heading(canvas, area, Heading(t("settings.title"), UiPalette.YELLOW))
        self._targets = []
        offered = self._settings.installer.offered
        rows = self._settings.rows()
        reserve = self.FOOTER_RESERVE + (self.INSTALL_RESERVE if offered else 0)
        height = max(self.MIN_ROW_HEIGHT, min(self.MAX_ROW_HEIGHT, (area.h - reserve) // len(rows)))
        y = area.y + self.FIRST_ROW_Y
        for row in rows:
            self._draw_row(canvas, RowFrame(area, y, min(self.MAX_CONTROL_HEIGHT, height - 1)), row)
            y += height
        self._draw_footer(canvas, area, y)

    def _draw_row(self, canvas: UiCanvas, frame: RowFrame, row: SettingRow) -> None:
        control = self._controls[row.editor.kind]
        locked = self._settings.locked and not row.key.always_unlocked
        font = canvas.fonts.body
        lift = (self.MAX_CONTROL_HEIGHT - frame.control_height) // 2
        label = Lettering(font).fitted(row.label, frame.area.w - control.reserved_width)
        canvas.write(
            label,
            Point(frame.area.x + self.SIDE_MARGIN, frame.top + 2 - lift),
            TextStyle(font, UiPalette.CHALK_DIM if locked else UiPalette.CHALK),
        )
        entry = RowEntry(row, self._settings.value(row.key))
        self._targets.extend(control.draw(canvas, frame, entry))

    def _draw_footer(self, canvas: UiCanvas, area: pygame.Rect, top: int) -> None:
        if self._settings.locked:
            canvas.write(
                t("settings.locked_hint"),
                Point(area.centerx, top + self.LOCKED_HINT_GAP),
                TextStyle(canvas.fonts.small, UiPalette.CORAL, TextAlign.CENTER),
            )
            return
        calibrate = self._draw_calibration_bar(canvas, area, top)
        if self._settings.installer.offered:
            self._draw_install_bar(canvas, calibrate)

    def _draw_calibration_bar(self, canvas: UiCanvas, area: pygame.Rect, top: int) -> pygame.Rect:
        rect = pygame.Rect(
            area.x + self.SIDE_MARGIN, top + self.BAR_GAP, area.w - 2 * self.SIDE_MARGIN, self.BAR_HEIGHT
        )
        if self._settings.has_camera_calibration:
            label = t("calibration.recalibrate_camera")
        else:
            label = t("calibration.calibrate_camera")
        self._draw_action(canvas, ActionBar(rect, label, UiPalette.CALIBRATE, fitted=False))
        self._targets.append(ClickTarget(rect, self._settings.request_calibration))
        return rect

    def _draw_install_bar(self, canvas: UiCanvas, above: pygame.Rect) -> None:
        rect = pygame.Rect(above.x, above.bottom + self.BAR_GAP, above.w, self.BAR_HEIGHT)
        installing = self._settings.installer.installing
        face = UiPalette.STEPPER if installing else UiPalette.INSTALL
        label = t("button.installing") if installing else t("button.install_blocker")
        self._draw_action(canvas, ActionBar(rect, label, face, fitted=True))
        self._targets.append(ClickTarget(rect, self._settings.install_blocker))

    def _draw_action(self, canvas: UiCanvas, bar: ActionBar) -> None:
        canvas.shapes.rect(UiPalette.INK, bar.rect)
        canvas.shapes.rect(bar.face, bar.rect.inflate(-2, -2))
        font = canvas.fonts.body
        text = Lettering(font).fitted(bar.label, bar.rect.w - self.ACTION_FIT_MARGIN) if bar.fitted else bar.label
        canvas.write(text, Point(*bar.rect.center), TextStyle(font, UiPalette.INK, TextAlign.CENTER))
