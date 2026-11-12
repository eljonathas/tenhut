from __future__ import annotations

from abc import ABC, abstractmethod

from tenhut.controllers.judge_controller import JudgeController
from tenhut.controllers.mission_controller import MissionController
from tenhut.controllers.page_id import PageId
from tenhut.core import Phase
from tenhut.i18n import t
from tenhut.ui.widgets import ButtonSpec, ButtonStyle

from .page_links import PageLinks


class MainButtonPlan(ABC):
    """Which buttons the main page offers in one situation."""

    def __init__(self, mission: MissionController, judge: JudgeController, links: PageLinks) -> None:
        self._mission = mission
        self._judge = judge
        self._links = links

    @abstractmethod
    def applies(self, phase: Phase, pending: int) -> bool: ...

    @abstractmethod
    def specs(self, compact: bool) -> list[ButtonSpec]: ...

    def _tasks_spec(self, compact: bool) -> ButtonSpec:
        if compact:
            return ButtonSpec(t("button.board"), self._links.to(PageId.BOARD), ButtonStyle.TAN)
        return ButtonSpec(t("button.add_task"), self._links.to(PageId.MISSION), ButtonStyle.TAN)

    def _desert_spec(self) -> ButtonSpec:
        return ButtonSpec(t("button.desert"), self._links.to(PageId.DESERTION), ButtonStyle.RED)

    def _settings_spec(self) -> ButtonSpec:
        return ButtonSpec(t("button.settings"), self._links.to(PageId.SETTINGS), ButtonStyle.TAN)
