"""The command line: one command per switch."""

from .command import Command
from .command_flag import CommandFlag
from .command_line import CommandLine
from .desktop_command import DesktopCommand
from .helper_command import HelperCommand
from .install_desktop_command import InstallDesktopCommand
from .install_helper_command import InstallHelperCommand
from .run_command import RunCommand
from .uninstall_desktop_command import UninstallDesktopCommand
from .uninstall_helper_command import UninstallHelperCommand

__all__ = [
    "Command",
    "CommandFlag",
    "CommandLine",
    "DesktopCommand",
    "HelperCommand",
    "InstallDesktopCommand",
    "InstallHelperCommand",
    "RunCommand",
    "UninstallDesktopCommand",
    "UninstallHelperCommand",
]
