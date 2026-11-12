import random
from collections.abc import Sequence
from typing import TypeVar

import pygame
import pytest

from tenhut.core import Phase, Task, Theme
from tenhut.game.geometry import Point
from tenhut.game.painting import Canvas
from tenhut.game.scenes import (
    Ambience,
    DeskState,
    FieldScene,
    OfficeScene,
    ParadeScene,
    SceneContext,
    SceneRegistry,
    TrenchScene,
    Viewport,
)
from tenhut.game.scenes.ambient_frame import AmbientFrame
from tenhut.game.scenes.birds import Birds
from tenhut.game.scenes.day_sky import DaySky
from tenhut.game.scenes.firework_show import FireworkShow
from tenhut.game.scenes.jet_squadron import JetSquadron
from tenhut.game.scenes.layer_cache import LayerCache
from tenhut.game.scenes.night_sky import NightSky
from tenhut.game.scenes.parade_frame import ParadeFrame
from tenhut.game.scenes.scene_anchors import SceneAnchors
from tenhut.game.scenes.scene_key import SceneKey
from tenhut.game.scenes.scene_layers import SceneLayers
from tenhut.game.scenes.sky_factory import SkyFactory
from tenhut.game.scenes.sky_palette import SkyPalette
from tenhut.game.scenes.smoke_drift import SmokeDrift
from tenhut.game.scenes.starfield import Starfield
from tenhut.game.scenes.sunset_sky import SunsetSky

T = TypeVar("T")
SIZES = [(280, 180, 100, 70), (300, 200, 125, 80), (180, 130, 54, 50)]
FRAME = 1 / 30


class MidpointRandom:
    """Deterministic stand-in for the random stream: always the middle of the range, always the first choice."""

    def random(self) -> float:
        return 0.5

    def uniform(self, low: float, high: float) -> float:
        return (low + high) / 2

    def randint(self, low: int, high: int) -> int:
        return low

    def randrange(self, start: int, stop: int) -> int:
        return start

    def choice(self, options: Sequence[T]) -> T:
        return options[0]


class FixedClock:
    def __init__(self, now: float) -> None:
        self.value = now

    def now(self) -> float:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.value += seconds


def context(phase: Phase = Phase.WORK, size: tuple[int, int, int, int] = SIZES[0]) -> SceneContext:
    width, height, vanishing_x, horizon_y = size
    return SceneContext(phase, Viewport(width, height, vanishing_x, horizon_y))


def draw(scene, ctx: SceneContext, desk: DeskState | None = None) -> tuple[pygame.Surface, pygame.Surface]:
    width, height = ctx.viewport.size
    background = pygame.Surface((width, height))
    foreground = pygame.Surface((width, height), pygame.SRCALPHA)
    scene.draw_background(background, ctx)
    scene.draw_foreground(foreground, ctx, desk or DeskState())
    return background, foreground


def pixels(surface: pygame.Surface) -> bytes:
    return pygame.image.tobytes(surface, "RGBA")


def test_registry_has_a_scene_for_every_theme():
    registry = SceneRegistry(randomness=MidpointRandom())
    scenes = {theme: registry.scene_for(theme) for theme in Theme}
    assert [type(scenes[theme]) for theme in Theme] == [OfficeScene, FieldScene, TrenchScene, ParadeScene]
    assert all(scene.theme is theme for theme, scene in scenes.items())


