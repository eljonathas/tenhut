from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from .monitor import Monitor
from .monitor_provider import MonitorProvider


class GnomeMonitorsXmlProvider(MonitorProvider):
    """Reads the first configuration of GNOME's monitors.xml."""

    DEFAULT_SIZE = (1920, 1080)

    def __init__(self, path: Path) -> None:
        self._path = path

    @classmethod
    def parse(cls, root: ET.Element) -> list[Monitor]:
        configuration = root.find("configuration")
        logical = configuration.findall("logicalmonitor") if configuration is not None else []
        return [cls._monitor(element) for element in logical]

    @classmethod
    def _monitor(cls, element: ET.Element) -> Monitor:
        mode = element.find("monitor/mode")
        scale = float(element.findtext("scale") or 1)
        width, height = cls.DEFAULT_SIZE
        if mode is not None:
            width = int(int(mode.findtext("width")) / scale)
            height = int(int(mode.findtext("height")) / scale)
        return Monitor(
            element.findtext("monitor/monitorspec/connector") or "?",
            int(element.findtext("x") or 0),
            int(element.findtext("y") or 0),
            width,
            height,
            element.find("primary") is not None,
        )

    def list_monitors(self) -> list[Monitor]:
        try:
            return self.parse(ET.parse(self._path).getroot())
        except (OSError, ET.ParseError, ValueError, TypeError):
            return []
