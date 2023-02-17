import src.game.menu.MenuSetup as menu
import pytest
from xvfbwrapper import Xvfb


@pytest.fixture
def setup():
    test_menu = menu.MenuSetup()

    vdisplay = Xvfb()
    vdisplay.start()
    return test_menu


def test_load_main_frame(setup):
    setup.load_main_frame()


def test_load_interaction_frame(setup):
    setup.load_interaction_frame()


def test_load_choose_map_frame(setup):
    setup.load_choose_map_frame()


def test_load_lobby_frame(setup):
    setup.load_lobby_frame()


def test_load_player(setup):
    setup.load_player(5.0, "mock_filestructure/player/placeholder.png")
    setup.load_player(5, "mock_filestructure/player/placeholder.png")
    setup.load_player(0, "mock_filestructure/player/placeholder.png")
    setup.load_player(-5.0, "mock_filestructure/player/placeholder.png")


def test_update_player(setup):
    setup.update_player()


def test_start_new_session(setup):
    setup.start_new_session()


def test_create_lobby(setup):
    setup.create_lobby()


def test_start_network(setup):
    setup.start_network()


def test_start_game(setup):
    setup.start_game()


def test_join_lobby(setup):
    setup.join_lobby()


def test_back_to_start(setup):
    setup.back_to_start()


def test_if_game_started(setup):
    setup.check_if_game_started()
