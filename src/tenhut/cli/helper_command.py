from __future__ import annotations

from abc import ABC, abstractmethod

from tenhut import i18n
from tenhut.i18n import t
from tenhut.services.platform import (
    HelperInstaller,
    HelperInstallerFactory,
    OperatingSystem,
    OperationResult,
    SubprocessCommandRunner,
    SystemIntegration,
)

from .command import Command


class HelperCommand(Command, ABC):
    """Installs or removes the blocking helper without opening the window."""

    @abstractmethod
    def _perform(self, installer: HelperInstaller) -> OperationResult: ...

    @abstractmethod
    def _default_message(self) -> str: ...

    def run(self) -> int:
        i18n.set_language("auto")
        system = OperatingSystem.current()
        if system.is_windows:
            print(t("error.helper.no_helper_on_windows"))
            return 0
        runner = SubprocessCommandRunner.for_system(system)
        installer = HelperInstallerFactory.create(system, runner, SystemIntegration(system, runner))
        result = self._perform(installer)
        print(result.message or self._default_message())
        return 0 if result.ok else 1
