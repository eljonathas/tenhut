from __future__ import annotations

import json
from pathlib import Path

from .clock import Clock
from .session import Session


class SessionStore:
    """Reads and writes state.json."""

    def __init__(self, path: Path, clock: Clock | None = None) -> None:
        self._path = path
        self._clock = clock

    def load(self) -> Session:
        """The saved session, or a fresh one when the file is missing or unusable."""
        session = Session(self._clock, self)
        try:
            session.restore(json.loads(self._path.read_text()))
        except (OSError, json.JSONDecodeError, TypeError, ValueError, AttributeError):
            return Session(self._clock, self)
        return session

    def save(self, session: Session) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(session.to_dict(), ensure_ascii=False, indent=1))
        tmp.replace(self._path)
