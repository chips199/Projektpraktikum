import src.game.gamelogic.canvas as canvas
import pytest


@pytest.fixture
def setup():
    return canvas.Canvas(50, 50)


def test_update(setup):
    assert setup.update() is None


def test_get_canvas(setup):
    assert setup.get_canvas == setup.screen


def test_draw_text(setup):
    assert setup.draw_text() is None


def test_draw_background(setup):
    assert setup.draw_background() is None