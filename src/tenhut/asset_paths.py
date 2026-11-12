from __future__ import annotations

import sys
from pathlib import Path


class AssetPaths:
    """Where the packaged assets live, also inside a PyInstaller bundle."""

    @staticmethod
    def root() -> Path:
        bundle = getattr(sys, "_MEIPASS", None)
        if bundle:
            return Path(bundle) / "tenhut" / "assets"
        return Path(__file__).resolve().parent / "assets"

    @classmethod
    def fonts_dir(cls) -> Path:
        return cls.root() / "fonts"

    @classmethod
    def icons_dir(cls) -> Path:
        return cls.root() / "icons"
