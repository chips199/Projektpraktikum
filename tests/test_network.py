import pytest
import src.game.gamelogic.network as network


@pytest.fixture
def setup():
    return network.Network("test")


def test_connect_lobby(setup):
    con1 = setup.connect_lobby("schneemap")
    con2 = setup.connect_lobby("basicmap")
    con3 = setup.connect_lobby("platformmap")
    assert isinstance(con1, str)
    assert isinstance(con2, str)
    assert isinstance(con3, str)
    assert con1 != "5,No connection possible"
    assert con2 != "5,No connection possible"
    assert con3 != "5,No connection possible"
    setup.connect_lobby(con1)
    setup.connect_lobby(con1)
    setup.connect_lobby(con1)
    assert setup.connect_lobby(con1) == "5,No connection possible"
    setup.connect_lobby(con2)
    setup.connect_lobby(con2)
    setup.connect_lobby(con2)
    assert setup.connect_lobby(con2) == "5,No connection possible"
    setup.connect_lobby(con3)
    setup.connect_lobby(con3)
    setup.connect_lobby(con3)
    assert setup.connect_lobby(con3) == "5,No connection possible"


def test_connect(setup):
    assert isinstance(setup.connect(), (int, int))


def test_lobby_check(setup):
    assert setup.check_lobby() is not None


def test_send(setup):
    assert setup.send("ready") is not None


def test_start_game(setup):
    assert setup.start_game() == setup.send("ready")


def test_get_spawnpoint(setup):
    assert setup.getSpawnpoint(1) == [0, 0]
    assert setup.getSpawnpoint(2) == [0, 0]
    assert setup.getSpawnpoint(3) == [0, 0]
    assert setup.getSpawnpoint(4) == [0, 0]


def test_get_max_players(setup):
    assert setup.get_max_number_of_players() == setup.send("get max players")


def test_get_map(setup):
    assert setup.get_map() == setup.send("get Mapname")


def test_game_started(setup):
    assert setup.game_started() is False
    setup.start_game()
    assert setup.game_started() is True
