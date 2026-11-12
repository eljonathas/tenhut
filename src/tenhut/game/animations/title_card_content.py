from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TitleCardContent:
    title: str
    subtitle: str
