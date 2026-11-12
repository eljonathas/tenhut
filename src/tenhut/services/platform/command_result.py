from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommandResult:
    """The outcome of a finished command."""

    returncode: int
    stdout: str = ""
    stderr: str = ""

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0

    @property
    def output(self) -> str:
        return self.stderr or self.stdout
