from __future__ import annotations

import threading

from ...i18n import t
from ..platform import HelperError, HelperLocator, SystemIntegration
from .hosts_backend import HostsBackend
from .hosts_error import HostsError


class WindowsDirectBackend(HostsBackend):
    """Windows: the app already runs as administrator and writes the hosts file in-process with the helper code."""

    _write_lock = threading.Lock()

    def __init__(self, system: SystemIntegration, locator: HelperLocator) -> None:
        self._system = system
        self._locator = locator
        self._admin: bool | None = None
        self._message = ""

    def available(self) -> bool:
        if self._admin is None:
            self._admin = self._system.is_admin()
        self._message = "" if self._admin else t("hint.install_blocker.run_as_admin")
        return self._admin

    def status_message(self) -> str:
        return self._message

    def apply(self, domains: list[str]) -> None:
        if not self.available():
            raise HostsError(self._message)
        try:
            helper = self._locator.load_module()
            valid = helper.validate_domains(domains)
            with self._write_lock:
                helper.write_hosts(valid)
        except (HelperError, OSError, ValueError) as error:  # PermissionError (antivirus/ACL), invalid domain...
            raise HostsError((str(error) or type(error).__name__)[:200]) from error

    def clear(self) -> None:
        self.apply([])
