from __future__ import annotations

from tenhut.controllers.settings import SettingRow, SettingsController


class RowAdjustment:
    """A click on one control of a settings row."""

    def __init__(self, settings: SettingsController, row: SettingRow, direction: int) -> None:
        self._settings = settings
        self._row = row
        self._direction = direction

    def __call__(self) -> None:
        self._settings.click(self._row, self._direction)
