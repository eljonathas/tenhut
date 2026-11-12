import pytest

from fakes import (
    FakeBackend,
    FakeCelebration,
    FakeClock,
    FakeEnforcement,
    FakeFeedback,
    FakeGestures,
    FakeNavigation,
    FakeRandom,
    FakeRunner,
    FakeSpeech,
    FixedLayouts,
)
from tenhut.controllers import (
    AccessOutcome,
    ActiveSettings,
    BlockingStatus,
    CareerController,
    ChatterController,
    DesertionOutcome,
    DistractionTracker,
    JudgeController,
    JudgeSlot,
    MissionController,
    PageId,
    PomodoroController,
    Reaction,
    RequestForm,
    SpeechController,
    Utterance,
)
from tenhut.core import Phase, Profile, RequestLog, Session, Settings
from tenhut.game.audio import SoundEffect
from tenhut.game.character import Character, Mood, PoseName
from tenhut.services.blocking import Blocker
from tenhut.services.judge import JudgeBackend, JudgeFactory, RequestKind, Verdict
from tenhut.services.platform import OperatingSystem


class World:
    """A mission controller wired to fakes, with the pieces a test wants to look at."""

    def __init__(self, tmp_path=None):
        self.clock = FakeClock(10_000.0)
        self.session = Session(self.clock)
        self.settings = ActiveSettings(Settings())
        self.navigation = FakeNavigation()
        self.speech = FakeSpeech()
        self.feedback = FakeFeedback()
        self.enforcement = FakeEnforcement()
        self.celebration = FakeCelebration()
        self.gestures = FakeGestures()
        self.profile = Profile()
        self.blocker = Blocker(FakeBackend(), self.clock)
        self.career = CareerController(self.profile, self.feedback, self.speech, celebration=self.celebration)
        self.mission = MissionController(
            session=self.session,
            settings=self.settings,
            clock=self.clock,
            navigation=self.navigation,
            speech=self.speech,
            feedback=self.feedback,
            blocking=BlockingStatus(self.blocker, OperatingSystem.LINUX),
            enforcement=self.enforcement,
            career=self.career,
            celebration=self.celebration,
            layouts=FixedLayouts(),
        )


@pytest.fixture
def world():
    return World()


