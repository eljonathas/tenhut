from __future__ import annotations

from abc import ABC, abstractmethod

from .command_result import CommandResult
from .command_spec import CommandSpec


class CommandRunner(ABC):
    """Runs external commands; injected so logic can be tested without spawning processes."""

    @abstractmethod
    def run(self, spec: CommandSpec) -> CommandResult:
        """Run to completion. Raises CommandTimeoutError / CommandError."""

    @abstractmethod
    def launch(self, spec: CommandSpec) -> None:
        """Start without waiting and discard the output. Raises CommandError if it cannot start."""
