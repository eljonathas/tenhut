from __future__ import annotations

from dataclasses import dataclass

from tenhut.controllers.active_settings import ActiveSettings
from tenhut.controllers.judge_slot import JudgeSlot
from tenhut.controllers.navigation import Navigation
from tenhut.core import Clock, Session
from tenhut.ui.fonts import FontSet
from tenhut.ui.layout import LayoutProvider


@dataclass(frozen=True, slots=True)
class PageContext:
    """What every page needs: the fonts and layout to draw with, and the state it shows."""

    fonts: FontSet
    layouts: LayoutProvider
    session: Session
    settings: ActiveSettings
    clock: Clock
    navigation: Navigation
    judge_slot: JudgeSlot
