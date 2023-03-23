import pytest
import src.game.gamelogic.player as player
from unittest.mock import MagicMock, Mock
import src.game.gamelogic.canvas as canvas
import pandas as pd
import os
import pygame


@pytest.fixture
def p_setup():
    pygame.init()
    pygame.display.set_mode((50, 50))
    basicmap = os.path.join((os.path.abspath(os.path.dirname(__file__))), "mock_resources", "basicmap")
    test_player = player.Player(1, [0, 0], directory=os.path.join(basicmap, "player", "animation", "basic_player_magenta_animation"))
    test_player.solid_df = pd.DataFrame([(1, 2), (3, 4), (4, 5)], columns=['x', 'y'])
    test_player.relative_solid_df = pd.DataFrame([(1, 1)], columns=["x", "y"])
    return test_player


@pytest.fixture
def setup():
    pygame.init()
    pygame.display.set_mode((50, 50))
    basicmap = os.path.join((os.path.abspath(os.path.dirname(__file__))), "mock_resources", "basicmap")
    t1 = player.Player(1, [0, 0], os.path.join(basicmap, "player", "animation", "basic_player_magenta_animation"))
    t2 = player.Player(2, [0, 0], os.path.join(basicmap, "player", "animation", "basic_player_magenta_animation"))
    t3 = player.Player(3, [0, 0], os.path.join(basicmap, "player", "animation", "basic_player_magenta_animation"))
    t4 = player.Player(4, [0, 0], os.path.join(basicmap, "player", "animation", "basic_player_magenta_animation"))
    return t1, t2, t3, t4


def test_velocity(p_setup):
    p_setup.set_velocity()
    assert p_setup.moving_velocity_on_ground == 1
    assert p_setup.moving_velocity_in_air == 1
    assert p_setup.velocity_jumping == 0
    assert p_setup.velocity_counter == 0
    p_setup.set_velocity((3, 5, 7, 2))
    assert p_setup.moving_velocity_on_ground == 3
    assert p_setup.moving_velocity_in_air == 5
    assert p_setup.velocity_jumping == 7
    assert p_setup.velocity_counter == 2
    p_setup.set_velocity((-2, -3, -5, - 7))
    assert p_setup.moving_velocity_on_ground == -2
    assert p_setup.moving_velocity_in_air == -3
    assert p_setup.velocity_jumping == -5
    assert p_setup.velocity_counter == -7
    p_setup.set_velocity((0, 0, 0, 0))
    assert p_setup.moving_velocity_on_ground == 0
    assert p_setup.moving_velocity_in_air == 0
    assert p_setup.velocity_jumping == 0
    assert p_setup.velocity_counter == 0


def test_keep_sliding(p_setup):
    p_setup.landed = True
    p_setup.moving_on_edge = True
    p_setup.is_falling = False
    p_setup.sliding_frame_counter = 1
    test_fun = MagicMock()
    p_setup.animation_direction = 1
    p_setup.max_sliding_frames = 1
    p_setup.keep_sliding(test_fun)
    p_setup.animation_direction = 0
    p_setup.keep_sliding(test_fun)
    assert p_setup.sliding_frame_counter == 1


def test_reset_sliding_counter(p_setup):
    assert p_setup.reset_sliding_counter() is None
    assert p_setup.sliding_frame_counter == p_setup.max_sliding_frames


def test_stop_sliding(p_setup):
    p_setup.sliding_frame_counter = 12
    p_setup.stop_sliding()
    assert p_setup.sliding_frame_counter == 1


def test_draw(p_setup):
    c = canvas.Canvas(50, 50)
    p_setup.health = 0
    assert p_setup.draw(c.get_canvas()) is None
    p_setup.health = -1
    assert p_setup.draw(c.get_canvas()) is None
    p_setup.health = 100
    assert p_setup.draw(c.get_canvas()) is None


# using == instead of "is" to compare boolean values
# reason for this is the failing comparison in this case using is
def test_shift_df(p_setup):
    p_setup.shift_df(p_setup.solid_df, 0, 1)
    assert (p_setup.solid_df["x"] == 3).any() == False
    p_setup.shift_df(p_setup.solid_df, 0, -1)
    assert (p_setup.solid_df["x"] == 1).any() == True
    p_setup.shift_df(p_setup.solid_df, 0, 1)
    p_setup.shift_df(p_setup.solid_df, 1, 1)
    assert (p_setup.solid_df["x"] == 1).any() == True
    p_setup.shift_df(p_setup.solid_df, 1, -1)
    assert (p_setup.solid_df["x"] == 3).any() == False
    p_setup.shift_df(p_setup.solid_df, 2, 1)
    assert (p_setup.solid_df["y"] == 4).any() == True
    p_setup.shift_df(p_setup.solid_df, 2, -1)
    assert (p_setup.solid_df["y"] == 2).any() == True
    p_setup.shift_df(p_setup.solid_df, 3, -1)
    assert (p_setup.solid_df["y"] == 6).any() == False
    p_setup.shift_df(p_setup.solid_df, 3, 1)
    assert (p_setup.solid_df["y"] == 4).any() == True


