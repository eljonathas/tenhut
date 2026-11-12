from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OperationResult:
    """Outcome of an operation that reports a short message for the interface."""

    ok: bool
    message: str = ""

    @classmethod
    def success(cls, message: str = "") -> OperationResult:
        return cls(True, message)

    @classmethod
    def failure(cls, message: str) -> OperationResult:
        return cls(False, message)
