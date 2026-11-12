from __future__ import annotations

from .tenhut_error import TenhutError


class SettingsError(TenhutError):
    """The settings file cannot be read as settings."""
