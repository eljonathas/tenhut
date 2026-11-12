from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .button_style import ButtonStyle

ButtonAction = Callable[[], None]


@dataclass(frozen=True, slots=True)
class ButtonSpec:
    """What a page wants from a button; the row decides where it goes."""

    label: str
    action: ButtonAction
    style: ButtonStyle = ButtonStyle.TAN
    enabled: bool = True
