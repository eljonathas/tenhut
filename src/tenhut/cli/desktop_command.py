from __future__ import annotations

from abc import ABC

from tenhut.services.platform import DesktopFactory, DesktopIntegration, OperatingSystem, SubprocessCommandRunner

from .command import Command


class DesktopCommand(Command, ABC):
    """Adds or removes the launcher in the desktop's application menu."""

    @staticmethod
    def _desktop() -> DesktopIntegration:
        system = OperatingSystem.current()
        return DesktopFactory.create(system, SubprocessCommandRunner.for_system(system))
