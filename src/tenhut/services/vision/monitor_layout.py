from __future__ import annotations

from ...core import MonitorSide
from .monitor import Monitor
from .monitor_provider import MonitorProvider


class MonitorLayout:
    """Where the other monitors are, relative to the one the camera sits on."""

    SIDE_TOLERANCE_PX = 50

    def __init__(self, provider: MonitorProvider) -> None:
        self._provider = provider

    def sides(self, camera_monitor: str = "") -> dict[MonitorSide, list[str]]:
        """Names of the monitors left and right of the camera's; empty with fewer than two monitors."""
        monitors = self._provider.list_monitors()
        out: dict[MonitorSide, list[str]] = {MonitorSide.LEFT: [], MonitorSide.RIGHT: []}
        if len(monitors) < 2:
            return out
        camera = self._camera_monitor(monitors, camera_monitor)
        for monitor in monitors:
            if monitor is camera:
                continue
            if monitor.right <= camera.x + self.SIDE_TOLERANCE_PX:
                out[MonitorSide.LEFT].append(monitor.name)
            elif monitor.x >= camera.right - self.SIDE_TOLERANCE_PX:
                out[MonitorSide.RIGHT].append(monitor.name)
        return out

    @staticmethod
    def _camera_monitor(monitors: list[Monitor], name: str) -> Monitor:
        named = next((m for m in monitors if m.name == name), None)
        return named or next((m for m in monitors if m.primary), monitors[0])
