from __future__ import annotations

from tenhut.controllers.calibration_starter import CalibrationStarter
from tenhut.controllers.reaction import Reaction
from tenhut.controllers.speech import Speech
from tenhut.controllers.utterance import Utterance
from tenhut.i18n import t
from tenhut.services.vision import CameraDependencies

from .change_guard import ChangeGuard
from .settings_draft import SettingsDraft


class CameraEnableGuard(ChangeGuard):
    """Switching the camera on needs its extras installed and a calibration; without one it starts calibrating."""

    def __init__(self, speech: Speech, calibration: CalibrationStarter) -> None:
        self._speech = speech
        self._calibration = calibration

    def allows(self, new_value: object, draft: SettingsDraft) -> bool:
        if not new_value:
            return True
        availability = CameraDependencies.check()
        if not availability.ok:
            self._speech.say(Utterance(availability.message, Reaction.THINKING_CHIN))
            return False
        if not draft.has_camera_calibration:
            self._speech.say(Utterance(t("calibration.speech.calibrate_first"), Reaction.NEUTRAL_POINT))
            self._calibration.start()
            return False
        return True
