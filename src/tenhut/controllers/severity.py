from __future__ import annotations

from enum import Enum


class Severity(Enum):
    """How a status line should be coloured."""

    NOTICE = "notice"
    SUCCESS = "success"
    WARNING = "warning"
    MUTED = "muted"
    ALERT = "alert"
