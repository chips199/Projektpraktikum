import src.game.menu.MyWindow as window
import pytest


@pytest.fixture
def setup():
    return window.MyWindow()


def test_set_size(setup):
    setup.set_size(50, 50)
    assert setup.window_width == 50
    assert setup.window_height == 50


def test_set_sizing(setup):
    setup.set_sizing(50, 50)
    assert setup.sizing_height == 50
    assert setup.sizing_width == 50


def test_on_closing(setup):
    assert setup.on_closing() is None