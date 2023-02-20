import src.game.gamelogic.background_music as music
import pytest
import os


@pytest.fixture
def setup():
    wrk_dir = wrk_dir = os.path.abspath(os.path.dirname(__file__))
    basicmap = "\\".join(str(wrk_dir).split("\\")[:-1]) + r"\src\game\basicmap\music\Corinna-Basic_Map_Music.mp3"
    test = music.Music(basicmap, 1)
    music.Music(basicmap, -1)
    music.Music(basicmap, 0)
    return test


def test_play(setup):
    assert setup.play() is None


def test_stop(setup):
    assert setup.stop() is None


def test_fadeout(setup):
    assert setup.fadeout(12) is None
    assert setup.fadeout(-12) is None
    assert setup.fadeout(0) is None
