from __future__ import annotations

from abc import ABC, abstractmethod

from ...i18n import t
from .command_spec import CommandSpec


class Elevator(ABC):
    """How to run a shell script as root with one elevation request."""

    TIMEOUT_SECONDS = 300  # the user may take a while to type the password

    @abstractmethod
    def command(self, script: str) -> CommandSpec | None:
        """The command that runs `script` as root, or None when there is no way to elevate."""

    def cancelled(self, returncode: int, output_lower: str) -> bool:
        return False

    def unavailable_message(self) -> str:
        return t("error.helper.pkexec_missing")

    def explain_failure(self, returncode: int, output: str) -> str:
        low = output.lower()
        if self.cancelled(returncode, low):
            return t("error.helper.install_cancelled")
        if "xcode-select" in low or "developer tools" in low:
            return t("error.helper.python_missing")
        return (output.strip().splitlines() or [t("error.helper.failed_with_code", n=returncode)])[-1][:160]
