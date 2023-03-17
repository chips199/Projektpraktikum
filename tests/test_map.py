import pytest
import src.game.gamelogic.map as map
from unittest.mock import MagicMock
import pygame
import os
import src.game.gamelogic.canvas as canvas


@pytest.fixture
def setup():
    game = MagicMock()
    game.width = 50
    game.height = 50
    pygame.display.set_mode((50, 50))
    basicmap = str(os.path.abspath(os.path.dirname(__file__))) + "/basicmap"
    platformmap = str(os.path.abspath(os.path.dirname(__file__))) + "/platformmap"
    schneemap = str(os.path.abspath(os.path.dirname(__file__))) + "/schneemap"
    test_map = map.Map(game, basicmap)
    map.Map(game, platformmap)
    map.Map(game, schneemap)
    return test_map


def test_draw_solids(setup):
    # canvas cannot be mocked easily so the dependency will be tolerated
    test_canvas = canvas.Canvas(50, 50)
    assert setup.draw_solids(test_canvas.get_canvas()) is None


def test_draw_background(setup):
    # canvas cannot be mocked easily so the dependency will be tolerated
    test_canvas = canvas.Canvas(50, 50)
    assert setup.draw_background(test_canvas.get_canvas()) is None


def test_draw_items(setup):
    # canvas cannot be mocked easily so the dependency will be tolerated
    test_canvas = canvas.Canvas(50, 50)
    assert setup.draw_items(test_canvas.get_canvas()) is None


# test only to be run locally
# def test_load_music(setup):
#    assert setup.load_music is None