class TestMissionController:
    def test_an_empty_task_only_makes_the_general_ask_for_one(self, world):
        assert not world.mission.add_task("")
        assert world.speech.messages and not world.session.tasks

    def test_adding_a_task_saves_it_and_clicks(self, world):
        assert world.mission.add_task("write tests")
        assert [task.text for task in world.session.tasks] == ["write tests"]
        assert SoundEffect.CLICK in world.feedback.sounds

    def test_starting_needs_tasks(self, world):
        world.mission.start_mission()
        assert world.session.phase is Phase.IDLE

    def test_starting_begins_the_work_block_and_enforces_at_once(self, world):
        world.mission.add_task("a")
        world.mission.start_mission()
        assert world.session.phase is Phase.WORK
        assert world.enforcement.forced == 1
        assert world.navigation.opened[-1] is PageId.MAIN
        assert SoundEffect.START in world.feedback.sounds

    def test_finishing_every_task_is_a_victory_with_xp_and_fireworks(self, world):
        for text in ("a", "b"):
            world.mission.add_task(text)
        world.mission.start_mission()
        world.mission.toggle_task(0)
        assert world.session.phase is Phase.WORK
        world.mission.toggle_task(1)
        assert world.session.phase is Phase.VICTORY
        assert world.profile.xp == MissionController.VICTORY_XP
        assert world.celebration.bursts == [world.mission._layouts.layout.vanishing_x]
        assert world.feedback.stamps and "+2 XP" in world.feedback.popups

    def test_a_task_that_does_not_exist_is_ignored(self, world):
        world.mission.toggle_task(7)
        assert SoundEffect.CLICK not in world.feedback.sounds

    def test_tasks_cannot_be_removed_during_a_mission(self, world):
        world.mission.add_task("a")
        world.mission.start_mission()
        world.mission.remove_task(0)
        assert len(world.session.tasks) == 1

    def test_tasks_can_be_removed_before_the_mission(self, world):
        world.mission.add_task("a")
        world.mission.remove_task(0)
        assert world.session.tasks == ()

    def test_pressing_a_task_before_starting_says_to_start_first(self, world):
        world.mission.add_task("a")
        world.mission.press_task(0)
        assert not world.session.tasks[0].done
        assert world.speech.said

    def test_new_mission_keeps_only_the_pending_tasks(self, world):
        for text in ("done", "todo"):
            world.mission.add_task(text)
        world.session.toggle_task(0)
        world.mission.new_mission()
        assert [task.text for task in world.session.tasks] == ["todo"]
        assert world.navigation.opened[-1] is PageId.MISSION

    def test_a_fresh_mission_asks_twice_before_discarding(self, world):
        world.mission.add_task("keep")
        world.mission.fresh_mission()
        assert world.session.tasks and world.mission.confirming_discard
        world.mission.fresh_mission()
        assert world.session.tasks == () and not world.mission.confirming_discard

    def test_the_confirmation_times_out(self, world):
        world.mission.add_task("keep")
        world.mission.fresh_mission()
        assert not world.mission.expire_confirmation()
        world.clock.current += MissionController.DISCARD_CONFIRMATION_SECONDS + 1
        assert world.mission.expire_confirmation()
        assert not world.mission.confirming_discard

    def test_resuming_keeps_the_ticked_tasks(self, world):
        for text in ("a", "b"):
            world.mission.add_task(text)
        world.mission.start_mission()
        world.mission.toggle_task(0)
        world.session.end_mission(False)
        world.mission.resume_mission()
        assert world.session.phase is Phase.WORK and world.session.tasks[0].done

    def test_skipping_a_break_goes_back_to_work(self, world):
        world.mission.add_task("a")
        world.mission.start_mission()
        world.session.expire_phase(world.clock.now() - 1)
        world.session.tick(world.settings.current, world.clock.now())
        assert world.session.phase is Phase.SHORT
        world.mission.skip_break()
        assert world.session.phase is Phase.WORK


class TestPomodoroController:
    def make(self, world):
        return PomodoroController(
            session=world.session,
            settings=world.settings,
            clock=world.clock,
            mission=world.mission,
            career=world.career,
            navigation=world.navigation,
            speech=world.speech,
            feedback=world.feedback,
        )

    def test_the_end_of_a_work_block_pays_xp_and_starts_the_break(self, world):
        pomodoro = self.make(world)
        world.mission.add_task("a")
        world.mission.start_mission()
        world.session.expire_phase(world.clock.now() - 1)
        pomodoro.tick(0.1)
        assert world.session.phase is Phase.SHORT
        assert world.profile.xp == 1 and world.profile.pomodoros == 1
        assert PageId.MAIN in world.navigation.refreshed

    def test_the_request_page_closes_when_the_break_starts(self, world):
        pomodoro = self.make(world)
        world.mission.add_task("a")
        world.mission.start_mission()
        world.navigation.current = PageId.REQUEST
        world.session.expire_phase(world.clock.now() - 1)
        pomodoro.tick(0.1)
        assert world.navigation.opened[-1] is PageId.MAIN

    def test_the_end_of_a_break_sounds_the_alarm(self, world):
        pomodoro = self.make(world)
        world.mission.add_task("a")
        world.mission.start_mission()
        world.session.expire_phase(world.clock.now() - 1)
        pomodoro.tick(0.1)
        world.session.expire_phase(world.clock.now() - 1)
        pomodoro.tick(0.1)
        assert world.session.phase is Phase.WORK and SoundEffect.ALARM in world.feedback.sounds

    def test_victory_comes_from_the_session_clock_too(self, world):
        pomodoro = self.make(world)
        world.mission.add_task("a")
        world.mission.start_mission()
        world.session.toggle_task(0)
        pomodoro.tick(0.1)
        assert world.session.phase is Phase.VICTORY and world.profile.missions == 1


