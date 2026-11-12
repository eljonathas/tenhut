from __future__ import annotations

from .command_runner import CommandRunner
from .elevator_factory import ElevatorFactory
from .helper_installer import HelperInstaller
from .helper_locator import HelperLocator
from .mac_runtime_check import MacRuntimeCheck
from .operating_system import OperatingSystem
from .ready_runtime_check import ReadyRuntimeCheck
from .system_integration import SystemIntegration


class HelperInstallerFactory:
    """Builds the installer of the blocking helper for the running system."""

    @staticmethod
    def create(system: OperatingSystem, runner: CommandRunner, integration: SystemIntegration) -> HelperInstaller:
        check = MacRuntimeCheck(runner) if system.is_mac else ReadyRuntimeCheck()
        elevator = ElevatorFactory.create(system, integration.is_admin())
        return HelperInstaller(system, elevator, runner, runtime_check=check, locator=HelperLocator())
