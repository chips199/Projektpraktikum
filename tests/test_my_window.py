import src.game.menu.MyWindow as window
import pytest
import multiprocessing
from src.game.gamelogic import backgroundProcess
from unittest.mock import MagicMock, Mock
import pygame


@pytest.fixture
def setup():

    # set up test subject

    pygame.init()
    return window.MyWindow()


def test_set_size(setup):

    # check for correct result

    setup.set_size(50, 50)
    assert setup.window_width == 50
    assert setup.window_height == 50


def test_set_sizing(setup):

    # check for correct result

    setup.set_sizing(50, 50)
    assert setup.sizing_height == 50
    assert setup.sizing_width == 50


def test_on_closing(setup):

    # check for error free execution

    assert setup.on_closing() is None


def test_set_process(setup):

    # set up process and check for error free execution

    conn1, conn2 = multiprocessing.Pipe(duplex=True)
    process = multiprocessing.Process(target=backgroundProcess, args=("test", conn2))
    assert setup.set_process(process) is None


def test_move_out_of_window(setup):

    # mock different values and check for error free execution for every direction, positive as well as zero values

    frame = MagicMock()
    frame.winfo_y = Mock(return_value=2)
    frame.winfo_height = Mock(return_value=2)
    frame.winfo_x = Mock(return_value=2)
    frame.winfo_width = Mock(return_value=2)
    assert setup.move_out_of_window(frame, 'up', 'n') is None
    assert setup.move_out_of_window(frame, 'left', 'ne') is None
    assert setup.move_out_of_window(frame, 'right', 'se') is None
    assert setup.move_out_of_window(frame, 'down', 'e') is None
    assert setup.move_out_of_window(frame, 'up', 'sw') is None
    assert setup.move_out_of_window(frame, 'up', 's') is None
    assert setup.move_out_of_window(frame, 'up', 'nw') is None
    assert setup.move_out_of_window(frame, 'up', 'w') is None
    frame.winfo_y = Mock(return_value=0)
    frame.winfo_height = Mock(return_value=0)
    frame.winfo_x = Mock(return_value=0)
    frame.winfo_width = Mock(return_value=0)
    assert setup.move_out_of_window(frame, 'up', 'n') is None
    assert setup.move_out_of_window(frame, 'left', 'ne') is None
    assert setup.move_out_of_window(frame, 'right', 'se') is None
    assert setup.move_out_of_window(frame, 'down', 'e') is None
    assert setup.move_out_of_window(frame, 'up', 'sw') is None
    assert setup.move_out_of_window(frame, 'up', 's') is None
    assert setup.move_out_of_window(frame, 'up', 'nw') is None
    assert setup.move_out_of_window(frame, 'up', 'w') is None
