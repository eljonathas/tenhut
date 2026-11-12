from __future__ import annotations

import threading

from ...core import Clock
from .hosts_backend import HostsBackend
from .hosts_error import HostsError


class Blocker:
    """Keeps the hosts file in the desired state without freezing the interface.

    `apply()` only records the desired state; a worker thread talks to the backend (the sudo helper takes
    hundreds of milliseconds). A failure is retried after `retry_seconds`, not on every frame.
    """

    RETRY_SECONDS = 30
    MIN_WAIT_SECONDS = 0.5

    def __init__(self, backend: HostsBackend, clock: Clock, retry_seconds: float = RETRY_SECONDS) -> None:
        self._backend = backend
        self._clock = clock
        self._retry_seconds = retry_seconds
        self._applied: list[str] | None = None
        self._desired: list[str] | None = None
        self._last_error = ""
        self._next_retry = 0.0
        self._condition = threading.Condition()
        threading.Thread(target=self._work, daemon=True, name="blocker").start()

    @property
    def last_error(self) -> str:
        return self._last_error

    @property
    def applied(self) -> list[str] | None:
        return self._applied

    @property
    def helper_msg(self) -> str:
        return self._backend.status_message()

    def helper_installed(self) -> bool:
        return self._backend.available()

    def apply(self, domains: list[str]) -> None:
        """Ask the hosts file to block exactly `domains` (non-blocking, idempotent)."""
        with self._condition:
            if domains != self._desired:
                self._desired = domains
                self._next_retry = 0.0
                self._condition.notify()

    def clear(self) -> None:
        self.apply([])

    def retry_now(self) -> None:
        with self._condition:
            self._next_retry = 0.0
            self._last_error = ""
            self._condition.notify()

    def reassert(self) -> None:
        """Apply the current state again, in case somebody edited the hosts file."""
        with self._condition:
            if not self._last_error:
                self._applied = None
                self._condition.notify()

    def apply_now(self, domains: list[str]) -> bool:
        """Synchronous version, for the app's exit."""
        ok = self._write(domains)
        if ok:
            with self._condition:
                self._applied = self._desired = domains
        return ok

    def _wait_for_work(self) -> list[str]:
        with self._condition:
            while True:
                wanted = self._desired
                pending = wanted is not None and wanted != self._applied
                wait = self._next_retry - self._clock.now()
                if pending and wait <= 0:
                    return wanted
                self._condition.wait(max(self.MIN_WAIT_SECONDS, wait) if pending else None)

    def _work(self) -> None:
        while True:
            wanted = self._wait_for_work()
            ok = self._write(wanted)
            with self._condition:
                if ok:
                    self._applied = wanted
                else:
                    self._next_retry = self._clock.now() + self._retry_seconds

    def _write(self, domains: list[str]) -> bool:
        try:
            if domains:
                self._backend.apply(domains)
            else:
                self._backend.clear()
        except HostsError as error:
            self._last_error = str(error)
            return False
        self._last_error = ""
        return True
