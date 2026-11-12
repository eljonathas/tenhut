from __future__ import annotations

from .operation_result import OperationResult
from .runtime_check import RuntimeCheck


class ReadyRuntimeCheck(RuntimeCheck):
    """Systems where python3 is always usable."""

    def check(self) -> OperationResult:
        return OperationResult.success()
