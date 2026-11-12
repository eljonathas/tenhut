import random

import pygame
import pytest

from tenhut.game.character import (
    Character,
    CharacterPainter,
    CharacterState,
    ExpressionCatalog,
    Mood,
    PoseCatalog,
    PoseName,
)
from tenhut.game.character.anatomy import Anatomy
from tenhut.game.character.sip_cycle import SipCycle
from tenhut.game.geometry import Point

FRAME = 1 / 30


def run(character: Character, seconds: float) -> None:
    for _ in range(round(seconds / FRAME)):
        character.update(FRAME)


def pixels(surface: pygame.Surface) -> bytes:
    return pygame.image.tobytes(surface, "RGBA")


def state_for(mood: Mood, pose: PoseName, **changes) -> CharacterState:
    base = CharacterState(mood, pose, 1.0, 0, Point(0.0, 0.0), False, False, False, False, 0.0)
    return CharacterState(**{**{name: getattr(base, name) for name in base.__slots__}, **changes})


def test_a_new_general_is_neutral_and_hands_behind_his_back():
    general = Character(random.Random(1))
    assert (general.mood, general.pose) == (Mood.NEUTRAL, PoseName.BEHIND)
    assert not general.distracted and not general.alerting and not general.talking


def test_show_changes_only_what_it_is_given():
    general = Character(random.Random(1))
    general.show(Mood.ANGRY)
    general.show(pose=PoseName.POINT)
    assert (general.mood, general.pose) == (Mood.ANGRY, PoseName.POINT)
    general.show(Mood.HAPPY, PoseName.COFFEE)
    assert (general.mood, general.pose) == (Mood.HAPPY, PoseName.COFFEE)


def test_same_seed_gives_the_same_general():
    first, second = Character(random.Random(7)), Character(random.Random(7))
    first.show(Mood.STERN)
    second.show(Mood.STERN)
    for _ in range(300):
        first.update(FRAME)
        second.update(FRAME)
        assert first.state == second.state
    assert pixels(first.render()) == pixels(second.render())


def test_different_seeds_diverge_once_he_starts_looking_around():
    first, second = Character(random.Random(1)), Character(random.Random(2))
    run(first, 8)
    run(second, 8)
    assert first.state != second.state


def test_he_blinks_after_two_seconds_and_opens_his_eyes_again():
    general = Character(random.Random(3))
    run(general, 1.9)
    assert not general.state.blinking
    seen_blink = False
    for _ in range(12):
        general.update(FRAME)
        seen_blink = seen_blink or general.state.blinking
    assert seen_blink
    run(general, 0.5)
    assert not general.state.blinking


def test_distract_turns_the_body_then_he_snaps_back_by_himself():
    general = Character(random.Random(4))
    general.distract(1, 1.0)
    assert general.distracted and general.facing_direction == 1
    run(general, 0.5)
    assert general.facing == pytest.approx(1.0)
    run(general, 1.0)
    assert not general.distracted and general.facing_direction == 0
    run(general, 1.0)
    assert general.facing == pytest.approx(0.0)


def test_snap_when_caught_looking_away_raises_the_alarm_for_less_than_a_second():
    general = Character(random.Random(5))
    general.distract(-1, 5.0)
    general.snap()
    assert general.alerting and not general.distracted and general.squinting
    run(general, 0.9)
    assert not general.alerting


def test_snap_without_alert_or_without_distraction_stays_quiet():
    general = Character(random.Random(5))
    general.snap()
    assert not general.alerting
    general.distract(1, 5.0)
    general.snap(alert=False)
    assert not general.alerting


def test_raise_alert_lasts_eight_tenths_of_a_second():
    general = Character(random.Random(5))
    general.raise_alert()
    run(general, 0.7)
    assert general.alerting
    run(general, 0.2)
    assert not general.alerting


def test_shake_displaces_the_sprite_only_while_it_lasts():
    general = Character(random.Random(6))
    assert general.jitter() == Point(0, 0)
    general.shake(0.2)
    offsets = {general.jitter() for _ in range(200)}
    assert len(offsets) > 1 and all(abs(p.x) <= 1 and abs(p.y) <= 1 for p in offsets)
    run(general, 0.3)
    assert general.jitter() == Point(0, 0)


def test_he_follows_the_pointer_and_goes_back_to_scanning_without_it():
    general = Character(random.Random(8))
    general.follow_pointer(Point(1.0, 0.0))
    run(general, 1.0)
    assert general.state.look.x == pytest.approx(1.0, abs=0.01)
    general.follow_pointer(None)
    run(general, 4.0)
    assert general.state.look.x != pytest.approx(1.0, abs=0.01)


