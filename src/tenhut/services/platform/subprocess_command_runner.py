from __future__ import annotations

import os
import subprocess

from .command_error import CommandError
from .command_result import CommandResult
from .command_runner import CommandRunner
from .command_spec import CommandSpec
from .command_timeout_error import CommandTimeoutError
from .operating_system import OperatingSystem

CREATE_NO_WINDOW = 0x08000000


class SubprocessCommandRunner(CommandRunner):
    """The real runner, built on `subprocess`."""

    def __init__(self, hide_console: bool = False) -> None:
        self._extra = {"creationflags": CREATE_NO_WINDOW} if hide_console else {}

    @classmethod
    def for_system(cls, system: OperatingSystem) -> SubprocessCommandRunner:
        return cls(hide_console=system.is_windows)

    @staticmethod
    def _environment(spec: CommandSpec) -> dict[str, str] | None:
        return {**os.environ, **spec.extra_env} if spec.extra_env else None

    def run(self, spec: CommandSpec) -> CommandResult:
        try:
            done = subprocess.run(
                list(spec.argv),
                input=spec.stdin_text,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=spec.timeout,
                cwd=spec.cwd,
                env=self._environment(spec),
                stdin=None if spec.stdin_text is not None else subprocess.DEVNULL,
                **self._extra,
            )
        except subprocess.TimeoutExpired as error:
            raise CommandTimeoutError(str(error)) from error
        except OSError as error:
            raise CommandError(str(error)) from error
        return CommandResult(done.returncode, done.stdout or "", done.stderr or "")

    def launch(self, spec: CommandSpec) -> None:
        try:
            subprocess.Popen(
                list(spec.argv),
                env=self._environment(spec),
                cwd=spec.cwd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **self._extra,
            )
        except OSError as error:
            raise CommandError(str(error)) from error
