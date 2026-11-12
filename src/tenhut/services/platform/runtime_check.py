from __future__ import annotations

from abc import ABC, abstractmethod

from .operation_result import OperationResult


class RuntimeCheck(ABC):
    """Verifies that the system can run the root helper (it needs a real python3)."""

    @abstractmethod
    def check(self) -> OperationResult: ...
