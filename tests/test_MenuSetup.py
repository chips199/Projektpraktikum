import src.game.menu.MenuSetup as menu
from unittest.mock import MagicMock, patch
import pytest
import multiprocessing
import src.game.gamelogic.game as game


@pytest.fixture
def setup():
    test_menu = menu.MenuSetup()
    test_menu.label_error = MagicMock()
    test_menu.label_error.label_hide_show = MagicMock()
    test_menu.label_game_name = MagicMock()
    test_menu.label_game_name.winfo_y = MagicMock()
    test_menu.label_game_name.winfo_height = MagicMock()
    test_menu.interaction_frame = MagicMock()
    test_menu.interaction_frame.destroy = MagicMock()
    test_menu.back_button = MagicMock()
    test_menu.back_button.place = MagicMock()
    test_menu.back_button.configure = MagicMock()
    test_menu.main_frame = MagicMock()
    test_menu.main_frame.after = MagicMock()
    test_menu.entry_session_id = MagicMock()
    test_menu.entry_session_id.get = MagicMock()
    test_menu.conn1, setup.conn2 = multiprocessing.Pipe(duplex=True)
    return test_menu


def test_load_main_frame(setup):
    assert setup.load_main_frame() is None


def test_load_interaction_frame(setup):
    assert setup.load_interaction_frame() is None


def test_load_choose_map_frame(setup):
    assert setup.load_choose_map_frame() is None
    setup.interaction_frame.destroy.assert_called()
    setup.back_button.place.assert_called()


def test_load_lobby_frame(setup):
    assert setup.load_lobby_frame() is None
    setup.back_button.configure.assert_called_with(text="Leave Lobby")
    setup.label_game_name.winfo_y.assert_called()
    setup.label_game_name.winfo_height.assert_called()


def test_load_player(setup):
    assert setup.load_player(5.0, "basicmap/player/basic_player_magenta.png") is None
    assert setup.load_player(5, "basicmap/player/basic_player_magenta.png") is None
    assert setup.load_player(0, "basicmap/player/basic_player_magenta.png") is None
    assert setup.load_player(-5.0, "basicmap/player/basic_player_magenta.png") is None


# This method loops
# def test_update_player(setup):
#    assert setup.update_player() is None
#   setup.main_frame.after.assert_called_with(1000, lambda: setup.update_player())


# test_start_new_session only calls another already tested method


def test_create_lobby(setup):
    assert setup.create_lobby("Schneemap") is None
    setup.main_frame.after.assert_called_with(300, setup.update_background_process)
    setup.label_error.label_hide_show.assert_called()
    setup.label_game_name.winfo_height.assert_called()
    setup.label_game_name.winfo_y.assert_called()


def test_start_network(setup):
    success_func = MagicMock()
    update_func = MagicMock()
    assert setup.start_network("test", success_func, update_func) is None
    success_func.assert_called()
    update_func.assert_called()
    assert setup.start_network("", success_func, update_func) is None
    success_func.assert_called()
    update_func.assert_called()


def test_start_game(setup):
    with patch('src.game.gamelogic.game.Game') as game_mock:
        assert setup.start_game() is None
        game_mock.assert_called()


# join_lobby only calls start_network, already tested


def test_back_to_start(setup):
    assert setup.back_to_start() is None


def test_if_game_started(setup):
    with patch('src.game.gamelogic.game.Game') as game_mock:
        setup.data["game_started"] = False
        assert setup.check_if_game_started() is None
        setup.data["game_started"] = True
        assert setup.check_if_game_started() is None
        game_mock.assert_called()
