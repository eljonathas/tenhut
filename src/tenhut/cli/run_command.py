from __future__ import annotations

import contextlib

from tenhut.application_options import ApplicationOptions
from tenhut.services.platform import (
    DesktopFactory,
    DesktopIntegration,
    OperatingSystem,
    SubprocessCommandRunner,
    SystemIntegration,
)

from .command import Command


class RunCommand(Command):
    """Opens the window and plays."""

    def __init__(self, dry_run: bool) -> None:
        self._dry_run = dry_run

    @property
    def dry_run(self) -> bool:
        return self._dry_run

    def run(self) -> int:
        system = OperatingSystem.current()
        runner = SubprocessCommandRunner.for_system(system)
        SystemIntegration(system, runner).set_app_id()
        desktop = DesktopFactory.create(system, runner)
        desktop.window_identity()  # before SDL is loaded
        self._open_display(desktop)
        from tenhut.application import Application

        Application(ApplicationOptions(dry_run=self._dry_run)).run()
        return 0

    @staticmethod
    def _open_display(desktop: DesktopIntegration) -> None:
        import pygame

        pygame.display.init()
        with contextlib.suppress(pygame.error, FileNotFoundError):
            pygame.display.set_icon(pygame.image.load(str(desktop.window_icon_path())))
