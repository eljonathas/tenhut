import pygame
import pytest

from fakes import FakeClock
from tenhut.game.animations import (
    CurtainTransition,
    FloatingTextStack,
    Lettering,
    PokeAnimation,
    PokeTrajectory,
    SlamAnimation,
    SlamPlacement,
    Stamp,
    StampContent,
    StampPlacement,
    TitleCard,
    TitleCardContent,
    TitleCardFonts,
    TitleCardPlacement,
)
from tenhut.game.animations.easing import Easing
from tenhut.game.geometry import Point
from tenhut.game.painting import Palette


@pytest.fixture(scope="module", autouse=True)
def pygame_ready():
    pygame.font.init()
    yield


@pytest.fixture
def font():
    return pygame.font.Font(pygame.font.get_default_font(), 13)


class SequenceRandom:
    def __init__(self, *values):
        self.values = list(values)

    def uniform(self, low, high):
        return self.values.pop(0)

    def randint(self, low, high):
        return self.values.pop(0)


def advance(animation, seconds, step=1 / 30):
    for _ in range(round(seconds / step)):
        animation.update(step)


def test_easing_is_clamped_and_monotonic():
    assert Easing.out_cubic(-1) == 0 and Easing.out_cubic(2) == 1
    assert Easing.out_cubic(0.2) < Easing.out_cubic(0.6) < 1


def test_curtain_finishes_and_uncovers_the_new_scene(font):
    old = pygame.Surface((64, 40))
    old.fill((255, 0, 0))
    curtain = CurtainTransition(old, column_width=8, randomness=SequenceRandom(*[0.0] * 9))
    new = pygame.Surface((64, 40))
    curtain.draw(new)
    assert not curtain.finished and new.get_at((3, 20))[:3] == (255, 0, 0)
    advance(curtain, CurtainTransition.DURATION)
    assert curtain.finished
    new.fill((0, 0, 255))
    curtain.draw(new)
    assert new.get_at((3, 20))[:3] == (0, 0, 255)


def test_curtain_gives_up_when_the_surface_size_changes():
    curtain = CurtainTransition(pygame.Surface((64, 40)), randomness=SequenceRandom(*[0.0] * 9))
    curtain.draw(pygame.Surface((32, 20)))
    assert curtain.finished


def poke(font, jabs):
    trajectory = PokeTrajectory(Point(40, 40), Point(100, 90), 10, 60, 4)
    return PokeAnimation(trajectory, jabs, caption="TOC", font=font)


@pytest.mark.parametrize(("jabs", "duration"), [(1, 1.0), (2, 1.25)])
def test_poke_lasts_as_long_as_its_jabs(font, jabs, duration):
    animation = poke(font, jabs)
    advance(animation, duration - 0.1)
    assert not animation.finished
    advance(animation, 0.2)
    assert animation.finished


def test_poke_reports_each_jab_on_the_frame_it_lands(font):
    animation = poke(font, 2)
    landed = []
    for _ in range(40):
        animation.update(1 / 30)
        landed.append(animation.jabs_landed)
    assert sum(landed) == 2
    assert landed.index(1) == int(0.36 * 30)


def test_poke_draws_the_arm_glove_and_caption(font):
    animation = poke(font, 2)
    surface = pygame.Surface((160, 120))
    surface.fill((50, 50, 50))
    advance(animation, 0.5)
    animation.draw(surface)
    assert pygame.image.tobytes(surface, "RGB") != pygame.image.tobytes(pygame.Surface((160, 120)), "RGB")


def slam(font):
    return SlamAnimation(SlamPlacement(desk_top=120, world_scale=2, character_scale=3, center_x=80), "BAM", font)


def test_slam_hits_once_at_the_impact_time_then_ends(font):
    animation = slam(font)
    impacts = []
    while not animation.finished:
        animation.update(1 / 30)
        impacts.append(animation.impact_landed)
    assert impacts.count(True) == 1
    assert (impacts.index(True) + 1) / 30 >= SlamAnimation.IMPACT_TIME
    assert animation.fists_raised is False


def test_slam_desk_is_still_until_the_impact_and_settles_afterwards(font):
    animation = slam(font)
    advance(animation, 0.2)
    assert animation.fists_raised and animation.shake == Point(0, 0) and animation.hop == 0
    assert animation.since_impact == -1.0
    advance(animation, 0.3)
    assert animation.since_impact > 0
    advance(animation, 0.5)
    assert animation.shake == Point(0, 0) and animation.hop == 0


def test_slam_draws_nothing_before_the_impact(font):
    animation = slam(font)
    surface = pygame.Surface((200, 150))
    before = pygame.image.tobytes(surface, "RGB")
    advance(animation, 0.1)
    animation.draw(surface)
    assert pygame.image.tobytes(surface, "RGB") == before
    advance(animation, 0.35)
    animation.draw(surface)
    assert pygame.image.tobytes(surface, "RGB") != before


def test_title_card_lives_four_seconds_on_the_clock(font):
    clock = FakeClock(100.0)
    scene = pygame.Rect(0, 0, 280, 180)
    card = TitleCard(
        TitleCardContent("STAGE 2", "1 of 4"),
        TitleCardFonts(font, font),
        clock,
        placement=TitleCardPlacement(scene, scene),
    )
    surface = pygame.Surface((280, 180))
    card.draw(surface)
    clock.current += 3.9
    assert not card.finished
    card.draw(surface)
    clock.current += 0.2
    assert card.finished


def test_title_card_drops_in_and_rises_out(font):
    clock = FakeClock(0.0)
    scene = pygame.Rect(0, 0, 280, 180)
    card = TitleCard(
        TitleCardContent("A", "b"), TitleCardFonts(font, font), clock, placement=TitleCardPlacement(scene, scene)
    )
    offsets = []
    for age in (0.0, 0.2, 1.0, 3.75, 4.0):
        clock.current = age
        offsets.append(card.vertical_offset())
    assert offsets[0] == -40 and offsets[2] == 8
    assert offsets[0] < offsets[1] < offsets[2] and offsets[3] < offsets[2] and offsets[4] == -40


def test_stamp_fades_out_and_stays_on_screen(font):
    clock = FakeClock(0.0)
    placement = StampPlacement(120, Point(5, 60))
    stamp = Stamp(StampContent("APPROVED!!", Palette.GOLD), font, clock, placement=placement)
    surface = pygame.Surface((120, 120))
    for age in (0.0, 0.1, 1.0, 1.6):
        clock.current = age
        stamp.draw(surface)
    assert not stamp.finished
    clock.current = 1.81
    assert stamp.finished


def test_floating_text_stacks_drifts_up_and_expires(font):
    stack = FloatingTextStack(font, SequenceRandom(3, -4))
    surface = pygame.Surface((100, 100))
    stack.anchor_at(Point(50, 80))
    stack.pop_up("+1 XP", Palette.GOLD)
    stack.pop_up("+5 min", Palette.RED)
    stack.draw(surface)
    assert not stack.finished
    stack.update(1.0)
    assert not stack.finished
    stack.update(1.3)
    assert stack.finished


def test_lettering_fits_text_with_an_ellipsis(font):
    lettering = Lettering(font)
    assert lettering.fitted("hi", 200) == "hi"
    fitted = lettering.fitted("a very long sentence that cannot fit", 60)
    assert fitted.endswith("…") and lettering.width(fitted) <= 60
