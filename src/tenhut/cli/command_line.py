from __future__ import annotations

import argparse
from collections.abc import Sequence
from typing import ClassVar

from tenhut import i18n
from tenhut.i18n import t

from .command import Command
from .command_flag import CommandFlag
from .install_desktop_command import InstallDesktopCommand
from .install_helper_command import InstallHelperCommand
from .run_command import RunCommand
from .uninstall_desktop_command import UninstallDesktopCommand
from .uninstall_helper_command import UninstallHelperCommand


class CommandLine:
    """Reads the command line and picks the command to run; with several switches the heaviest one wins."""

    FLAGS: ClassVar[tuple[CommandFlag, ...]] = (
        CommandFlag("--install-desktop", "hint.cli.install_desktop", InstallDesktopCommand, priority=2),
        CommandFlag("--uninstall-desktop", "hint.cli.uninstall_desktop", UninstallDesktopCommand, priority=1),
        CommandFlag("--install-helper", "hint.cli.install_helper", InstallHelperCommand, priority=3),
        CommandFlag("--uninstall-helper", "hint.cli.uninstall_helper", UninstallHelperCommand, priority=4),
    )

    def __init__(self, arguments: Sequence[str] | None = None) -> None:
        self._arguments = arguments

    def command(self) -> Command:
        i18n.set_language("auto")
        parser = argparse.ArgumentParser(prog="tenhut", description=t("hint.cli.description"))
        parser.add_argument("--dry-run", action="store_true", help=t("hint.cli.dry_run"))
        for flag in self.FLAGS:
            parser.add_argument(flag.option, action="store_true", help=t(flag.help_key))
        chosen = parser.parse_args(self._arguments)
        given = [flag for flag in self.FLAGS if getattr(chosen, flag.attribute)]
        selected = max(given, key=lambda flag: flag.priority, default=None)
        return selected.command() if selected else RunCommand(chosen.dry_run)
