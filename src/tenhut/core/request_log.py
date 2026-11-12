from __future__ import annotations

import json
from pathlib import Path

from .request_record import RequestRecord


class RequestLog:
    """Append-only log of the soldier's requests (one JSON object per line)."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def append(self, record: RequestRecord) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a") as handle:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