class FakeJudgeBackend(JudgeBackend):
    """Answers at once with the verdict it was given."""

    name_key = "judge.name.none"
    uses_ai = False

    def __init__(self, settings, verdict):
        super().__init__(settings, clock=FakeClock())
        self.verdict = verdict
        self.asked = []

    def available(self):
        return True

    def ask(self, request):
        self.asked.append(request)
        return self.verdict


class FakeJudgeFactory(JudgeFactory):
    def __init__(self, verdict):
        super().__init__(FakeRunner(), FakeClock())
        self.verdict = verdict
        self.created = []

    def create(self, settings, work_dir=None):
        backend = FakeJudgeBackend(settings, self.verdict)
        self.created.append(backend)
        return backend


class JudgeWorld(World):
    def __init__(self, tmp_path, verdict):
        super().__init__()
        self.slot = JudgeSlot()
        self.factory = FakeJudgeFactory(verdict)
        common = {
            "session": self.session,
            "settings": self.settings,
            "speech": self.speech,
            "feedback": self.feedback,
            "gestures": self.gestures,
        }
        self.judge = JudgeController(
            slot=self.slot,
            factory=self.factory,
            work_dir=tmp_path,
            session=self.session,
            settings=self.settings,
            clock=self.clock,
            log=RequestLog(tmp_path / "requests.jsonl"),
            general=Character(),
            outcomes={RequestKind.ACCESS: AccessOutcome(**common), RequestKind.DESERTION: DesertionOutcome(**common)},
            speech=self.speech,
            feedback=self.feedback,
            navigation=self.navigation,
            enforcement=self.enforcement,
        )
        self.mission.add_task("write the report")
        self.mission.start_mission()

    def finish(self):
        self.slot.job.join(timeout=2)
        self.judge.tick(0.1)


GOOD_REASON = "I need the tutorial to finish the task"


