from __future__ import annotations

from ...core import Clock
from ..platform import (
    CommandRunner,
    HelperLocator,
    MacRuntimeCheck,
    OperatingSystem,
    ReadyRuntimeCheck,
    SystemIntegration,
)
from .dry_run_backend import DryRunBackend
from .hosts_backend import HostsBackend
from .posix_helper_backend import PosixHelperBackend
from .windows_direct_backend import WindowsDirectBackend


class HostsBackendFactory:
    """Picks the hosts-file strategy for the platform (or the logging one for a dry run)."""

    def __init__(self, runner: CommandRunner, clock: Clock) -> None:
        self._runner = runner
        self._clock = clock

    def create(self, system: OperatingSystem, dry_run: bool = False) -> HostsBackend:
        if dry_run:
            return DryRunBackend()
        locator = HelperLocator()
        if system.is_windows:
            return WindowsDirectBackend(SystemIntegration(system, self._runner), locator)
        check = MacRuntimeCheck(self._runner) if system.is_mac else ReadyRuntimeCheck()
        return PosixHelperBackend(system, self._runner, locator=locator, runtime_check=check, clock=self._clock)
