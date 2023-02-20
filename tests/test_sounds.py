import src.game.gamelogic.sounds as sound
import pytest


@pytest.fixture
def setup():
    wrk_dir = wrk_dir = os.path.abspath(os.path.dirname(__file__))
    basicsound = "\\".join(str(wrk_dir).split("\\")[:-1]) + r"\src\game\basicmap\music\Corinna-Basic_Map_Music.mp3"
    test = sound.Sounds(basicsound, 1)
    sound.Sounds(basicsound, 0)
    sound.Sounds(basicsound, -1)
    return test


def test_play(setup):
    assert setup.play() is None
