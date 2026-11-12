from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from pathlib import Path

from ... import i18n
from ...asset_paths import AssetPaths
from ...i18n import t

APP_ID = "tenhut"
APP_NAME = "Tenhut"


class DesktopIntegration(ABC):
    """What the app does for the desktop it runs on; the window identity is common to every OS."""

    supported = False

    def __init__(self, environ: MutableMapping[str, str] | None = None) -> None:
        self._environ = os.environ if environ is None else environ

    def window_identity(self) -> None:
        """Set the window class BEFORE pygame/SDL creates the window."""
        self._environ.setdefault("SDL_VIDEO_X11_WMCLASS", APP_ID)
        self._environ.setdefault("SDL_VIDEO_WAYLAND_WMCLASS", APP_ID)
        self._environ.setdefault("SDL_APP_NAME", APP_NAME)

    @staticmethod
    def window_icon_path() -> Path:
        return AssetPaths.icons_dir() / "icon-128.png"

    @abstractmethod
    def install(self) -> list[Path]:
        """Install the launcher and icons; returns the files written."""

    @abstractmethod
    def uninstall(self) -> None: ...

    def cli_install(self) -> int:
        """Implements --install-desktop; where unsupported it prints a friendly message and succeeds."""
        i18n.set_language("auto")
        if not self.supported:
            print(t("error.desktop.linux_only"))
            return 0
        for path in self.install():
            print(path)
        print(t("status.desktop.installed", app=APP_NAME))
        return 0

    def cli_uninstall(self) -> int:
        i18n.set_language("auto")
        if not self.supported:
            print(t("error.desktop.linux_only"))
            return 0
        self.uninstall()
        print(t("status.desktop.removed", app=APP_NAME))
        return 0
