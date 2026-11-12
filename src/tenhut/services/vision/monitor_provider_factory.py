from __future__ import annotations

from pathlib import Path

from ..platform import CommandRunner, OperatingSystem
from .fallback_monitor_provider import FallbackMonitorProvider
from .gnome_monitors_xml_provider import GnomeMonitorsXmlProvider
from .mac_monitor_provider import MacMonitorProvider
from .monitor_provider import MonitorProvider
from .windows_monitor_provider import WindowsMonitorProvider
from .xrandr_provider import XrandrProvider


class MonitorProviderFactory:
    """Picks the monitor source for the OS."""

    @staticmethod
    def create(system: OperatingSystem, runner: CommandRunner) -> MonitorProvider:
        if system.is_windows:
            return WindowsMonitorProvider()
        if system.is_mac:
            return MacMonitorProvider(runner)
        gnome = GnomeMonitorsXmlProvider(Path.home() / ".config/monitors.xml")
        return FallbackMonitorProvider((XrandrProvider(runner), gnome))
