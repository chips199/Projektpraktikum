import src.game.menu.MenuSetup as menu
import pytest


@pytest.fixture
def setup():
    test_menu = menu.MenuSetup()

    return test_menu


def test_load_main_frame(setup):
    assert setup.load_main_frame() is None


def test_load_interaction_frame(setup):
    assert setup.load_interaction_frame() is None


def test_load_choose_map_frame(setup):
    assert setup.load_choose_map_frame() is None


def test_load_lobby_frame(setup):
    assert setup.load_lobby_frame() is None


def test_load_player(setup):
    setup.load_player(5.0, "basicmap/player/basic_player_magenta.png")
    setup.load_player(5, "basicmap/player/basic_player_magenta.png")
    setup.load_player(0, "basicmap/player/basic_player_magenta.png")
    setup.load_player(-5.0, "basicmap/player/basic_player_magenta.png")


def test_update_player(setup):
    assert setup.update_player() is None


def test_start_new_session(setup):
    assert setup.start_new_session() is None


def test_create_lobby(setup):
    assert setup.create_lobby() is None


def test_start_network(setup):
    assert setup.start_network() is None


def test_start_game(setup):
    assert setup.start_game() is None


def test_join_lobby(setup):
    assert setup.join_lobby() is None


def test_back_to_start(setup):
    assert setup.back_to_start() is None


def test_if_game_started(setup):
    assert setup.check_if_game_started() is None
