from __future__ import annotations

from abc import ABC, abstractmethod

from .settings_draft import SettingsDraft


class ChangeGuard(ABC):
    """Can veto a change of one option (and do something else instead)."""

    @abstractmethod
    def allows(self, new_value: object, draft: SettingsDraft) -> bool: ...
