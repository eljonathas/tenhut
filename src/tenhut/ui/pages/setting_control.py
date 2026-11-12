from __future__ import annotations

from abc import ABC, abstractmethod

from tenhut.ui.painting import UiCanvas

from .click_target import ClickTarget
from .row_entry import RowEntry
from .row_frame import RowFrame


class SettingControl(ABC):
    """The controls at the right end of a settings row."""

    @property
    @abstractmethod
    def reserved_width(self) -> int:
        """Width the controls take, which the label must leave free."""

    @abstractmethod
    def draw(self, canvas: UiCanvas, frame: RowFrame, entry: RowEntry) -> list[ClickTarget]: ...
