from __future__ import annotations

import getpass
import os

from ...i18n import t
from .command_error import CommandError
from .command_runner import CommandRunner
from .elevator import Elevator
from .helper_locator import HelperLocator
from .helper_scripts import HelperScripts
from .operating_system import OperatingSystem
from .operation_result import OperationResult
from .runtime_check import RuntimeCheck


class HelperInstaller:
    """Installs and removes the root helper and its sudo rule. Failures come back as messages, never raised."""

    def __init__(
        self,
        system: OperatingSystem,
        elevator: Elevator,
        runner: CommandRunner,
        *,
        runtime_check: RuntimeCheck,
        locator: HelperLocator,
    ) -> None:
        self._system = system
        self._elevator = elevator
        self._runner = runner
        self._runtime_check = runtime_check
        self._locator = locator

    @staticmethod
    def current_username() -> str:
        """The real user (SUDO_USER when the app was started through sudo)."""
        return os.environ.get("SUDO_USER") or getpass.getuser()

    def install(self, username: str | None = None) -> OperationResult:
        if self._system.is_windows:
            return OperationResult.failure(t("error.helper.windows_needs_admin"))
        user = username or self.current_username()
        if not HelperScripts.valid_username(user):
            return OperationResult.failure(t("error.helper.unsupported_user", u=user)[:160])
        source = self._locator.bundled()
        if source is None:
            return OperationResult.failure(t("error.helper.file_missing"))
        runtime = self._runtime_check.check()
        if not runtime.ok:
            return runtime
        outcome = self._elevate(HelperScripts.install(user, str(source), self._system))
        return OperationResult.success(t("status.helper.installed")) if outcome.ok else outcome

    def uninstall(self) -> OperationResult:
        if self._system.is_windows:
            return OperationResult.success()
        outcome = self._elevate(HelperScripts.uninstall())
        return OperationResult.success(t("status.helper.removed")) if outcome.ok else outcome

    def _elevate(self, script: str) -> OperationResult:
        command = self._elevator.command(script)
        if command is None:
            return OperationResult.failure(self._elevator.unavailable_message())
        try:
            result = self._runner.run(command)
        except CommandError as error:
            return OperationResult.failure(str(error)[:160])
        if not result.succeeded:
            return OperationResult.failure(
                self._elevator.explain_failure(result.returncode, result.stderr + result.stdout)
            )
        return OperationResult.success()
