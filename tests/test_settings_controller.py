import pytest

from fakes import FakeBackend, FakeClock, FakeFeedback, FakeNavigation, FakeRunner, FakeSpeech
from tenhut import i18n
from tenhut.controllers import ActiveSettings, HelperInstallController, PageId
from tenhut.controllers.settings import (
    CameraEnableGuard,
    ChoiceEditor,
    ClickEffect,
    JudgeEditor,
    LanguageEditor,
    NumberEditor,
    NumberRange,
    SettingKey,
    SettingsController,
    SettingsDraft,
    SettingsRowCatalog,
    ToggleEditor,
    VolumePreviewEffect,
)
from tenhut.core import Phase, Session, Settings, SettingsStore
from tenhut.game.audio import SoundBank, SoundEffect
from tenhut.services.blocking import Blocker
from tenhut.services.judge import JudgeFactory
from tenhut.services.platform import OperatingSystem, SystemIntegration


class StubJudge:
    class Backend:
        uses_ai = False
        name_key = "judge.name.none"

    backend = Backend()

    def __init__(self):
        self.refreshed = 0

    def refresh_backend(self):
        self.refreshed += 1


class StubCalibration:
    def __init__(self):
        self.started = 0

    def start(self):
        self.started += 1


class Setup:
    def __init__(self, tmp_path):
        clock = FakeClock()
        self.session = Session(clock)
        self.active = ActiveSettings(Settings())
        self.store = SettingsStore(tmp_path / "config.json")
        self.sounds = SoundBank(False)
        self.speech, self.feedback, self.navigation = FakeSpeech(), FakeFeedback(), FakeNavigation()
        self.judge, self.calibration = StubJudge(), StubCalibration()
        installer = HelperInstallController(
            session=self.session,
            system=OperatingSystem.LINUX,
            runner=FakeRunner(),
            integration=SystemIntegration(OperatingSystem.LINUX, FakeRunner()),
            blocker=Blocker(FakeBackend(), clock),
            speech=self.speech,
            feedback=self.feedback,
        )
        self.controller = SettingsController(
            active=self.active,
            store=self.store,
            session=self.session,
            catalog=SettingsRowCatalog(JudgeFactory(FakeRunner(), clock), tmp_path),
            sounds=self.sounds,
            speech=self.speech,
            feedback=self.feedback,
            navigation=self.navigation,
            judge=self.judge,
            installer=installer,
            calibration=self.calibration,
            integration=SystemIntegration(OperatingSystem.LINUX, FakeRunner()),
            guards={SettingKey.CAMERA_ENABLED: CameraEnableGuard(self.speech, self.calibration)},
            effects={SettingKey.VOLUME: VolumePreviewEffect(self.sounds, self.feedback)},
            default_effect=ClickEffect(self.feedback),
        )
        self.controller.begin_draft()

    def row(self, key):
        return next(row for row in self.controller.rows() if row.key is key)

    def work(self):
        self.session._phase = Phase.WORK


@pytest.fixture
def setup(tmp_path):
    return Setup(tmp_path)


class TestSettingsDraft:
    def test_values_are_read_and_written_by_key(self):
        draft = SettingsDraft.from_settings(Settings())
        draft.set(SettingKey.WORK_MINUTES, 30)
        draft.set(SettingKey.CAMERA_TOLERANCE, 9)
        assert draft.get(SettingKey.WORK_MINUTES) == 30 and draft.get(SettingKey.CAMERA_TOLERANCE) == 9
        assert draft.as_settings().timer.work_minutes == 30
        assert draft.as_settings().camera.tolerance_seconds == 9

    def test_every_edit_bumps_the_revision(self):
        draft = SettingsDraft.from_settings(Settings())
        before = draft.revision
        draft.set(SettingKey.VOLUME, 10)
        assert draft.revision == before + 1

    def test_during_a_combat_only_the_unlocked_edits_survive(self):
        base = Settings()
        draft = SettingsDraft.from_settings(base)
        draft.set(SettingKey.VOLUME, 5)
        draft.set(SettingKey.WORK_MINUTES, 99)
        merged = draft.keeping_unlocked(base).merged_into(base)
        assert merged.sound.volume == 5 and merged.timer.work_minutes == base.timer.work_minutes

    def test_the_calibration_flag(self):
        assert not SettingsDraft.from_settings(Settings()).has_camera_calibration


