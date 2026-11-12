from fakes import FakeClock
from tenhut.core import Phase, Session, SessionEvent, SessionStore


def make(tasks=("a", "b")):
    session = Session(FakeClock())
    for text in tasks:
        session.add_task(text)
    return session


def test_start_enters_work_with_configured_length(cfg):
    s = make()
    s.start_mission(cfg, now=1000.0)
    assert s.phase is Phase.WORK
    assert s.phase_end - s.phase_start == cfg.timer.work_minutes * 60


def test_work_ends_in_short_break_and_counts_a_cycle(cfg):
    s = make()
    s.start_mission(cfg, now=0.0)
    assert s.tick(cfg, now=1.0) == []
    assert s.tick(cfg, now=s.phase_end + 1) == [SessionEvent.WORK_END]
    assert s.phase is Phase.SHORT and s.cycles == 1


def test_every_nth_break_is_long(cfg):
    s = make()
    s.start_mission(cfg, now=0.0)
    n = cfg.timer.cycles_before_long_break
    for i in range(n):
        assert s.tick(cfg, now=s.phase_end + 1) == [SessionEvent.WORK_END]
        assert s.phase is (Phase.LONG if i == n - 1 else Phase.SHORT)
        assert s.tick(cfg, now=s.phase_end + 1) == [SessionEvent.BREAK_END]
        assert s.phase is Phase.WORK


def test_finishing_all_tasks_is_victory(cfg):
    s = make(("only",))
    s.start_mission(cfg, now=0.0)
    s.toggle_task(0)
    assert s.tick(cfg, now=1.0) == [SessionEvent.VICTORY]
    assert s.phase is Phase.VICTORY


def test_penalty_only_extends_work(cfg):
    s = make()
    s.start_mission(cfg, now=0.0)
    end = s.phase_end
    s.penalize(2)
    assert s.phase_end == end + 120
    s.tick(cfg, now=s.phase_end + 1)
    end = s.phase_end
    s.penalize(2)
    assert s.phase_end == end


def test_skip_break_returns_to_work(cfg):
    s = make()
    s.start_mission(cfg, now=0.0)
    s.tick(cfg, now=s.phase_end + 1)
    s.skip_break(cfg, now=5000.0)
    assert s.phase is Phase.WORK


def test_deserting_keeps_pending_tasks_and_clears_grants(cfg):
    s = make()
    s.start_mission(cfg, now=0.0)
    s.grant("YouTube", 9e9)
    s.end_mission(victory=False)
    assert s.phase is Phase.IDLE and s.active_grants(1.0) == {} and len(s.tasks) == 2


def test_grants_expire_and_keep_the_longest(cfg):
    s = make()
    s.grant("YouTube", 100)
    s.grant("YouTube", 50)
    assert s.active_grants(10) == {"YouTube": 100}
    assert s.active_grants(100) == {}


def test_tasks_are_changed_through_intention_methods():
    s = make()
    assert s.toggle_task(5) is None
    assert s.toggle_task(0).done and s.pending_count() == 1 and s.done_count() == 1
    s.keep_pending_tasks()
    assert [t.text for t in s.tasks] == ["b"]
    s.clear_tasks()
    assert s.tasks == ()


def test_state_round_trips_through_disk(cfg, tmp_path):
    store = SessionStore(tmp_path / "state.json", FakeClock())
    s = store.load()
    s.add_task("a")
    s.add_task("b")
    s.start_mission(cfg, now=123.0)
    s.toggle_task(1)
    s.grant("Reddit", 500.0)
    s.log("entry")
    s.save()
    again = store.load()
    assert again.phase is Phase.WORK and [(t.text, t.done) for t in again.tasks] == [("a", False), ("b", True)]
    assert again.active_grants(1.0) == {"Reddit": 500.0} and again.history == ("entry",)
    assert again.phase_start == 123.0


def test_state_file_keeps_the_documented_fields(cfg, tmp_path):
    import json

    path = tmp_path / "state.json"
    s = SessionStore(path).load()
    s.add_task("x")
    s.save()
    data = json.loads(path.read_text())
    assert data["phase"] == "idle" and data["tasks"] == [{"text": "x", "done": False}]
    assert set(data) == {
        "phase",
        "phase_start",
        "phase_end",
        "cycles",
        "tasks",
        "grants",
        "denied_until",
        "history",
        "infractions",
        "mission_start",
    }


def test_corrupt_state_gives_a_fresh_session(tmp_path):
    path = tmp_path / "state.json"
    path.write_text('{"phase": "bogus"}')
    assert SessionStore(path).load().phase is Phase.IDLE
