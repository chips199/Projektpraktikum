import src.game.gamelogic.game as game
import pytest
import multiprocessing
import src.game.gamelogic.backgroundProcess as process
import pygame
from unittest.mock import MagicMock
import pandas as pd
import datetime


# the method "run" of game will only be tested exploratory since it is the main game loop and therefore subject to
# constant change and countless dependencies and an endless loop

@pytest.fixture(scope="session")
def setup():
    pygame.init()
    conn1, conn2 = multiprocessing.Pipe(duplex=True)
    test_process = multiprocessing.Process(target=process.backgroundProzess, args=("abc", conn2))
    with pytest.raises(Exception) as e:
        game.Game(50, 50, conn1, test_process)
        assert e == Exception('timeout while receiving data from background process')

    return game.Game(50, 50, conn1, test_process, set_data())


def test_print_loading(setup):
    i = 0
    while i < 1.1:
        assert setup.print_loading(i) is None
        i = i + 0.1


def test_update_background_process(setup):
    assert setup.update_background_process() is None


def test_send_to_background_process(setup):
    assert setup.send_to_background_process() is None


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
    assert setup.next_to_solid(player, 0, 1) == 1
    assert setup.next_to_solid(player, 1, 1) == 1
    assert setup.next_to_solid(player, 1, 2) == 2
    assert setup.next_to_solid(player, 1, 3) == 3
    setup.map.solid_df = pd.DataFrame([(2, 2)], columns=["x", "y"])
    assert setup.next_to_solid(player, 0, 1) == 1
    assert setup.next_to_solid(player, 1, 1) == 1
    assert setup.next_to_solid(player, 1, 2) == 2
    assert setup.next_to_solid(player, 1, 3) == 3


# initialize game data loops and only a simple call. Therefore it will not be tested


def set_data():
    data = {
        "id": 1,
        "0": {
            "id": 0,
            "position": [50, 50],
            "connected": False,
            "health": 100,
            "player_frame": [0, False, 1],
            "weapon_data": [0, False, 1, "Fist", 100, None],
            "killed_by": [0, 0, 0, 0, 0],
            "is_blocking": False,
            "shots": []
        },
        "1": {
            "id": 1,
            "position": [100, 100],
            "connected": False,
            "health": 100,
            "player_frame": [0, False, 1],
            "weapon_data": [0, False, 1, "Fist", 100, None],
            "killed_by": [0, 0, 0, 0, 0],
            "is_blocking": False,
            "shots": []
        },
        "2": {
            "id": 2,
            "position": [150, 150],
            "connected": False,
            "health": 100,
            "player_frame": [0, False, 1],
            "weapon_data": [0, False, 1, "Fist", 100, None],
            "killed_by": [0, 0, 0, 0, 0],
            "is_blocking": False,
            "shots": []
        },
        "3": {
            "id": 3,
            "position": [200, 200],
            "connected": False,
            "health": 100,
            "player_frame": [0, False, 1],
            "weapon_data": [0, False, 1, "Fist", 100, None],
            "killed_by": [0, 0, 0, 0, 0],
            "is_blocking": False,
            "shots": []
        },
        "metadata": {
            "start": (datetime.datetime.now() + datetime.timedelta(seconds=12)).strftime("%d/%m/%Y, %H:%M:%S"),
            "end": (datetime.datetime.now() + datetime.timedelta(seconds=312)).strftime("%d/%m/%Y, %H:%M:%S"),
            "map": "basicmap",
            "spawnpoints": {
                "0": [0, 0],
                "1": [0, 0],
                "2": [0, 0],
                "3": [0, 0],
                "velocity": [7, 7, 20, 0],
                "items": {
                    "Sword": [],
                    "Laser": []
                }
            },
            "scoreboard": {
                "0": [0, 0],
                "1": [0, 0],
                "2": [0, 0],
                "3": [0, 0]
            }
        }
    }
    return data
