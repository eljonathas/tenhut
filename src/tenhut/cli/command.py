from __future__ import annotations

from abc import ABC, abstractmethod


class Command(ABC):
    """One thing the command line can ask the program to do."""

    @abstractmethod
    def run(self) -> int:
        """Does it and returns the process exit code."""
