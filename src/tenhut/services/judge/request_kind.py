from __future__ import annotations

from enum import Enum


class RequestKind(Enum):
    """What the soldier is asking the judge for."""

    ACCESS = "access"
    DESERTION = "desertion"
