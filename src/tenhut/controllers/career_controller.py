from __future__ import annotations

from tenhut.core import Profile
from tenhut.game.audio import SoundEffect
from tenhut.game.painting import Rgb
from tenhut.i18n import t

from .celebration import Celebration
from .feedback import Feedback
from .speech import Speech
from .xp_award import XpAward


class CareerController:
    """Pays out experience and celebrates promotions."""

    PROMOTION_COLOR = Rgb(140, 230, 140)

    def __init__(self, profile: Profile, feedback: Feedback, speech: Speech, *, celebration: Celebration) -> None:
        self._profile = profile
        self._feedback = feedback
        self._speech = speech
        self._celebration = celebration

    def award(self, award: XpAward) -> None:
        promoted = self._profile.add_xp(award.points, pomodoro=award.pomodoro, mission=award.mission)
        self._feedback.popup(f"+{award.points} XP")
        if promoted:
            self._celebrate_promotion()

    def _celebrate_promotion(self) -> None:
        rank = t(self._profile.rank.name_key)
        self._celebration.fireworks()
        self._feedback.play(SoundEffect.VICTORY)
        self._speech.say_next(t("speech.rank.promoted", rank=rank))
        self._feedback.popup(t("popup.promoted", rank=rank), self.PROMOTION_COLOR)
        self._feedback.notify(t("notify.promoted.title"), t("notify.promoted.body", rank=rank))
