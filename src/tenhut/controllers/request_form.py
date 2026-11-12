from __future__ import annotations

from dataclasses import dataclass

from tenhut.services.judge import RequestKind


@dataclass(frozen=True, slots=True)
class RequestForm:
    """What the soldier typed on the request or desertion page."""

    kind: RequestKind
    target: str
    justification: str
