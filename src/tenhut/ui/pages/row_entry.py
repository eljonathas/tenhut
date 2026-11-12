from __future__ import annotations

from dataclasses import dataclass

from tenhut.controllers import SettingRow


@dataclass(frozen=True, slots=True)
class RowEntry:
    """A settings row and the value it currently holds."""

    row: SettingRow
    value: object
