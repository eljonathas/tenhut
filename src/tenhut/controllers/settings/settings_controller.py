from __future__ import annotations

from tenhut import i18n
from tenhut.controllers.active_settings import ActiveSettings
from tenhut.controllers.calibration_starter import CalibrationStarter
from tenhut.controllers.feedback import Feedback
from tenhut.controllers.helper_install_controller import HelperInstallController
from tenhut.controllers.judge_controller import JudgeController
from tenhut.controllers.navigation import Navigation
from tenhut.controllers.page_id import PageId
from tenhut.controllers.reaction import Reaction
from tenhut.controllers.speech import Speech
from tenhut.controllers.utterance import Utterance
from tenhut.core import Phase, Session, SettingsStore
from tenhut.game.audio import SoundBank, SoundEffect
from tenhut.i18n import t
from tenhut.services.platform import SystemIntegration
from tenhut.services.vision import CameraDependencies

from .change_effect import ChangeEffect
from .change_guard import ChangeGuard
from .setting_key import SettingKey
from .setting_row import SettingRow
from .settings_draft import SettingsDraft
from .settings_row_catalog import SettingsRowCatalog


class SettingsController:
    """Edits a draft of the settings, enforcing the locks of a combat, and saves or drops it."""

    SAVED_SPEECH_SECONDS = 2

    def __init__(
        self,
        active: ActiveSettings,
        store: SettingsStore,
        session: Session,
        *,
        catalog: SettingsRowCatalog,
        sounds: SoundBank,
        speech: Speech,
        feedback: Feedback,
        navigation: Navigation,
        judge: JudgeController,
        installer: HelperInstallController,
        calibration: CalibrationStarter,
        integration: SystemIntegration,
        guards: dict[SettingKey, ChangeGuard],
        effects: dict[SettingKey, ChangeEffect],
        default_effect: ChangeEffect,
    ) -> None:
        self._active = active
        self._store = store
        self._session = session
        self._catalog = catalog
        self._sounds = sounds
        self._speech = speech
        self._feedback = feedback
        self._navigation = navigation
        self._judge = judge
        self._installer = installer
        self._calibration = calibration
        self._integration = integration
        self._guards = guards
        self._effects = effects
        self._default_effect = default_effect
        self._draft = SettingsDraft.from_settings(active.current)
        self._rows: list[SettingRow] = []
        self._rows_key: tuple[int, str] | None = None

    @property
    def locked(self) -> bool:
        return self._session.phase is Phase.WORK

    @property
    def has_camera_calibration(self) -> bool:
        return self._active.current.camera.calibration is not None

    @property
    def installer(self) -> HelperInstallController:
        return self._installer

    def begin_draft(self) -> None:
        self._draft = SettingsDraft.from_settings(self._active.current)

    def value(self, key: SettingKey) -> object:
        return self._draft.get(key)

    def rows(self) -> list[SettingRow]:
        key = (self._draft.revision, i18n.lang())
        if key != self._rows_key:
            self._rows = self._catalog.rows(self._draft)
            self._rows_key = key
        return self._rows

    def click(self, row: SettingRow, direction: int) -> None:
        if self.locked and not row.key.always_unlocked:
            self._speech.say(Utterance(t("speech.settings.locked_during_work"), Reaction.ANGRY_POINT))
            self._feedback.play(SoundEffect.DENIED)
            return
        new_value = row.editor.adjust(self._draft.get(row.key), direction)
        guard = self._guards.get(row.key)
        if guard is not None and not guard.allows(new_value, self._draft):
            return
        self._draft.set(row.key, new_value)
        self._effects.get(row.key, self._default_effect).apply(new_value)

    def request_calibration(self) -> None:
        available = CameraDependencies.check()
        if self.locked:
            self._speech.say(Utterance(t("calibration.speech.not_during_combat"), Reaction.ANGRY_POINT))
        elif not available.ok:
            self._speech.say(Utterance(available.message, Reaction.THINKING_CHIN))
        else:
            self._calibration.start()

    def install_blocker(self) -> None:
        self._installer.install()

    def save(self) -> None:
        current = self._active.current
        if self.locked:
            self._draft = self._draft.keeping_unlocked(current)
        self._active.replace(self._draft.merged_into(current))
        settings = self._active.current
        self._store.save(settings)
        i18n.set_language(settings.language)
        self._sounds.enabled = settings.sound.enabled and self._sounds.available
        self._sounds.set_volume(settings.sound.volume)
        self._judge.refresh_backend()
        self._navigation.open(PageId.MAIN)
        self._say_saved()

    def cancel(self) -> None:
        self._sounds.set_volume(self._active.current.sound.volume)
        self._navigation.open(PageId.MAIN)

    def open_config_file(self) -> None:
        if self.locked:
            self._speech.say(Utterance(t("speech.settings.blocklist_locked"), Reaction.ANGRY_POINT))
            return
        self._store.save(self._active.current)
        self._integration.open_path(self._store.path)
        self._speech.say(
            Utterance(t("speech.settings.config_file_hint", path=self._store.path), Reaction.NEUTRAL_POINT)
        )

    def _say_saved(self) -> None:
        backend = self._judge.backend
        extra = "" if backend.uses_ai else t("speech.settings.saved_no_ai_suffix")
        self._speech.say(
            Utterance(
                t("speech.settings.saved", judge=t(backend.name_key), extra=extra),
                Reaction.HAPPY_THUMBS,
                self.SAVED_SPEECH_SECONDS,
            )
        )
