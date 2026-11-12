from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .command import Command


@dataclass(frozen=True, slots=True)
class CommandFlag:
    """A command-line switch, the key of its help text, the command it selects and its weight when several are given."""

    option: str
    help_key: str
    command: Callable[[], Command]
    priority: int

    @property
    def attribute(self) -> str:
        return self.option.lstrip("-").replace("-", "_")
