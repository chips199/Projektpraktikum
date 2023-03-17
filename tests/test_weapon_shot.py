import pandas as pd
import pytest
from unittest.mock import MagicMock, Mock
import src.game.gamelogic.weapon_shot as shot
import src.game.gamelogic.canvas as canvas


@pytest.fixture
def setup_right():
    return shot.WeaponShot((12, 45), 2, (231, 24, 55), 1, 10, 12)


@pytest.fixture
def setup_left():
    return shot.WeaponShot((12, 45), 2, (231, 24, 55), -1, 10, 12)


def test_get_dataframe(setup_left, setup_right):
    assert isinstance(setup_left.get_dataframe(), pd.DataFrame)
    assert isinstance(setup_right.get_dataframe(), pd.DataFrame)


def test_move(setup_left, setup_right):
    game = MagicMock()
    game.next_to_solid = Mock(return_value=10)
    assert setup_left.move(game, 34) is None
    setup_right.move(game, -56) is None


def test_draw(setup_left, setup_right):
    test_canvas = canvas.Canvas(50, 50)
    assert setup_left.draw(test_canvas.get_canvas()) is None
    assert setup_right.draw(test_canvas.get_canvas()) is None
