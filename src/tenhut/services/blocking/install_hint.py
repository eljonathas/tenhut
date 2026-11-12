from __future__ import annotations

from typing import ClassVar

from ...i18n import t
from ..platform import OperatingSystem


class InstallHint:
    """The short UI text that says how to turn blocking on."""

    KEYS: ClassVar[dict[bool, str]] = {
        True: "hint.install_blocker.open_as_admin",
        False: "hint.install_blocker.menu_path",
    }

    @staticmethod
    def for_system(system: OperatingSystem) -> str:
        return t(InstallHint.KEYS[system.is_windows])
