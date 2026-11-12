from __future__ import annotations

from collections.abc import Callable

from .hosts_backend import HostsBackend


class DryRunBackend(HostsBackend):
    """Only logs what it would block (`tenhut --dry-run`); never touches the hosts file."""

    def __init__(self, log: Callable[[str], None] = print) -> None:
        self._log = log

    def available(self) -> bool:
        return True

    def status_message(self) -> str:
        return ""

    def apply(self, domains: list[str]) -> None:
        self._log(f"[dry-run] blocking {len(domains)} domains")

    def clear(self) -> None:
        self.apply([])