class TestJudgeController:
    def test_an_access_request_without_a_target_is_refused(self, tmp_path):
        world = JudgeWorld(tmp_path, Verdict(True))
        world.judge.submit(RequestForm(RequestKind.ACCESS, "", GOOD_REASON))
        assert not world.slot.active and world.speech.said

    def test_a_short_justification_is_refused_with_a_sound(self, tmp_path):
        world = JudgeWorld(tmp_path, Verdict(True))
        world.judge.submit(RequestForm(RequestKind.ACCESS, "YouTube", "because"))
        assert not world.slot.active and SoundEffect.DENIED in world.feedback.sounds

    def test_an_approved_request_grants_the_groups_and_logs_it(self, tmp_path):
        world = JudgeWorld(tmp_path, Verdict(True, ["YouTube"], 10, "granted"))
        world.judge.submit(RequestForm(RequestKind.ACCESS, "YouTube", GOOD_REASON))
        assert world.slot.active and SoundEffect.THINK in world.feedback.sounds
        world.finish()
        assert not world.slot.active
        assert "YouTube" in world.session.active_grants(world.clock.now())
        assert "granted" in world.speech.messages
        assert (tmp_path / "requests.jsonl").read_text().count("\n") == 1
        assert world.navigation.opened[-1] is PageId.MAIN and world.enforcement.forced >= 2

    def test_a_denied_request_starts_the_cooldown_and_the_slam(self, tmp_path):
        world = JudgeWorld(tmp_path, Verdict(False, speech="no"))
        world.judge.submit(RequestForm(RequestKind.ACCESS, "YouTube", GOOD_REASON))
        world.finish()
        cooldown = world.settings.current.judge.denial_cooldown_seconds
        assert world.session.denied_until == pytest.approx(world.clock.now() + cooldown)
        assert world.gestures.slams == 1 and world.feedback.stamps
        assert world.feedback.flashes == [AccessOutcome.DENIAL_FLASH]

    def test_a_request_cannot_be_opened_during_the_cooldown(self, tmp_path):
        world = JudgeWorld(tmp_path, Verdict(False))
        world.session.deny_until(world.clock.now() + 60)
        world.navigation.opened.clear()
        world.judge.open_request()
        assert world.navigation.opened == [] and SoundEffect.DENIED in world.feedback.sounds

    def test_opening_the_request_page_when_allowed(self, tmp_path):
        world = JudgeWorld(tmp_path, Verdict(False))
        world.judge.open_request()
        assert world.navigation.opened[-1] is PageId.REQUEST

    def test_an_approved_desertion_ends_the_mission_but_keeps_the_tasks(self, tmp_path):
        world = JudgeWorld(tmp_path, Verdict(True, speech="go"))
        world.judge.submit(RequestForm(RequestKind.DESERTION, "", GOOD_REASON))
        world.finish()
        assert world.session.phase is Phase.IDLE and world.session.pending_count() == 1
        assert world.speech.queued

    def test_a_denied_desertion_is_punished_like_any_denial(self, tmp_path):
        world = JudgeWorld(tmp_path, Verdict(False))
        world.judge.submit(RequestForm(RequestKind.DESERTION, "", GOOD_REASON))
        world.finish()
        assert world.session.phase is Phase.WORK and world.gestures.slams == 1

    def test_a_desertion_cannot_be_sent_during_the_cooldown(self, tmp_path):
        world = JudgeWorld(tmp_path, Verdict(True))
        world.session.deny_until(world.clock.now() + 60)
        world.judge.submit(RequestForm(RequestKind.DESERTION, "", GOOD_REASON))
        assert not world.slot.active

    def test_only_one_request_is_judged_at_a_time(self, tmp_path):
        world = JudgeWorld(tmp_path, Verdict(True, ["YouTube"], 5))
        form = RequestForm(RequestKind.ACCESS, "YouTube", GOOD_REASON)
        world.judge.submit(form)
        count = len(world.factory.created)
        world.judge.submit(form)
        assert len(world.factory.created) == count


class SpeechWorld:
    def __init__(self, phase=Phase.IDLE):
        import pygame

        from tenhut.game.audio import SoundBank
        from tenhut.ui.widgets import Balloon

        pygame.init()
        self.clock = FakeClock(10_000.0)
        self.session = Session(self.clock)
        self.session._phase = phase
        self.balloon = Balloon(SoundBank(False))
        self.general = Character(FakeRandom())
        self.slot = JudgeSlot()
        self.tracker = DistractionTracker()
        self.speech = SpeechController(
            self.balloon, self.general, self.session, clock=self.clock, judge=self.slot, distraction=self.tracker
        )


