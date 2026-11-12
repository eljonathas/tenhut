import pygame
import pytest

from tenhut.game.painting import Canvas, Rgb
from tenhut.game.scenes import PerspectiveGrid, Side, Viewport

VIEWPORT = Viewport(width=200, height=100, vanishing_x=100, horizon_y=40)


def test_viewport_desk_takes_a_fifth_of_the_height_but_at_least_eighteen_pixels():
    assert Viewport.desk_height_for(180) == 36
    assert Viewport.desk_top_for(180) == 144
    assert Viewport.desk_height_for(60) == 18
    assert VIEWPORT.desk_height == 20 and VIEWPORT.desk_y == 80


def test_viewport_span_is_the_narrower_side_around_the_vanishing_line():
    assert Viewport(200, 100, 70, 40).span == 70
    assert Viewport(200, 100, 150, 40).span == 50


def test_viewport_can_be_refitted_to_another_surface_size():
    fitted = VIEWPORT.fitted_to((300, 150))
    assert fitted.size == (300, 150) and fitted.vanishing_x == 100 and fitted.horizon_y == 40


def test_nearest_depth_lands_on_the_bottom_edge():
    grid = PerspectiveGrid(VIEWPORT)
    assert grid.project(1, 0) == (100, 100)
    assert grid.project(1, -30) == (70, 100)


def test_larger_depth_converges_on_the_vanishing_point():
    grid = PerspectiveGrid(VIEWPORT)
    assert grid.project(2, 40) == (120, 70)
    assert grid.project(1000, 40).x == pytest.approx(100, abs=0.1)
    assert grid.project(1000, 40).y == pytest.approx(40, abs=0.1)


def test_street_facades_sit_half_a_street_width_either_side():
    grid = PerspectiveGrid(VIEWPORT)
    assert grid.half_width == 125
    assert grid.point_at(1, Side.LEFT) == (-25, 100)
    assert grid.point_at(2, Side.RIGHT) == (162.5, 70)


def test_narrow_views_still_get_a_minimum_street_width():
    assert PerspectiveGrid(Viewport(100, 100, 20, 40)).half_width == 60


def test_horizon_drop_lowers_the_far_edge_of_the_ground():
    grid = PerspectiveGrid(VIEWPORT, horizon_drop=2)
    assert grid.horizon_y == 42 and grid.ground_height == 58
    assert grid.project(1, 0).y == 100


def test_depth_points_run_from_far_to_near_and_grow():
    posts = PerspectiveGrid(VIEWPORT).depth_points(Side.LEFT, 80, 5)
    assert len(posts) == 5
    assert [post.scale for post in posts] == sorted(post.scale for post in posts)
    assert posts[-1].scale == 1 and posts[-1].y == 100 and posts[-1].x == 20
    assert posts[0].scale == pytest.approx(1 / 4.6)
    assert all(post.x < 100 for post in posts)


def test_depth_points_mirror_between_the_sides():
    grid = PerspectiveGrid(VIEWPORT)
    left, right = grid.depth_points(Side.LEFT, 60, 4), grid.depth_points(Side.RIGHT, 60, 4)
    assert [100 - post.x for post in left] == pytest.approx([post.x - 100 for post in right])


def test_floor_lines_fan_out_from_the_back_wall_to_the_bottom_edge():
    grid = PerspectiveGrid(VIEWPORT)
    assert grid.floor_ray_end(100, 70) == (100, 100)
    end = grid.floor_ray_end(130, 70)
    assert end.y == 100 and end.x == pytest.approx(100 + 30 * 60 / 30)


def test_ground_is_striped_from_the_horizon_down():
    surface = pygame.Surface(VIEWPORT.size)
    base, stripe = Rgb(10, 20, 30), Rgb(200, 100, 50)
    PerspectiveGrid(VIEWPORT).paint_ground(Canvas(surface), base, stripe)
    colors = {tuple(surface.get_at((5, y)))[:3] for y in range(40, 100)}
    assert colors == {tuple(base), tuple(stripe)}
    assert tuple(surface.get_at((5, 39)))[:3] != tuple(base)
    assert tuple(surface.get_at((5, 40)))[:3] == tuple(base)
