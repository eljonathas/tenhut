from __future__ import annotations

from collections.abc import Iterable

import psutil

from .process_source import ProcessSource
from .running_process import RunningProcess


class PsutilProcessSource(ProcessSource):
    """The real process list, from psutil."""

    def processes(self) -> Iterable[RunningProcess]:
        return psutil.process_iter()

    def own_pid(self) -> int:
        return psutil.Process().pid

    def own_username(self) -> str:
        return psutil.Process().username()
