from __future__ import annotations

from tenhut.core import Settings


class ActiveSettings:
    """The settings in force; replaced as a whole when the user saves or the camera is calibrated."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def current(self) -> Settings:
        return self._settings

    def replace(self, settings: Settings) -> None:
        self._settings = settings
