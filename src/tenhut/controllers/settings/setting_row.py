from __future__ import annotations

from dataclasses import dataclass

from .row_editor import RowEditor
from .setting_key import SettingKey


@dataclass(frozen=True, slots=True)
class SettingRow:
    """One line of the settings page."""

    label: str
    key: SettingKey
    editor: RowEditor
