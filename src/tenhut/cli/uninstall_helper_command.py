from __future__ import annotations

from tenhut.i18n import t
from tenhut.services.platform import HelperInstaller, OperationResult

from .helper_command import HelperCommand


class UninstallHelperCommand(HelperCommand):
    """--uninstall-helper"""

    def _perform(self, installer: HelperInstaller) -> OperationResult:
        return installer.uninstall()

    def _default_message(self) -> str:
        return t("status.helper.removed")
