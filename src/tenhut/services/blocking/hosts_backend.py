from __future__ import annotations

from abc import ABC, abstractmethod


class HostsBackend(ABC):
    """Writes exactly the given domains into the hosts file, or removes them all."""

    @abstractmethod
    def available(self) -> bool:
        """Can blocking work? Cheap (called every frame); the reason is in `status_message()`."""

    @abstractmethod
    def status_message(self) -> str:
        """Why blocking is inactive; empty when it is active. Meaningful after `available()`."""

    @abstractmethod
    def apply(self, domains: list[str]) -> None:
        """Block exactly `domains`. Raises HostsError on failure."""

    @abstractmethod
    def clear(self) -> None:
        """Remove every block. Raises HostsError on failure."""
