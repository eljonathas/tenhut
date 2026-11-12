from __future__ import annotations

import pygame

from tenhut.controllers.settings import SettingsController
from tenhut.game.geometry import Point
from tenhut.i18n import t
from tenhut.ui.painting import TextAlign, TextStyle, UiCanvas, UiPalette

from .click_target import ClickTarget
from .row_adjustment import RowAdjustment
from .row_entry import RowEntry
from .row_frame import RowFrame
from .setting_control import SettingControl


class ToggleControl(SettingControl):
    """A yes/no switch."""

    WIDTH = 48
    RESERVED_WIDTH = 66
    RIGHT_OFFSET = 54

    def __init__(self, settings: SettingsController) -> None:
        self._settings = settings

    @property
    def reserved_width(self) -> int:
        return self.RESERVED_WIDTH

    def draw(self, canvas: UiCanvas, frame: RowFrame, entry: RowEntry) -> list[ClickTarget]:
        value = entry.value
        switch = pygame.Rect(frame.area.right - self.RIGHT_OFFSET, frame.top, self.WIDTH, frame.control_height)
        canvas.shapes.rect(UiPalette.INK, switch)
        canvas.shapes.rect(UiPalette.GREEN if value else UiPalette.GRAY, switch.inflate(-2, -2))
        caption = t("settings.toggle.yes") if value else t("settings.toggle.no")
        canvas.write(caption, Point(*switch.center), TextStyle(canvas.fonts.small, UiPalette.INK, TextAlign.CENTER))
        return [ClickTarget(switch, RowAdjustment(self._settings, entry.row, 1))]