def test_looking_aside_beats_following_the_pointer():
    general = Character(random.Random(8))
    general.follow_pointer(Point(-1.0, 0.0))
    general.distract(1, 5.0)
    run(general, 1.0)
    assert general.state.look.x > 0.9


def test_mouth_flaps_only_while_talking():
    general = Character(random.Random(9))
    run(general, 1.0)
    assert not general.state.mouth_open
    general.talking = True
    opened = set()
    for _ in range(60):
        general.update(FRAME)
        opened.add(general.state.mouth_open)
    assert opened == {True, False}
    general.talking = False
    general.update(FRAME)
    assert not general.state.mouth_open


def test_the_coffee_mug_goes_up_only_in_the_sip_window():
    general = Character(random.Random(10))
    general.show(pose=PoseName.COFFEE)
    run(general, 3.0)
    assert not general.state.sipping
    run(general, 2.0)
    assert general.state.sipping
    run(general, 2.5)
    assert not general.state.sipping


def test_sip_cycle_only_runs_while_holding_the_coffee():
    general = Character(random.Random(10))
    run(general, 5.0)
    assert general.state.sip_phase == 0.0


@pytest.mark.parametrize("mood", list(Mood))
@pytest.mark.parametrize("pose", list(PoseName))
def test_every_mood_and_pose_renders_an_outlined_sprite(mood, pose):
    sprite = CharacterPainter().render(state_for(mood, pose))
    assert sprite.get_size() == Anatomy.CANVAS_SIZE
    assert pygame.mask.from_surface(sprite).count() > 1000


@pytest.mark.parametrize("pose", list(PoseName))
def test_every_pose_renders_turned_blinking_and_talking(pose):
    painter = CharacterPainter()
    for turn in (-4, -2, 0, 2, 4):
        state = state_for(Mood.ANGRY, pose, turn=turn, blinking=True, talking=True, mouth_open=True, sip_phase=5.0)
        assert painter.render(state).get_size() == Anatomy.CANVAS_SIZE


def test_moods_look_different_from_one_another():
    painter = CharacterPainter()
    images = {mood: pixels(painter.render(state_for(mood, PoseName.BEHIND, elapsed=4.0))) for mood in Mood}
    assert len(set(images.values())) == len(Mood)


def test_poses_look_different_from_one_another():
    painter = CharacterPainter()
    images = {pose: pixels(painter.render(state_for(Mood.STERN, pose, sip_phase=5.0))) for pose in PoseName}
    assert len(set(images.values())) == len(PoseName)


def test_angry_general_does_not_breathe():
    painter = CharacterPainter()
    exhaling = {"elapsed": 0.65}
    inhaling = {"elapsed": 0.0}
    assert pixels(painter.render(state_for(Mood.ANGRY, PoseName.BEHIND, **exhaling))) == pixels(
        painter.render(state_for(Mood.ANGRY, PoseName.BEHIND, **inhaling))
    )
    assert pixels(painter.render(state_for(Mood.STERN, PoseName.BEHIND, **exhaling))) != pixels(
        painter.render(state_for(Mood.STERN, PoseName.BEHIND, **inhaling))
    )


def test_catalogs_cover_every_enum_member():
    expressions, poses = ExpressionCatalog.standard(), PoseCatalog.standard()
    assert all(expressions.for_mood(mood).mood is mood for mood in Mood)
    assert all(poses.for_name(name).name is name for name in PoseName)


def test_incomplete_catalogs_are_rejected():
    with pytest.raises(ValueError):
        PoseCatalog([])
    with pytest.raises(ValueError):
        ExpressionCatalog([])


def test_state_is_immutable_and_read_only_properties_cannot_be_assigned():
    general = Character(random.Random(1))
    for name in ("mood", "pose", "elapsed", "facing", "distracted", "alerting"):
        with pytest.raises(AttributeError):
            setattr(general, name, 1)
    with pytest.raises(AttributeError):
        general.state.mood = Mood.HAPPY


def test_freeze_parks_the_general_for_a_portrait():
    general = Character(random.Random(1))
    general.freeze(elapsed=1.4, look=Point(0.0, 0.15))
    run_state = general.state
    assert run_state.elapsed == 1.4 and run_state.look == Point(0.0, 0.15) and not run_state.blinking
    assert SipCycle.is_sipping_at(5.0) and not SipCycle.is_sipping_at(6.0)
