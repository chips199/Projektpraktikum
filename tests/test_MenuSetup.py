import os
import src.game.menu.MenuSetup as menu
from unittest.mock import MagicMock, patch, Mock
import pytest
import multiprocessing
import pygame
import src.game.menu.MyFrame as frame


@pytest.fixture()
def setup():
    pygame.init()
    test_menu = menu.MenuSetup()
    test_menu.label_error = Mock()
    test_menu.label_error.label_hide_show = Mock()
    test_menu.label_game_name = Mock()
    test_menu.label_game_name.winfo_y = Mock(return_value=5)
    test_menu.label_game_name.winfo_height = Mock(return_value=5)
    test_menu.interaction_frame = Mock()
    test_menu.interaction_frame.destroy = Mock()
    test_menu.back_button = Mock()
    test_menu.back_button.place = Mock()
    test_menu.back_button.configure = Mock()
    test_menu.main_frame = Mock()
    test_menu.main_frame.after = Mock()
    test_menu.entry_session_id = Mock()
    test_menu.entry_session_id.get = Mock()
    test_menu.conn1, setup.conn2 = multiprocessing.Pipe(duplex=True)
    yield test_menu


def test_load_main_frame(setup):
    assert setup.load_main_frame() is None


def test_load_interaction_frame(setup):
    while setup.test:
        assert setup.root.update() is None
        assert setup.load_interaction_frame() is None


def test_load_choose_map_frame(setup):
    while setup.test:
        assert setup.load_choose_map_frame() is None
        setup.interaction_frame.destroy.assert_called()
        setup.back_button.place.assert_called()


def test_load_lobby_frame(setup):
    while setup.test:
        assert setup.load_lobby_frame() is None
        setup.back_button.configure.assert_called_with(text="Leave Lobby")
        setup.label_game_name.winfo_y.assert_called()
        setup.label_game_name.winfo_height.assert_called()


# loop
def test_load_player(setup):
    while setup.test:
        path = os.path.join("mock_resources", "basicmap", "player", "basic_player_magenta.png")
        assert setup.load_player(5.0, path) is None
        assert setup.load_player(5, path) is None
        assert setup.load_player(0, path) is None
        assert setup.load_player(-5.0, path) is None


def test_update_player(setup):
    setup.data["map"] = "schneemap"
    assert setup.update_player() is None
    setup.main_frame.after.assert_called()
    setup.data["map"] = "platformmap"
    assert setup.update_player() is None
    setup.main_frame.after.assert_called()
    setup.data["map"] = "basicmap"
    assert setup.update_player() is None
    setup.main_frame.after.assert_called()


# test_start_new_session only calls another already tested method


def test_create_lobby(setup):
    assert setup.create_lobby("Schneemap") is None


def test_start_network(setup):
    success_func = MagicMock()
    update_func = MagicMock()
    assert setup.start_network("test", success_func, update_func) is None
    success_func.assert_called()
    assert setup.start_network("", success_func, update_func) is None


def test_start_game(setup):
    with patch('src.game.gamelogic.game.Game') as game_mock:
        assert setup.start_game() is None
        game_mock.assert_called()


# join_lobby only calls start_network, already tested


def test_back_to_start(setup):
    while setup.test:
        assert setup.back_to_start() is None


def test_if_game_started(setup):
    with patch('src.game.gamelogic.game.Game') as game_mock:
        setup.data["game_started"] = True
        assert setup.check_if_game_started() is None
        setup.data["game_started"] = False
        assert setup.check_if_game_started() is None
        game_mock.assert_called()


def test_update_background_process(setup):
    assert setup.update_background_process() is None


def test_clear_frame_sliding(setup):
    test_frame = MagicMock()
    assert setup.clear_frame_sliding(test_frame, "n", 10, 0) is None
    assert setup.clear_frame_sliding(test_frame, "ne", 0, 20) is None
    assert setup.clear_frame_sliding(test_frame, "w", -10) is None
    assert setup.clear_frame_sliding(test_frame, "sw") is None
    assert setup.clear_frame_sliding(test_frame, "nw") is None
    assert setup.clear_frame_sliding(test_frame, "se") is None

