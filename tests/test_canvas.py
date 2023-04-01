import src.game.gamelogic.canvas as canvas
import pytest
import pygame
import os


@pytest.fixture(scope="session")
def setup():

    # set up test canvas

    return canvas.Canvas(50, 50)


def test_update(setup):

    # check for error free execution

    assert setup.update() is None


def test_get_canvas(setup):

    # check for correct return value

    assert setup.get_canvas() == setup.screen


def test_draw_text(setup):

    # check for error free execution

    wrk_dir = os.path.abspath(os.path.dirname(__file__))
    scoreboard = pygame.image.load(os.path.join(wrk_dir, "mock_resources", "Scoreboard.png")).convert_alpha()
    assert setup.draw_text(scoreboard, "Player 3", 20, (64, 224, 208), 40, 165) is None


def test_draw_background(setup):

    # check for error free execution

    assert setup.draw_background("red") is None
