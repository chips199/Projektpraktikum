import pytest
import src.game.gamelogic.network as network
import pygame


@pytest.fixture
def setup():
    pygame.init()
    con1 = network.Network("schneemap")
    con2 = network.Network("basicmap")
    con3 = network.Network("platformmap")
    return con1, con2, con3


# connect_lobby is tested in setup, because the function is only called in constructor of the Network class
def test_connections(setup):
    # only to execute when the server is empty. If the server is in usage the test will fail!
    assert setup[0].id != "5"
    assert setup[1].id != "5"
    assert setup[2].id != "5"
    for i in range(0, 3):
        network.Network(setup[0].session_id)
    test = network.Network(setup[0].session_id)
    assert test.session_id == " Session is full"
    for i in range(0, 3):
        network.Network(setup[1].session_id)
    test = network.Network(setup[1].session_id)
    assert test.session_id == " Session is full"
    for i in range(0, 3):
        network.Network(setup[2].session_id)
    test = network.Network(setup[2].session_id)
    assert test.session_id == " Session is full"

    
def test_lobby_check(setup):
    assert setup[0].check_lobby() == "4"


def test_send(setup):
    assert setup[0].send("ready") is not None


def test_start_game(setup):
    assert setup[0].start_game() == 'schneemap'


def test_get_max_players(setup):
    assert setup[0].get_max_number_of_players() == setup[0].send("get max players")


def test_get_map(setup):
    assert setup[0].get_map() == setup[0].send("get Mapname")


def test_game_started(setup):
    assert setup[0].game_started() is False
    # game start cannot be mocked without huge unnecessary effort. Tested exploratively

