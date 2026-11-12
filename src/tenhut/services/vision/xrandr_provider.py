from __future__ import annotations

import re

from ..platform import CommandError, CommandRunner, CommandSpec
from .monitor import Monitor
from .monitor_provider import MonitorProvider


class XrandrProvider(MonitorProvider):
    """Monitors from `xrandr --listactivemonitors`."""

    LINE = re.compile(r"^\s*\d+:\s+\+(\*?)(\S+)\s+(\d+)/\d+x(\d+)/\d+\+(-?\d+)\+(-?\d+)", re.M)

    def __init__(self, runner: CommandRunner) -> None:
        self._runner = runner

    @classmethod
    def parse(cls, text: str) -> list[Monitor]:
        """Monitors from the output of `xrandr --listactivemonitors`."""
        return [
            Monitor(m.group(2), int(m.group(5)), int(m.group(6)), int(m.group(3)), int(m.group(4)), bool(m.group(1)))
            for m in cls.LINE.finditer(text)
        ]

    def list_monitors(self) -> list[Monitor]:
        try:
            result = self._runner.run(CommandSpec(("xrandr", "--listactivemonitors"), timeout=5))
        except CommandError:
            return []
        return self.parse(result.stdout)
