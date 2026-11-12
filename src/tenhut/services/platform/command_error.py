from __future__ import annotations

from ...core import TenhutError


class CommandError(TenhutError):
    """An external command could not be started or did not finish."""
