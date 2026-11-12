from __future__ import annotations

from ...i18n import t
from .command_error import CommandError
from .command_runner import CommandRunner
from .command_spec import CommandSpec
from .operation_result import OperationResult
from .runtime_check import RuntimeCheck


class MacRuntimeCheck(RuntimeCheck):
    """macOS: /usr/bin/python3 is only a stub until the Command Line Tools are installed."""

    def __init__(self, runner: CommandRunner) -> None:
        self._runner = runner

    def check(self) -> OperationResult:
        try:
            if self._runner.run(CommandSpec(("xcode-select", "-p"), timeout=5)).succeeded:
                return OperationResult.success()
        except CommandError:
            pass
        return OperationResult.failure(t("error.helper.python_missing"))
