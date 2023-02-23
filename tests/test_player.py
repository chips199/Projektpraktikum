import src.game.gamelogic.player as player
import pytest


@pytest.fixtue
def setup():
    return player.Player()

