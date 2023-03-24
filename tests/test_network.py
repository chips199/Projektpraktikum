import pytest
import src.game.gamelogic.network as network


@pytest.fixture(scope="session")
def setup():
    con1 = network.Network("schneemap")
    con2 = network.Network("basicmap")
    con3 = network.Network("platformmap")
    assert con1.id != "5"
    assert con2.id != "5"
    assert con3.id != "5"
    for i in range(0, 3):
        network.Network(con1.session_id)
    test = network.Network(con1.session_id)
    assert test.session_id == " Session is full"
    for i in range(0, 3):
        network.Network(con2.session_id)
    test = network.Network(con2.session_id)
    assert test.session_id == " Session is full"
    for i in range(0, 3):
        network.Network(con3.session_id)
    test = network.Network(con3.session_id)
    assert test.session_id == " Session is full"
    return con1


# connect_lobby is tested in setup, because the function is only called in constructor of the Network class


def test_lobby_check():
    con1 = network.Network("schneemap")
    network.Network(con1.session_id)
    network.Network(con1.session_id)
    assert con1.check_lobby() == '3'


def test_send():
    con1 = network.Network("schneemap")
    assert con1.send("ready") is not None


def test_start_game():
    con1 = network.Network("schneemap")
    assert con1.start_game() == 'schneemap'


def test_get_max_players():
    con1 = network.Network("schneemap")
    assert con1.get_max_number_of_players() == con1.send("get max players")


def test_get_map():
    con1 = network.Network("schneemap")
    assert con1.get_map() == con1.send("get Mapname")


def test_game_started():
    con1 = network.Network("schneemap")
    assert con1.game_started() is False
    # game start cannot be mocked without huge unnecessary effort. Tested exploratively

