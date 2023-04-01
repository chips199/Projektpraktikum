import src.game.gamelogic.background_music as music
import pytest
import os
import pygame


@pytest.fixture(scope="session")
def setup():

    # set up test subject

    pygame.init()
    wrk_dir = os.path.abspath(os.path.dirname(__file__))
    basicmap = os.path.join(wrk_dir, "mock_resources", "basicmap", "music")
    test = music.Music(basicmap, 1)
    music.Music(basicmap, -1)
    music.Music(basicmap, 0)
    return test


def test_play(setup):

    # test error free execution

    assert setup.play() is None


def test_stop(setup):

    # test error free execution

    assert setup.stop() is None


def test_fadeout(setup):

    # test error free execution

    assert setup.fadeout(12) is None
    assert setup.fadeout(-12) is None
    assert setup.fadeout(0) is None
