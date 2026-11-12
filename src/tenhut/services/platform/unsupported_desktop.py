from __future__ import annotations

from pathlib import Path

from .desktop_integration import DesktopIntegration


class UnsupportedDesktop(DesktopIntegration):
    """macOS and Windows: no launcher integration."""

    def install(self) -> list[Path]:
        return []

    def uninstall(self) -> None:
        return None
