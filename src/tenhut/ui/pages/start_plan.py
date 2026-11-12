from __future__ import annotations

from tenhut.core import Phase
from tenhut.i18n import t
from tenhut.ui.widgets import ButtonSpec, ButtonStyle

from .main_button_plan import MainButtonPlan


class StartPlan(MainButtonPlan):
    """Nothing going on: start a mission."""

    def applies(self, phase: Phase, pending: int) -> bool:
        return True

    def specs(self, compact: bool) -> list[ButtonSpec]:
        if compact:
            return [
                ButtonSpec(t("button.mission_short"), self._mission.new_mission, ButtonStyle.GREEN),
                self._tasks_spec(compact),
                self._settings_spec(),
            ]
        return [
            ButtonSpec(t("button.new_mission"), self._mission.new_mission, ButtonStyle.GREEN),
            self._settings_spec(),
        ]
