import pandas as pd
import src.game.gamelogic.animated as animated
import pytest
import os
import src.game.gamelogic.canvas as canvas
import pygame


@pytest.fixture(scope="session")
def setup():
    pygame.init()
    pygame.display.set_mode((50, 50))
    wrk_dir = os.path.abspath(os.path.dirname(__file__))
    basicmap = os.path.join(wrk_dir, "mock_resources", "basicmap")
    return animated.Animated([0, 0], os.path.join(basicmap, "player", "blood_animation"))


@pytest.fixture(scope="session")
def setup_canvas():
    return canvas.Canvas(50, 50)


def test_set_pos(setup):
    setup.set_pos(1, 2)
    assert setup.x == 1
    assert setup.y == 2
    setup.set_pos(-1, 2)
    assert setup.x == -1
    assert setup.y == 2
    setup.set_pos(1, -2)
    assert setup.x == 1
    assert setup.y == -2
    setup.set_pos(-1, -2)
    assert setup.x == -1
    assert setup.y == -2


def test_draw(setup, setup_canvas):
    assert setup.draw(g=setup_canvas.get_canvas()) is None


def test_cut_frames(setup):
    length = len(setup.images_right) - 1
    setup.cut_frames(2)
    if length % 2 == 0:
        length = length / 2
    else:
        length = (length - 1) / 2
    assert len(setup.images_right) - 1 == length


def test_double_frames(setup):
    length = len(setup.images_right)
    setup.double_frames(1)
    assert len(setup.images_right) - 1 == length * 2 - 1


# animate function is tested by test_draw


def test_draw_animation_once(setup, setup_canvas):
    assert setup.draw_animation_once(setup_canvas.get_canvas()) is None


def test_stop_animation(setup):
    setup.animation_running = True
    setup.stop_animation()
    assert setup.animation_running is False


def test_start_animation(setup):
    dir = 0
    while dir < 4:
        setup.animation_running = False
        setup.start_animation_in_direction(dir)
        assert setup.animation_running is True
        assert setup.animation_direction == dir
        dir = dir + 1


def test_load_images(setup):
    res = setup.load_images()
    for i in res:
        assert isinstance(i, list)


def test_load_dfs(setup):
    res = setup.load_dfs()
    for i in res:
        assert isinstance(i, list)
        for item in i:
            assert isinstance(item, pd.DataFrame)


def test_animate(setup, setup_canvas):
    setup.animation_direction = 0
    assert setup.animate(setup_canvas.get_canvas(), setup.load_images()[0]) is None
    setup.animation_direction = 1
    assert setup.animate(setup_canvas.get_canvas(), setup.load_images()[0]) is None