@pytest.mark.parametrize("theme", list(Theme))
@pytest.mark.parametrize("size", SIZES)
def test_every_scene_draws_in_every_phase_at_every_layout(theme, size):
    registry = SceneRegistry(randomness=random.Random(3))
    scene = registry.scene_for(theme)
    for phase in Phase:
        registry.update(FRAME)
        background, foreground = draw(scene, context(phase, size))
        assert len({tuple(background.get_at((size[0] // 2, y))) for y in range(size[1])}) > 3
        assert foreground.get_at((size[0] // 2, size[1] - 2))[3] == 255


def test_static_layers_are_cached_per_view():
    registry = SceneRegistry(randomness=MidpointRandom())
    scene = registry.scene_for(Theme.FIELD)
    assert scene.background_layer(context()) is scene.background_layer(context())
    assert scene.background_layer(context()) is not scene.background_layer(context(Phase.IDLE))
    assert scene.background_layer(context()) is not scene.background_layer(context(size=SIZES[1]))
    assert scene.foreground_layer(context()) is scene.foreground_layer(context())


def test_cache_is_emptied_when_it_grows_past_its_limit():
    cache = LayerCache()
    blank = pygame.Surface((4, 4))
    for width in range(20):
        key = SceneKey(Theme.OFFICE, Phase.WORK, width, 10, 2, 2)
        cache.put(key, SceneLayers(blank, blank, SceneAnchors()))
        assert len(cache) <= LayerCache.MAX_ENTRIES + 2
    assert cache.get(key) is not None
    assert cache.get(SceneKey(Theme.OFFICE, Phase.WORK, 0, 10, 2, 2)) is None


def test_same_seed_gives_identical_animation():
    def play(seed: int) -> bytes:
        registry = SceneRegistry(FixedClock(1_000_000.0), random.Random(seed))
        scene = registry.scene_for(Theme.TRENCH)
        for _ in range(400):
            registry.update(FRAME)
            background, _ = draw(scene, context())
        return pixels(background)

    assert play(1) == play(1)
    assert play(1) != play(2)


def test_construction_consumes_the_original_random_stream():
    rng = random.Random(7)
    SceneRegistry(randomness=rng)
    mirror = random.Random(7)
    for _ in range(7):
        mirror.uniform(0, 600), mirror.uniform(0.05, 0.45), mirror.uniform(2, 5), mirror.choice((1, 2))
    for _ in range(60):
        mirror.random(), mirror.random()
    assert rng.getstate() == mirror.getstate()


def test_tasks_are_redrawn_on_the_clipboard_each_frame():
    registry = SceneRegistry(randomness=MidpointRandom())
    scene = registry.scene_for(Theme.OFFICE)
    ctx = context()
    _, empty = draw(scene, ctx, DeskState())
    _, pending = draw(scene, ctx, DeskState((Task("write"),)))
    _, done = draw(scene, ctx, DeskState((Task("write", done=True),)))
    assert len({pixels(empty), pixels(pending), pixels(done)}) == 3


def test_desk_shake_moves_the_whole_foreground():
    registry = SceneRegistry(randomness=MidpointRandom())
    scene = registry.scene_for(Theme.FIELD)
    ctx = context()
    _, still = draw(scene, ctx, DeskState())
    _, shaken = draw(scene, ctx, DeskState(shake=Point(0, 2)))
    assert pixels(still) != pixels(shaken)


def test_wall_clock_shows_the_injected_time():
    clock = FixedClock(1_800_000_000.0)
    registry = SceneRegistry(clock, MidpointRandom())
    scene = registry.scene_for(Theme.OFFICE)
    first, _ = draw(scene, context())
    clock.value += 3 * 3600 + 20 * 60
    second, _ = draw(scene, context())
    assert pixels(first) != pixels(second)


def test_burst_confetti_falls_and_disappears():
    registry = SceneRegistry(randomness=random.Random(1))
    scene = registry.scene_for(Theme.FIELD)
    ctx = context()
    confetti = registry.ambience.confetti
    registry.burst(100)
    assert len(confetti._pieces) == confetti.PIECES
    for _ in range(40):
        registry.update(FRAME)
    draw(scene, ctx)
    assert 0 < len(confetti._pieces) <= confetti.PIECES
    for _ in range(600):
        registry.update(FRAME)
    assert not confetti._pieces


def test_fireworks_only_launch_when_switched_on():
    registry = SceneRegistry(randomness=random.Random(1))
    assert registry.fireworks is False
    for _ in range(60):
        registry.update(FRAME)
    assert len(registry.ambience.fireworks._sparks) == 0
    registry.fireworks = True
    registry.update(FRAME)
    assert registry.fireworks is True and len(registry.ambience.fireworks._sparks) == FireworkShow.SPARKS_PER_BURST


def test_ambience_remembers_the_size_of_the_last_background_drawn():
    registry = SceneRegistry(randomness=MidpointRandom())
    assert registry.ambience.world == Ambience.DEFAULT_WORLD
    draw(registry.scene_for(Theme.FIELD), context(size=SIZES[2]))
    assert registry.ambience.world == (180, 130)


def frame_at(elapsed: float, world: tuple[int, int] = (280, 180)) -> AmbientFrame:
    return AmbientFrame(elapsed, world[0], world[1], MidpointRandom())


def test_first_flock_appears_after_five_seconds_and_leaves_the_sky():
    birds = Birds()
    birds.fly(FRAME, frame_at(4.9))
    assert not birds._flock
    birds.fly(FRAME, frame_at(5.0))
    assert birds._flock
    for step in range(1200):
        birds.fly(FRAME, frame_at(5.0 + step * FRAME + FRAME))
    assert not birds._flock or birds._next_flock_at > 5


def test_smoke_puffs_rise_and_expire():
    smoke = SmokeDrift()
    smoke.emit_if_due(frame_at(0.0), 70)
    smoke.emit_if_due(frame_at(0.1), 70)
    assert len(smoke._puffs) == 1
    first = smoke._puffs[0]
    smoke.rise(1.0)
    assert first.y == pytest.approx(64) and first.radius == pytest.approx(4.5)
    smoke.rise(20.0)
    assert not smoke._puffs


def test_sparks_fade_after_about_a_second():
    show = FireworkShow()
    show.launching = True
    show.update(FRAME, frame_at(0.0))
    assert show._sparks
    show.launching = False
    for _ in range(60):
        show.update(FRAME, frame_at(1.0))
    assert not show._sparks


def test_jets_wait_three_seconds_for_the_first_launch_then_cross_the_sky():
    squadron = JetSquadron()
    canvas = Canvas(pygame.Surface((280, 180), pygame.SRCALPHA))
    canvas.surface.fill((10, 10, 10, 255))

    def show(elapsed: float) -> None:
        squadron.draw(canvas, ParadeFrame(elapsed, party=False, randomness=MidpointRandom()), None)

    show(0.0)
    show(2.9)
    assert squadron._flight is None
    show(3.1)
    assert squadron._flight is not None and len(squadron._trails) == len(JetSquadron.FORMATION)
    for step in range(400):
        show(3.2 + step * FRAME)
    assert squadron._flight is None


@pytest.mark.parametrize(
    ("phase", "sky_type"),
    [
        (Phase.IDLE, NightSky),
        (Phase.SHORT, SunsetSky),
        (Phase.LONG, SunsetSky),
        (Phase.WORK, DaySky),
        (Phase.VICTORY, DaySky),
    ],
)
def test_sky_follows_the_phase(phase, sky_type):
    factory = SkyFactory(Starfield(MidpointRandom()))
    assert type(factory.create(Theme.FIELD, phase)) is sky_type


def test_sky_colours_per_theme_and_phase():
    factory = SkyFactory(Starfield(MidpointRandom()))
    assert factory.create(Theme.TRENCH, Phase.WORK).colors == SkyPalette.daylight(Theme.TRENCH)
    assert factory.create(Theme.PARADE, Phase.VICTORY).colors == SkyPalette.PARADE_VICTORY
    assert factory.create(Theme.OFFICE, Phase.VICTORY).colors == SkyPalette.daylight(Theme.OFFICE)
    assert factory.create(Theme.PARADE, Phase.IDLE).colors == SkyPalette.NIGHT
    assert factory.create(Theme.FIELD, Phase.SHORT).colors == SkyPalette.SUNSET


def test_sky_gradient_runs_from_the_top_colour_to_the_horizon_colour():
    sky = SkyFactory(Starfield(MidpointRandom())).create(Theme.FIELD, Phase.WORK)
    surface = pygame.Surface((20, 100))
    sky.paint_gradient(Canvas(surface), pygame.Rect(0, 0, 20, 100))
    assert tuple(surface.get_at((0, 0)))[:3] == tuple(sky.colors.top)
    assert tuple(surface.get_at((0, 99)))[:3] == tuple(sky.colors.horizon)
