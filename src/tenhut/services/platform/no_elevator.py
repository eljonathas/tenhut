from __future__ import annotations

from ...i18n import t
from .command_spec import CommandSpec
from .elevator import Elevator


class NoElevator(Elevator):
    """Windows: the app itself runs as administrator, there is nothing to elevate."""

    def command(self, script: str) -> CommandSpec | None:
        return None

    def unavailable_message(self) -> str:
        return t("error.helper.windows_needs_admin")
