from __future__ import annotations

from tenhut.services.blocking import Blocker, InstallHint
from tenhut.services.platform import OperatingSystem


class BlockingStatus:
    """Whether website blocking can work, and what to tell the soldier when it cannot."""

    def __init__(self, blocker: Blocker, system: OperatingSystem) -> None:
        self._blocker = blocker
        self._system = system

    @property
    def helper_installed(self) -> bool:
        return self._blocker.helper_installed()

    @property
    def last_error(self) -> str:
        return self._blocker.last_error

    @property
    def hint(self) -> str:
        return self._blocker.helper_msg or InstallHint.for_system(self._system)