class TestSpeechController:
    def test_saying_something_shows_it_and_sets_the_look(self):
        world = SpeechWorld()
        world.speech.say(Utterance("halt", Reaction.ANGRY_POINT, 3))
        world.balloon.update(0)
        assert world.balloon.text == "halt"
        assert (world.general.mood, world.general.pose) == (Mood.ANGRY, PoseName.POINT)
        assert world.speech.reacting

    def test_the_look_is_held_at_least_as_long_as_the_text_takes_to_read(self):
        world = SpeechWorld()
        world.speech.say(Utterance("x" * 90, Reaction.STERN_POINT, 1))
        world.clock.current += 7
        assert world.speech.reacting
        world.clock.current += 1
        assert not world.speech.reacting

    def test_a_line_without_reaction_leaves_the_look_alone(self):
        world = SpeechWorld()
        world.speech.say(Utterance("hm"))
        assert not world.speech.reacting

    def test_the_ambient_look_follows_the_phase(self):
        for phase, expected in (
            (Phase.WORK, (Mood.STERN, PoseName.CROSSED)),
            (Phase.SHORT, (Mood.HAPPY, PoseName.COFFEE)),
            (Phase.IDLE, (Mood.NEUTRAL, PoseName.BEHIND)),
        ):
            world = SpeechWorld(phase)
            world.speech.tick(0.1)
            assert (world.general.mood, world.general.pose) == expected

    def test_the_victory_pose_alternates(self):
        world = SpeechWorld(Phase.VICTORY)
        poses = set()
        for step in range(4):
            world.clock.current = 10_000.0 + step * SpeechController.VICTORY_POSE_SECONDS
            world.speech.tick(0.1)
            poses.add(world.general.pose)
        assert poses == {PoseName.SALUTE, PoseName.THUMBS}

    def test_a_reaction_in_progress_is_not_overridden(self):
        world = SpeechWorld(Phase.WORK)
        world.speech.say(Utterance("hm", Reaction.HAPPY_THUMBS, 5))
        world.speech.tick(0.1)
        assert world.general.pose is PoseName.THUMBS

    def test_waiting_for_the_judge_keeps_the_thinking_pose(self):
        world = SpeechWorld(Phase.WORK)
        world.general.show(Mood.THINKING, PoseName.CHIN)
        world.slot.occupy(object())
        world.speech.tick(0.1)
        assert world.general.pose is PoseName.CHIN

    def test_keep_and_release_reaction(self):
        world = SpeechWorld()
        world.speech.react_for(1)
        world.speech.keep_reacting(5)
        world.clock.current += 3
        assert world.speech.reacting
        world.speech.release_reaction()
        assert not world.speech.reacting


class TestChatterController:
    def make(self, phase=Phase.WORK):
        world = SpeechWorld(phase)
        navigation = FakeNavigation()
        chatter = ChatterController(
            session=world.session,
            clock=world.clock,
            speech=world.speech,
            navigation=navigation,
            judge=world.slot,
            gestures=FakeGestures(),
            randomness=FakeRandom(),
            balloon=world.balloon,
        )
        return world, chatter, navigation

    def test_he_stays_quiet_until_the_first_delay_is_over(self):
        world, chatter, _ = self.make()
        chatter.tick(0.1)
        assert world.speech.last_said_at == 0.0
        world.clock.current += ChatterController.FIRST_REMARK_DELAY + 1
        chatter.tick(0.1)
        assert world.speech.last_said_at > 0.0

    def test_after_a_remark_he_waits_the_phase_interval(self):
        world, chatter, _ = self.make(Phase.WORK)
        world.clock.current += 10
        chatter.tick(0.1)
        said_at = world.speech.last_said_at
        world.balloon.silence()
        world.clock.current += 119
        chatter.tick(0.1)
        assert world.speech.last_said_at == said_at
        world.clock.current += 2
        chatter.tick(0.1)
        assert world.speech.last_said_at > said_at

    def test_he_does_not_talk_over_himself_or_off_the_main_page(self):
        world, chatter, navigation = self.make()
        world.clock.current += 100
        world.balloon.say("busy")
        world.balloon.update(0)
        chatter.tick(0.1)
        assert world.speech.last_said_at == 0.0
        world.balloon.silence()
        navigation.current = PageId.SETTINGS
        chatter.tick(0.1)
        assert world.speech.last_said_at == 0.0

    def test_a_victory_has_no_remarks_and_the_next_try_is_two_minutes_later(self):
        world, chatter, _ = self.make(Phase.VICTORY)
        world.clock.current += 10
        chatter.tick(0.1)
        assert world.speech.last_said_at == 0.0
        world.clock.current += 119
        chatter.tick(0.1)
        assert world.speech.last_said_at == 0.0


class FakeKiller:
    def __init__(self, closed):
        self.closed = closed
        self.asked = []

    def kill(self, names):
        self.asked.append(names)
        return self.closed


