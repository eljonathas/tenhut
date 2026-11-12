from __future__ import annotations

import psutil

from .process_source import ProcessSource


class ProcessKiller:
    """Terminates the current user's processes whose name matches the blocked apps."""

    def __init__(self, source: ProcessSource) -> None:
        self._source = source

    @staticmethod
    def normalize(name: str) -> str:
        """Comparable across systems: lowercase, without a trailing ".exe"."""
        lowered = (name or "").strip().lower()
        return lowered[:-4] if lowered.endswith(".exe") else lowered

    def kill(self, names: list[str]) -> list[str]:
        """Terminate matching processes; returns the sorted names that were closed."""
        wanted = {self.normalize(n) for n in names} - {""}
        if not wanted:
            return []
        closed = {name for process in self._source.processes() if (name := self._terminate(process, wanted))}
        return sorted(closed)

    def _terminate(self, process, wanted: set[str]) -> str | None:
        try:
            name = self.normalize(process.name())
            if process.pid == self._source.own_pid() or name not in wanted:
                return None
            if process.username() != self._source.own_username():
                return None
            process.terminate()
            return name
        except psutil.Error:
            return None
