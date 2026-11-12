from __future__ import annotations

from enum import Enum


class EditorKind(Enum):
    """How a settings row is operated: one switch, or a minus and a plus."""

    TOGGLE = "toggle"
    STEPPER = "stepper"