class TestGreeter:
    @pytest.mark.parametrize(
        ("phase", "key"),
        [
            (Phase.WORK, "speech.greeting.resume_work"),
            (Phase.SHORT, "speech.greeting.still_on_break"),
            (Phase.LONG, "speech.greeting.still_on_break"),
            (Phase.VICTORY, "speech.greeting.mission_done"),
            (Phase.IDLE, "speech.greeting.first_time"),
        ],
    )
    def test_the_greeting_follows_the_phase(self, phase, key):
        from tenhut import i18n
        from tenhut.controllers import Greeter

        session, speech = Session(FakeClock()), FakeSpeech()
        session._phase = phase
        Greeter(session, speech).greet()
        assert speech.messages == [i18n.t(key)]

    def test_an_unfinished_mission_is_mentioned(self):
        from tenhut.controllers import Greeter

        session, speech = Session(FakeClock()), FakeSpeech()
        session.add_task("left over")
        Greeter(session, speech).greet()
        assert "1" in speech.messages[0]


class TestBlockingController:
    def make(self, world, closed=()):
        from tenhut.controllers import BlockingController

        self.killer = FakeKiller(list(closed))
        self.backend = world.blocker._backend
        return BlockingController(
            session=world.session,
            settings=world.settings,
            clock=world.clock,
            blocker=world.blocker,
            killer=self.killer,
            speech=world.speech,
            feedback=world.feedback,
            gestures=world.gestures,
        )

    def wait_for_backend(self, expected):
        import time

        for _ in range(100):
            if self.backend.calls and self.backend.calls[-1] == expected:
                return True
            time.sleep(0.01)
        return False

    def test_outside_a_combat_nothing_is_blocked(self, world):
        blocking = self.make(world)
        blocking.enforce(force=True)
        assert world.blocker._desired == []

    def test_during_a_combat_the_blocked_domains_are_applied(self, world):
        blocking = self.make(world)
        world.mission.add_task("a")
        world.mission.start_mission()
        blocking.enforce(force=True)
        assert world.blocker._desired

    def test_a_pass_unblocks_its_group(self, world):
        blocking = self.make(world)
        world.mission.add_task("a")
        world.mission.start_mission()
        blocking.enforce(force=True)
        blocked = len(world.blocker._desired)
        world.session.grant("YouTube", world.clock.now() + 600)
        blocking.enforce(force=True)
        assert len(world.blocker._desired) < blocked

    def test_enforcement_is_throttled_unless_forced(self, world):
        blocking = self.make(world)
        world.mission.add_task("a")
        world.mission.start_mission()
        blocking.enforce(force=True)
        world.session.grant("YouTube", world.clock.now() + 600)
        blocking.enforce()
        assert len(world.blocker._desired) == len(
            world.settings.current.block_list.domains_for(set(world.settings.current.block_list.names))
        )

    def test_closed_apps_make_the_general_react_and_poke(self, world):
        blocking = self.make(world, closed=["steam"])
        world.mission.add_task("a")
        world.mission.start_mission()
        blocking.enforce(force=True)
        assert world.gestures.pokes == [2] and SoundEffect.DENIED in world.feedback.sounds

    def test_an_expired_pass_is_announced_once(self, world):
        blocking = self.make(world)
        world.mission.add_task("a")
        world.mission.start_mission()
        world.session.grant("YouTube", world.clock.now() + 5)
        blocking.enforce(force=True)
        world.clock.current += 10
        blocking.enforce(force=True)
        blocking.enforce(force=True)
        assert world.gestures.pokes.count(1) == 1

    def test_leaving_during_a_mission_blocks_everything_at_once(self, world):
        blocking = self.make(world)
        world.mission.add_task("a")
        world.mission.start_mission()
        blocking.lock_for_exit()
        assert self.backend.calls and self.backend.calls[-1]
