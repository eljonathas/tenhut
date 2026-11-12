from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from .running_process import RunningProcess


class ProcessSource(ABC):
    """Lists the running processes."""

    @abstractmethod
    def processes(self) -> Iterable[RunningProcess]: ...

    @abstractmethod
    def own_pid(self) -> int: ...

    @abstractmethod
    def own_username(self) -> str: ...
