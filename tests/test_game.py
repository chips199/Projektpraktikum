import src.game.gamelogic.game as game
import pytest
import multiprocessing
import src.game.gamelogic.backgroundProzess as process
import pygame
from unittest.mock import MagicMock, Mock
import pandas as pd


# the method "run" of game will only be tested exploratory since it is the main game loop and therefore subject to
# constant change and countless dependencies and an endless loop

@pytest.fixture
def setup():
    pygame.init()
    conn1, conn2 = multiprocessing.Pipe(duplex=True)
    test_process = multiprocessing.Process(target=process.backgroundProzess, args=("abc", conn2))
    test_process.start()
    return game.Game(50, 50, conn1, test_process)


def test_print_loading(setup):
    assert setup.print_loading() is None


def test_update_background_process(setup):
    assert setup.update_background_process() is None


def test_send_to_background_process(setup):
    assert setup.send_to_background_process() is None


def test_update_fps(setup):
    assert isinstance(setup.update_fps(), str)


def test_parse(setup):
    res = setup.parse()
    assert isinstance(res, tuple)
    for key in res:
        assert isinstance(key, list)
    assert len(res) == 8


def test_next_to_solid(setup):
    # this method also tests next_to_solid_df by call
    player = MagicMock()
    player.solid_df = pd.DataFrame([(2, 2)], columns=["x", "y"])
    setup.map.solid_df = pd.DataFrame([(5, 3)], columns=["x", "y"])
    assert setup.next_to_solid(player, 0, 1) is False
    assert setup.next_to_solid(player, 1, 1) is False
    assert setup.next_to_solid(player, 1, 2) is False
    assert setup.next_to_solid(player, 1, 3) is False
    setup.map.solid_df = pd.DataFrame([(2, 2)], columns=["x", "y"])
    assert setup.next_to_solid(player, 0, 1) is True
    assert setup.next_to_solid(player, 1, 1) is True
    assert setup.next_to_solid(player, 1, 2) is True
    assert setup.next_to_solid(player, 1, 3) is True


# initialize game data loops and only a simple call. Therefore it will not be tested
