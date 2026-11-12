from __future__ import annotations

from .monitor import Monitor
from .monitor_provider import MonitorProvider


class FallbackMonitorProvider(MonitorProvider):
    """The first provider that finds any monitor wins."""

    def __init__(self, providers: tuple[MonitorProvider, ...]) -> None:
        self._providers = providers

    def list_monitors(self) -> list[Monitor]:
        for provider in self._providers:
            monitors = provider.list_monitors()
            if monitors:
                return monitors
        return []
