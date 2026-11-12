from __future__ import annotations

import pygame

from tenhut.asset_paths import AssetPaths


class FontSet:
    """The bundled DejaVu fonts (same look on every system); else the system's; else pygame's default."""

    BODY_SIZE = 11
    SMALL_SIZE = 10
    TITLE_SIZE = 13
    BIG_SIZE = 38
    MID_SIZE = 16

    def __init__(self) -> None:
        sans_bold = pygame.font.match_font("dejavusans", bold=True) or pygame.font.get_default_font()
        sans = pygame.font.match_font("dejavusans") or sans_bold
        mono_bold = pygame.font.match_font("dejavusansmono", bold=True) or sans_bold
        self._body = self._font("DejaVuSans-Bold.ttf", sans_bold, self.BODY_SIZE)
        self._small = self._font("DejaVuSans.ttf", sans, self.SMALL_SIZE)
        self._title = self._font("DejaVuSans-Bold.ttf", sans_bold, self.TITLE_SIZE)
        self._big = self._font("DejaVuSansMono-Bold.ttf", mono_bold, self.BIG_SIZE)
        self._mid = self._font("DejaVuSansMono-Bold.ttf", mono_bold, self.MID_SIZE)

    @property
    def body(self) -> pygame.font.Font:
        return self._body

    @property
    def small(self) -> pygame.font.Font:
        return self._small

    @property
    def title(self) -> pygame.font.Font:
        return self._title

    @property
    def big(self) -> pygame.font.Font:
        return self._big

    @property
    def mid(self) -> pygame.font.Font:
        return self._mid

    @classmethod
    def _font(cls, bundled: str, fallback: str | None, size: int) -> pygame.font.Font:
        return (
            cls._load(cls._bundled_path(bundled), size)
            or cls._load(fallback, size)
            or pygame.font.Font(pygame.font.get_default_font(), size)
        )

    @staticmethod
    def _bundled_path(name: str) -> str | None:
        path = AssetPaths.fonts_dir() / name
        return str(path) if path.is_file() else None

    @staticmethod
    def _load(path: str | None, size: int) -> pygame.font.Font | None:
        if not path:
            return None
        try:
            return pygame.font.Font(path, size)
        except (OSError, pygame.error):
            return None
