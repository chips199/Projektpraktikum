import pytest
import src.game.gamelogic.map as map
from unittest.mock import MagicMock
import pygame
import os
import src.game.gamelogic.canvas as canvas


@pytest.fixture(scope="session")
def setup():

    # set up test subject

    pygame.init()
    game = MagicMock()
    game.width = 50
    game.height = 50
    pygame.display.set_mode((50, 50))
    basicmap = os.path.join(os.path.abspath(os.path.dirname(__file__)), "mock_resources", "basicmap")
    platformmap = os.path.join(os.path.abspath(os.path.dirname(__file__)), "mock_resources", "platformmap")
    schneemap = os.path.join(os.path.abspath(os.path.dirname(__file__)), "mock_resources", "schneemap")
    test_map = map.Map(game, basicmap)
    map.Map(game, platformmap)
    map.Map(game, schneemap)
    return test_map


def test_draw_solids(setup):

    # check for error free execution

    test_canvas = canvas.Canvas(50, 50)
    assert setup.draw_solids(test_canvas.get_canvas()) is None


def test_draw_background(setup):

    # check for error free execution

    test_canvas = canvas.Canvas(50, 50)
    assert setup.draw_background(test_canvas.get_canvas()) is None


def test_draw_items(setup):

    # check for error free execution

    test_canvas = canvas.Canvas(50, 50)
    assert setup.draw_items(test_canvas.get_canvas()) is None


def test_load_music(setup):

    # check for error free execution

    assert setup.music_load() is None
