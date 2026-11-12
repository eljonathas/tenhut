"""Operating-system integration: data folders, notifications, privilege elevation, desktop launcher."""

from .app_paths import APP_DIR, AppPaths
from .command_error import CommandError
from .command_result import CommandResult
from .command_runner import CommandRunner
from .command_spec import CommandSpec
from .command_timeout_error import CommandTimeoutError
from .desktop_factory import DesktopFactory
from .desktop_integration import APP_ID, APP_NAME, DesktopIntegration
from .elevator import Elevator
from .elevator_factory import ElevatorFactory
from .helper_error import HelperError
from .helper_installer import HelperInstaller
from .helper_installer_factory import HelperInstallerFactory
from .helper_locator import HelperLocator
from .helper_scripts import HelperScripts
from .legacy_data_migration import LegacyDataMigration
from .linux_desktop import LinuxDesktop
from .linux_notifier import LinuxNotifier
from .mac_notifier import MacNotifier
from .mac_runtime_check import MacRuntimeCheck
from .no_elevator import NoElevator
from .notifier import Notifier
from .notifier_factory import NotifierFactory
from .operating_system import OperatingSystem
from .operation_result import OperationResult
from .osascript_elevator import OsascriptElevator
from .pkexec_elevator import PkexecElevator
from .ready_runtime_check import ReadyRuntimeCheck
from .root_elevator import RootElevator
from .runtime_check import RuntimeCheck
from .subprocess_command_runner import SubprocessCommandRunner
from .system_integration import SystemIntegration
from .unsupported_desktop import UnsupportedDesktop
from .windows_notifier import WindowsNotifier

__all__ = [
    "APP_DIR",
    "APP_ID",
    "APP_NAME",
    "AppPaths",
    "CommandError",
    "CommandResult",
    "CommandRunner",
    "CommandSpec",
    "CommandTimeoutError",
    "DesktopFactory",
    "DesktopIntegration",
    "Elevator",
    "ElevatorFactory",
    "HelperError",
    "HelperInstaller",
    "HelperInstallerFactory",
    "HelperLocator",
    "HelperScripts",
    "LegacyDataMigration",
    "LinuxDesktop",
    "LinuxNotifier",
    "MacNotifier",
    "MacRuntimeCheck",
    "NoElevator",
    "Notifier",
    "NotifierFactory",
    "OperatingSystem",
    "OperationResult",
    "OsascriptElevator",
    "PkexecElevator",
    "ReadyRuntimeCheck",
    "RootElevator",
    "RuntimeCheck",
    "SubprocessCommandRunner",
    "SystemIntegration",
    "UnsupportedDesktop",
    "WindowsNotifier",
]
