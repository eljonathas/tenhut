import pygame
import pytest

from tenhut.ui.fonts import FontSet
from tenhut.ui.layout import (
    LayoutFactory,
    LayoutMode,
    LogicalScreen,
    MiniLayout,
    Size,
    TallLayout,
    WideLayout,
    WindowScaler,
)


def layout_for(window):
    size = Size(*window)
    scale = WindowScaler.scale_for(size)
    return LayoutFactory().create(Size(size.width // scale, size.height // scale))


@pytest.mark.parametrize(
    ("window", "mode"),
    [
        ((1120, 720), LayoutMode.WIDE),
        ((1920, 1080), LayoutMode.WIDE),
        ((600, 1000), LayoutMode.TALL),
        ((360, 260), LayoutMode.MINI),
    ],
)
def test_layout_mode_follows_window_shape(window, mode):
    assert layout_for(window).mode is mode


@pytest.mark.parametrize("window", [(1120, 720), (960, 600), (1920, 1080), (1000, 1400), (360, 260), (320, 240)])
def test_layout_pieces_stay_inside_the_window(window):
    layout = layout_for(window)
    screen = (0, 0, layout.size.width, layout.size.height)
    for rect in (layout.board, layout.buttons):
        assert rect.x >= 0 and rect.y >= 0 and rect.right <= screen[2] and rect.bottom <= screen[3]


def test_each_mode_has_its_strategy():
    factory = LayoutFactory()
    assert isinstance(factory.strategy_for(Size(560, 360)), WideLayout)
    assert isinstance(factory.strategy_for(Size(300, 500)), TallLayout)
    assert isinstance(factory.strategy_for(Size(180, 130)), MiniLayout)


def test_wide_layout_puts_the_board_on_the_right_and_the_buttons_under_it():
    layout = LayoutFactory().create(Size(560, 360))
    assert layout.board.right == 560 - WideLayout.BOARD_MARGIN
    assert layout.buttons.x == layout.board.x and layout.buttons.y > layout.board.bottom
    assert layout.board_visible and not layout.compact


def test_tall_layout_stacks_scene_board_and_buttons():
    layout = LayoutFactory().create(Size(300, 500))
    assert layout.scene.bottom <= layout.board.y < layout.board.bottom <= layout.buttons.y


def test_mini_layout_is_compact_and_hides_the_board_by_default():
    layout = LayoutFactory().create(Size(180, 130))
    assert layout.compact and not layout.board_visible


def test_the_general_stands_inside_the_scene():
    layout = LayoutFactory().create(Size(560, 360))
    assert layout.scene.contains(layout.general_rect.clip(layout.scene))
    assert layout.head.y > layout.general_top


def test_scale_is_an_integer_that_grows_with_the_window():
    scales = [WindowScaler.scale_for(Size(w, h)) for w, h in ((560, 360), (1120, 720), (1920, 1080), (2560, 1440))]
    assert scales == sorted(scales) and scales[0] == 1 and scales[-1] >= 4


def test_scaler_centres_the_logical_screen_and_converts_positions():
    scaler = WindowScaler()
    assert scaler.resize(Size(1121, 721))
    assert scaler.scale == 2
    assert scaler.logical_size == Size(560, 360)
    assert tuple(scaler.offset) == (0, 0)
    assert scaler.to_logical((101, 51)) == (50, 25)


def test_scaler_reports_whether_anything_changed():
    scaler = WindowScaler()
    assert scaler.resize(Size(1120, 720))
    assert not scaler.resize(Size(1120, 720))
    assert scaler.resize(Size(1120, 720), force=True)
    assert scaler.resize(Size(600, 1000))


def test_scaler_never_goes_below_the_minimum_window():
    assert WindowScaler().logical_for(Size(100, 100)) == Size(160, 120)


def test_logical_screen_builds_surface_and_layout_on_resize():
    pygame.font.init()
    screen = LogicalScreen(FontSet())
    assert screen.resize(Size(1120, 720))
    assert screen.surface.get_size() == tuple(screen.layout.size)
    assert not screen.resize(Size(1120, 720))
