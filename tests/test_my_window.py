import src.game.menu.MyWindow as window
import pytest
import multiprocessing
from src.game.gamelogic import backgroundProzess
from unittest.mock import MagicMock, Mock


@pytest.fixture
def setup():
    return window.MyWindow()


def test_set_size(setup):
    setup.set_size(50, 50)
    assert setup.window_width == 50
    assert setup.window_height == 50


def test_set_sizing(setup):
    setup.set_sizing(50, 50)
    assert setup.sizing_height == 50
    assert setup.sizing_width == 50


def test_on_closing(setup):
    assert setup.on_closing() is None


def test_set_process(setup):
    conn1, conn2 = multiprocessing.Pipe(duplex=True)
    process = multiprocessing.Process(target=backgroundProzess, args=("test", conn2))
    assert setup.set_process(process) is None


def test_move_out_of_window(setup):
    frame = MagicMock()
    frame.winfo_y = Mock(return_value=2)
    frame.winfo_height = Mock(return_value=2)
    frame.winfo_x = Mock(return_value=2)
    frame.winfo_width = Mock(return_value=2)
    setup.move_out_of_window(frame, 'up', 'n')
    setup.move_out_of_window(frame, 'left', 'ne')
    setup.move_out_of_window(frame, 'right', 'se')
    setup.move_out_of_window(frame, 'down', 'e')
    setup.move_out_of_window(frame, 'up', 'sw')
    setup.move_out_of_window(frame, 'up', 's')
    setup.move_out_of_window(frame, 'up', 'nw')
    setup.move_out_of_window(frame, 'up', 'w')
    frame.winfo_y = Mock(return_value=0)
    frame.winfo_height = Mock(return_value=0)
    frame.winfo_x = Mock(return_value=0)
    frame.winfo_width = Mock(return_value=0)
    setup.move_out_of_window(frame, 'up', 'n')
    setup.move_out_of_window(frame, 'left', 'ne')
    setup.move_out_of_window(frame, 'right', 'se')
    setup.move_out_of_window(frame, 'down', 'e')
    setup.move_out_of_window(frame, 'up', 'sw')
    setup.move_out_of_window(frame, 'up', 's')
    setup.move_out_of_window(frame, 'up', 'nw')
    setup.move_out_of_window(frame, 'up', 'w')
