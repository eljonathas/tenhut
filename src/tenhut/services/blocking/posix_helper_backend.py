from __future__ import annotations

from pathlib import Path

from ...core import Clock
from ...i18n import t
from ..platform import (
    CommandError,
    CommandResult,
    CommandRunner,
    CommandSpec,
    HelperLocator,
    OperatingSystem,
    OperationResult,
    RuntimeCheck,
)
from .hosts_backend import HostsBackend
from .hosts_error import HostsError
from .install_hint import InstallHint


class PosixHelperBackend(HostsBackend):
    """Linux/macOS: runs the root helper through `sudo -n` (a NOPASSWD rule installed once)."""

    RUNTIME_CHECK_TTL = 30
    TIMEOUT_SECONDS = 15

    def __init__(
        self,
        system: OperatingSystem,
        runner: CommandRunner,
        *,
        locator: HelperLocator,
        runtime_check: RuntimeCheck,
        clock: Clock,
    ) -> None:
        self._system = system
        self._runner = runner
        self._locator = locator
        self._runtime_check = runtime_check
        self._clock = clock
        self._runtime_checked_at = float("-inf")
        self._runtime_status = OperationResult.success()
        self._message = ""

    def available(self) -> bool:
        if not Path(self._locator.installed_path()).exists():
            self._message = InstallHint.for_system(self._system)
            return False
        status = self._cached_runtime_status()
        self._message = "" if status.ok else status.message
        return status.ok

    def _cached_runtime_status(self) -> OperationResult:
        now = self._clock.now()
        if now - self._runtime_checked_at > self.RUNTIME_CHECK_TTL:
            self._runtime_status = self._runtime_check.check()
            self._runtime_checked_at = now
        return self._runtime_status

    def status_message(self) -> str:
        return self._message

    def apply(self, domains: list[str]) -> None:
        self._run("apply" if domains else "clear", domains)

    def clear(self) -> None:
        self._run("clear", [])

    def _run(self, command: str, domains: list[str]) -> None:
        spec = CommandSpec(
            ("sudo", "-n", self._locator.installed_path(), command),
            stdin_text="\n".join(domains),
            timeout=self.TIMEOUT_SECONDS,
        )
        try:
            result = self._runner.run(spec)
        except CommandError as error:
            raise HostsError(str(error)) from error
        if not result.succeeded:
            raise HostsError(self.explain_error(result))

    def explain_error(self, result: CommandResult) -> str:
        output = result.output.strip()
        low = output.lower()
        if "password is required" in low or "not in the sudoers" in low:
            return t("error.helper.no_sudo_permission", hint=InstallHint.for_system(self._system))
        if "xcode-select" in low or "developer tools" in low:
            return t("error.helper.python_missing")
        return output[:200] or f"helper exited with {result.returncode}"
