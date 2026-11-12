from __future__ import annotations

import json
from pathlib import Path

from .profile import Profile


class ProfileStore:
    """Reads and writes profile.json (the old file called the missions count `missoes`)."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> Profile:
        try:
            data = json.loads(self._path.read_text())
            return Profile(
                int(data.get("xp", 0)),
                int(data.get("pomodoros", 0)),
                int(data.get("missions", data.get("missoes", 0))),
                store=self,
            )
        except (OSError, json.JSONDecodeError, TypeError, ValueError, AttributeError):
            return Profile(store=self)

    def save(self, profile: Profile) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(profile.to_dict()))
