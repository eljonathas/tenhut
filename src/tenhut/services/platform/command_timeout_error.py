from __future__ import annotations

from .command_error import CommandError


class CommandTimeoutError(CommandError):
    """An external command ran past its timeout."""
