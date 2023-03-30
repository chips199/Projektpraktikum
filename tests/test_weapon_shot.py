import pandas as pd
import pytest
from unittest.mock import MagicMock, Mock
import src.game.gamelogic.weapon_shot as shot
import src.game.gamelogic.canvas as canvas
import pygame


@pytest.fixture(scope="session")
def setup_right():
    # Initiate test subject and initiate module

    pygame.init()
    return shot.WeaponShot((12, 45), 2, (231, 24, 55), 1, 10, 12)


@pytest.fixture(scope="session")
def setup_left():
    # Initiate test subject and initiate module

    pygame.init()
    return shot.WeaponShot((12, 45), 2, (231, 24, 55), -1, 10, 12)


def test_get_dataframe(setup_left, setup_right):
    # test if function returns a dataframe

    assert isinstance(setup_left.get_dataframe(), pd.DataFrame)
    assert isinstance(setup_right.get_dataframe(), pd.DataFrame)


def test_move(setup_left, setup_right):
    # test that method move runs without error

    game = MagicMock()
    game.next_to_solid = Mock(return_value=10)
    assert setup_left.move(game, 34) is None
    assert setup_right.move(game, -56) is None


def test_draw(setup_left, setup_right):
    # test that draw method runs without error

    test_canvas = canvas.Canvas(50, 50)
    assert setup_left.draw(test_canvas.get_canvas()) is None
    assert setup_right.draw(test_canvas.get_canvas()) is None


def test_is_active(setup_right, setup_left):
    # setup test parameters

    setup_right.active = True
    setup_left.active = True

    # test for return value

    assert setup_right.is_active() is True
    assert setup_left.is_active() is True

    # setup test parameters

    setup_right.direction = 0
    setup_left.active = False

    # test for return value

    assert setup_right.is_active() is False
    assert setup_left.is_active() is False


def test_get_sync_data(setup_right, setup_left):
    # test if list of length six is returned

    assert isinstance(setup_right.get_sync_data(), list)
    assert isinstance(setup_left.get_sync_data(), list)
    assert len(setup_right.get_sync_data()) == 6
    assert len(setup_left.get_sync_data()) == 6
