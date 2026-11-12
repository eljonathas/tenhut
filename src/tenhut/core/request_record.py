from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RequestRecord:
    """One judged request, as written to the log."""

    timestamp: float
    kind: str
    target: str
    justification: str
    approved: bool
    groups: tuple[str, ...]
    minutes: int
    speech: str
    error: str

    def to_dict(self) -> dict[str, object]:
        return {
            "ts": self.timestamp,
            "kind": self.kind,
            "target": self.target,
            "justification": self.justification,
            "approved": self.approved,
            "groups": list(self.groups),
            "minutes": self.minutes,
            "speech": self.speech,
            "error": self.error,
        }
