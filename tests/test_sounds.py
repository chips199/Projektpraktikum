import src.game.gamelogic.sounds as sound
import pytest
import os
import pygame


@pytest.fixture
def setup():
    pygame.init()
    wrk_dir = os.path.abspath(os.path.dirname(__file__))
    basicsound = os.path.join(wrk_dir, "mock_resources", "basicmap", "music", "Corinna-Basic_Map_Music.mp3")
    test = sound.Sounds(basicsound, 1)
    sound.Sounds(basicsound, 0)
    sound.Sounds(basicsound, -1)
    return test


def test_play(setup):
    assert setup.play() is None