class TestEditors:
    def test_toggle_flips(self):
        assert ToggleEditor().adjust(False, 1) is True and ToggleEditor().adjust(True, -1) is False

    def test_choice_cycles_both_ways_and_recovers_from_unknown_values(self):
        editor = ChoiceEditor(["a", "b", "c"])
        assert editor.adjust("c", 1) == "a" and editor.adjust("a", -1) == "c" and editor.adjust("zzz", 1) == "a"

    def test_number_is_clamped_to_its_range(self):
        editor = NumberEditor(NumberRange(5, 5, 20))
        assert editor.adjust(20, 1) == 20 and editor.adjust(5, -1) == 5 and editor.adjust(10, 1) == 15

    def test_the_default_model_is_shown_as_default(self):
        assert ChoiceEditor([""]).shown("") == i18n.t("settings.value.default")

    def test_language_and_judge_names_are_translated(self):
        assert LanguageEditor().shown("pt") == i18n.t("language.name.pt")
        assert JudgeEditor().shown("none") == i18n.t("settings.value.none")
        assert JudgeEditor().shown("claude") == "claude"

    def test_only_sound_volume_and_language_stay_open_during_a_combat(self):
        open_keys = {key for key in SettingKey if key.always_unlocked}
        assert open_keys == {SettingKey.SOUND_ENABLED, SettingKey.VOLUME, SettingKey.LANGUAGE}


class TestSettingsController:
    def test_a_click_changes_the_draft_and_clicks(self, setup):
        before = setup.controller.value(SettingKey.WORK_MINUTES)
        setup.controller.click(setup.row(SettingKey.WORK_MINUTES), 1)
        assert setup.controller.value(SettingKey.WORK_MINUTES) == before + 5
        assert SoundEffect.CLICK in setup.feedback.sounds

    def test_nothing_is_in_force_until_it_is_saved(self, setup):
        setup.controller.click(setup.row(SettingKey.WORK_MINUTES), 1)
        assert setup.active.current.timer.work_minutes == 25
        setup.controller.save()
        assert setup.active.current.timer.work_minutes == 30
        assert setup.store.load().timer.work_minutes == 30
        assert setup.navigation.opened[-1] is PageId.MAIN and setup.judge.refreshed == 1

    def test_during_a_combat_the_timers_are_locked(self, setup):
        setup.work()
        before = setup.controller.value(SettingKey.WORK_MINUTES)
        setup.controller.click(setup.row(SettingKey.WORK_MINUTES), 1)
        assert setup.controller.value(SettingKey.WORK_MINUTES) == before
        assert SoundEffect.DENIED in setup.feedback.sounds and setup.speech.said

    def test_during_a_combat_the_volume_still_moves_and_is_previewed(self, setup):
        setup.work()
        before = setup.controller.value(SettingKey.VOLUME)
        setup.controller.click(setup.row(SettingKey.VOLUME), -1)
        assert setup.controller.value(SettingKey.VOLUME) == before - 10
        assert SoundEffect.VICTORY in setup.feedback.sounds and setup.sounds.volume == before - 10

    def test_saving_during_a_combat_drops_the_locked_edits(self, setup):
        setup.controller.click(setup.row(SettingKey.WORK_MINUTES), 1)
        setup.work()
        setup.controller.click(setup.row(SettingKey.VOLUME), -1)
        setup.controller.save()
        assert setup.active.current.timer.work_minutes == 25
        assert setup.active.current.sound.volume == 30

    def test_cancelling_undoes_the_volume_preview(self, setup):
        setup.controller.click(setup.row(SettingKey.VOLUME), 1)
        setup.controller.cancel()
        assert setup.sounds.volume == setup.active.current.sound.volume

    def test_the_camera_cannot_be_enabled_without_a_calibration(self, setup, monkeypatch):
        from tenhut.services.platform import OperationResult
        from tenhut.services.vision import CameraDependencies

        monkeypatch.setattr(CameraDependencies, "check", staticmethod(lambda: OperationResult.success()))
        setup.controller.click(setup.row(SettingKey.CAMERA_ENABLED), 1)
        assert setup.controller.value(SettingKey.CAMERA_ENABLED) is False
        assert setup.calibration.started == 1

    def test_the_camera_cannot_be_enabled_without_its_extras(self, setup, monkeypatch):
        from tenhut.services.platform import OperationResult
        from tenhut.services.vision import CameraDependencies

        monkeypatch.setattr(CameraDependencies, "check", staticmethod(lambda: OperationResult.failure("no extras")))
        setup.controller.click(setup.row(SettingKey.CAMERA_ENABLED), 1)
        assert setup.speech.messages == ["no extras"] and setup.calibration.started == 0

    def test_calibration_is_not_offered_during_a_combat(self, setup):
        setup.work()
        setup.controller.request_calibration()
        assert setup.calibration.started == 0 and setup.speech.said

    def test_the_rows_are_cached_until_the_draft_changes(self, setup):
        first = setup.controller.rows()
        assert setup.controller.rows() is first
        setup.controller.click(setup.row(SettingKey.WORK_MINUTES), 1)
        assert setup.controller.rows() is not first

    def test_the_json_file_is_locked_during_a_combat(self, setup):
        setup.work()
        setup.controller.open_config_file()
        assert not setup.store.path.exists() and setup.speech.said
