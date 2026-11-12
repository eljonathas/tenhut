import json

from tenhut.core import Phase, Profile, ProfileStore, RankLadder, Theme


def test_ranks_follow_the_thresholds():
    ladder = RankLadder.standard()
    assert ladder.rank_for(0).name_key == "rank.recruit"
    assert ladder.rank_for(3).name_key == "rank.private"
    assert ladder.rank_for(119).name_key == "rank.colonel"
    assert ladder.next_after(120) is None and ladder.next_after(0).min_xp == 3


def test_add_xp_reports_promotions_and_persists(tmp_path):
    store = ProfileStore(tmp_path / "profile.json")
    profile = store.load()
    assert profile.add_xp(1, pomodoro=True) is False
    assert profile.add_xp(2, mission=True) is True
    again = store.load()
    assert (again.xp, again.pomodoros, again.missions) == (3, 1, 1)
    assert again.rank.name_key == "rank.private"


def test_progress_fraction():
    assert Profile().progress == 0.0
    assert Profile(xp=5).progress == (5 - 3) / (8 - 3)
    assert Profile(xp=500).progress == 1.0


def test_old_profile_file_with_portuguese_field_is_read(tmp_path):
    path = tmp_path / "profile.json"
    path.write_text(json.dumps({"xp": 4, "pomodoros": 2, "missoes": 3}))
    assert ProfileStore(path).load().missions == 3


def test_theme_follows_the_progress_of_the_tasks():
    work = Phase.WORK
    assert Theme.for_progress(0, 4, work, True) is Theme.OFFICE
    assert Theme.for_progress(1, 4, work, True) is Theme.FIELD
    assert Theme.for_progress(2, 4, work, True) is Theme.TRENCH
    assert Theme.for_progress(3, 4, work, True) is Theme.PARADE
    assert Theme.for_progress(0, 0, work, True) is Theme.OFFICE
    assert Theme.for_progress(2, 4, Phase.IDLE, False) is Theme.OFFICE
    assert Theme.for_progress(0, 4, Phase.VICTORY, False) is Theme.PARADE


def test_theme_titles_and_stage_numbers():
    assert Theme.OFFICE.title_key == "theme.office.title" and Theme.PARADE.stage_number == 4
