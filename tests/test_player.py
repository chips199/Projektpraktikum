import pytest
import src.game.gamelogic.player as player
from unittest.mock import MagicMock
import math
import src.game.gamelogic.canvas as canvas
import pandas as pd


@pytest.fixture
def p_setup():
    basicmap = str(wrk_dir)
    player.Player(1, 1, [0, 0], basicmap + r"/player/animation")
    player.Player(1, 2, [0, 0], basicmap + r"/player/animation")
    player.Player(1, 3, [0, 0], basicmap + r"/player/animation")
    player.Player(1, 4, [0, 0], basicmap + r"/player/animation")
    test_player = player.Playerplayer.Player(1, [0, 0], directory=basicmap + r"/player/animation")
    test_player.solid_df = pd.DataFrame([(1, 2), (3, 4), (4, 5)], columns=['x', 'y'])
    return test_player


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
    p_setup.set_velocity((-2, -3, -5. - 7))
    assert p_setup.moving_velocity_on_ground == -2
    assert p_setup.moving_velocity_in_air == -3
    assert p_setup.velocity_jumping == -5
    assert p_setup.velocity_counter == -7
    p_setup.set_velocity(0, 0, 0, 0)
    assert p_setup.moving_velocity_on_ground == 0
    assert p_setup.moving_velocity_in_air == 0
    assert p_setup.velocity_jumping == 0
    assert p_setup.velocity_counter == 0


def test_keep_sliding(p_setup):
    p_setup.sliding_frame_counter = 2
    p_setup.landed = True
    p_setup.moving_on_edge = True
    p_setup.is_falling = False
    p_setup.sliding_frame_counter = 1
    test_fun = MagicMock()
    p_setup.animation_direction = 1
    p_setup.keep_sliding(test_fun)
    test_fun.assert_called_with((p_setup, 1, int(p_setup.current_moving_velocity)) *
                                math.sqrt(p_setup.sliding_frame_counter / p_setup.max_sliding_frames))
    p_setup.animation_direction = 0
    p_setup.keep_sliding(test_fun)
    test_fun.assert_called_with((p_setup, 0, int(p_setup.current_moving_velocity)) *
                                math.sqrt(p_setup.sliding_frame_counter / p_setup.max_sliding_frames))
    assert p_setup.sliding_frame_counter == 0


def test_reset_sliding_counter(p_setup):
    assert p_setup.reset_sliding_counter() is None
    assert p_setup.sliding_frame_counter == p_setup.max_sliding_frames


def test_stop_sliding(p_setup):
    p_setup.sliding_frame_counter = 12
    p_setup.stop_sliding()
    assert p_setup.sliding_frame_counter == 1


def test_draw(p_setup):
    c = canvas.Canvas()
    p_setup.health = 0
    assert p_setup.draw(c) is None
    p_setup.health = -1
    assert p_setup.draw(c) is None
    p_setup.health = 100
    assert p_setup.draw(c) is None


def test_shift_df(p_setup):
    p_setup.shift_df(p_setup.solid_df, 0, 1)
    assert p_setup.solid_df["x"] == 3
    p_setup.shift_df(p_setup.solid_df, 0, -1)
    assert p_setup.solid_df["x"] == 1
    p_setup.shift_df(p_setup.solid_df, 0, 1)
    p_setup.shift_df(p_setup.solid_df, 1, 1)
    assert p_setup.solid_df["x"] == 1
    p_setup.shift_df(p_setup.solid_df, 1, -1)
    assert p_setup.solid_df["x"] == 3
    p_setup.shift_df(p_setup.solid_df, 2, 1)
    assert p_setup.solid_df["y"] == 4
    p_setup.shift_df(p_setup.solid_df, 2, -1)
    assert p_setup.solid_df["y"] == 2
    p_setup.shift_df(p_setup.solid_df, 3, -1)
    assert p_setup.solid_df["y"] == 6
    p_setup.shift_df(p_setup.solid_df, 3, 1)
    assert p_setup.solid_df["y"] == 4


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
    assert p_setup.y == 1
    p_setup.move(3, 1)
    assert p_setup.y == 0
