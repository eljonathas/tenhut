from __future__ import annotations

from typing import Protocol


class RunningProcess(Protocol):
    """The slice of a process the killer needs (psutil.Process satisfies it)."""

    pid: int

    def name(self) -> str: ...

    def username(self) -> str: ...

    def terminate(self) -> None: ...