def test_move(p_setup):
    assert p_setup.move(0) is None
    assert p_setup.move(1) is None
    assert p_setup.move(2) is None
    assert p_setup.move(3) is None
    p_setup.x = 0
    p_setup.y = 0
    p_setup.move(0, 1)
    assert p_setup.x == 1
    p_setup.move(1, 1)
    assert p_setup.x == 0
    p_setup.move(2, 1)
    assert p_setup.y == -1
    p_setup.move(3, 1)
    assert p_setup.y == 0


def test_jump(p_setup):
    next_to_solid = Mock(return_value=2)
    p_setup.is_falling = False
    assert p_setup.jump(next_to_solid) is None
    p_setup.is_falling = True
    assert p_setup.jump(next_to_solid) is None
    next_to_solid = Mock(return_value=-2)
    p_setup.is_falling = False
    assert p_setup.jump(next_to_solid) is None
    p_setup.is_falling = True
    assert p_setup.jump(next_to_solid) is None
    next_to_solid = Mock(return_value=0)
    p_setup.is_falling = False
    assert p_setup.jump(next_to_solid) is None
    p_setup.is_falling = True
    assert p_setup.jump(next_to_solid) is None


def test_start_blocking(p_setup):
    p_setup.is_blocking = False
    p_setup.block_x_axis = False
    p_setup.start_blocking()
    assert p_setup.is_blocking is True
    assert p_setup.block_x_axis is True


def test_stop_blocking(p_setup):
    p_setup.is_blocking = True
    p_setup.block_x_axis = True
    p_setup.stop_blocking()
    assert p_setup.is_blocking is False
    assert p_setup.block_x_axis is False


def test_is_alive(p_setup):
    p_setup.health = 50
    assert p_setup.is_alive() is True
    p_setup.health = 0
    assert p_setup.is_alive() is False
    p_setup.health = -1
    assert p_setup.is_alive() is False


def test_refresh_solids(p_setup):
    p_setup.relativ_solids_df = pd.DataFrame([(1, 1)], columns=["x", "y"])
    p_setup.x = 1
    p_setup.y = 1
    p_setup.refresh_solids()
    assert (p_setup.solid_df["x"] == 2).all()
    assert (p_setup.solid_df["y"] == 2).all()
    p_setup.relativ_solids_df = pd.DataFrame([(2, 2)], columns=["x", "y"])
    p_setup.x = -1
    p_setup.y = -1
    p_setup.refresh_solids()
    assert (p_setup.solid_df["x"] == 1).all()
    assert (p_setup.solid_df["y"] == 1).all()
    p_setup.relativ_solids_df = pd.DataFrame([(1, 1)], columns=["x", "y"])
    p_setup.x = 0
    p_setup.y = 0
    p_setup.refresh_solids()
    assert (p_setup.solid_df["x"] == 1).all()
    assert (p_setup.solid_df["y"] == 1).all()


def test_falling(p_setup):
    next_to_solid = Mock(return_value=10)
    p_setup.is_jumping = False
    assert p_setup.falling(next_to_solid) is None
    p_setup.is_jumping = True
    assert p_setup.falling(next_to_solid) is None
    next_to_solid = Mock(return_value=0)
    p_setup.is_jumping = False
    assert p_setup.falling(next_to_solid) is None
    p_setup.is_jumping = True
    assert p_setup.falling(next_to_solid) is None
    next_to_solid = Mock(return_value=-10)
    p_setup.is_jumping = False
    assert p_setup.falling(next_to_solid) is None
    p_setup.is_jumping = True
    assert p_setup.falling(next_to_solid) is None


def test_get_color(setup):
    test = [setup[0].get_color(setup[0].directory), setup[0].get_color(setup[1].directory), setup[2].get_color(setup[2].directory), setup[3].get_color(setup[3].directory)]
    assert "magenta" in test
    assert len(test) == 4


def test_add_shot(p_setup):
    p_setup.animation_direction = 0

    assert len(p_setup.weapon_shots) == 0
    p_setup.add_shot()
    assert len(p_setup.weapon_shots) == 1

    assert player.Player.get_color_rgb(p_setup) == p_setup.weapon_shots[0].color

    assert p_setup.weapon_shots[0].direction == 1
    p_setup.animation_direction = 1
    p_setup.add_shot()
    assert p_setup.weapon_shots[1].direction == -1

