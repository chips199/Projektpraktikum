import os.path
import src.game.menu.MyLabel as label
import src.game.menu.MyFrame as frame
import src.game.menu.MyWindow as window
import pytest
import customtkinter as tk
from PIL import Image


@pytest.fixture()
def setup():
    wrk_dir = os.path.abspath(os.path.dirname(__file__))
    test_frame = frame.MyFrame(window.MyWindow(), 50, 50)
    test_image = tk.CTkImage(dark_image=Image.open(os.path.join(wrk_dir, "mock_resources", "basicmap", "player", "basic_player_orange.png")), size=(3, 4))
    test_label = label.MyLabel(master=test_frame, text=None, image=test_image)
    return test_label


def test_set_sizing(setup):
    setup.set_sizing(3.0, 3.5)
    assert setup.sizing_width == 3.0
    assert setup.sizing_height == 3.5
    setup.set_sizing(4, 3)
    assert setup.sizing_width == 4
    assert setup.sizing_height == 3
    setup.set_sizing(-3.0, 3.5)
    assert setup.sizing_width == -3.0
    assert setup.sizing_height == 3.5
    setup.set_sizing(3.0, -3.5)
    assert setup.sizing_width == 3.0
    assert setup.sizing_height == -3.5
    setup.set_sizing(-3.0, -3.5)
    assert setup.sizing_width == -3.0
    assert setup.sizing_height == -3.5


def test_label_hide_show(setup):
    assert setup.label_hide_show(3, 4, 3, "test") is None


def test_set_rel_positions(setup):
    assert setup.set_rel_positions(0, 0) is None
    assert setup.current_rely == 0
    assert setup.current_relx == 0
    assert setup.set_rel_positions(1, -1) is None
    assert setup.current_rely == -1
    assert setup.current_relx == 1
    assert setup.set_rel_positions(-1, 1) is None
    assert setup.current_rely == 1
    assert setup.current_relx == -1


def test_move_on_y_axis(setup):
    assert setup.move_on_y_axis() is None
    assert setup.move_on_y_axis(1, 0.5, 0.05, 17) is None


def test_animate_on_y_axis(setup):
    assert setup.idle_animation_on_y_axis() is None
    assert setup.idle_animation_on_y_axis(0.5, 0.6, "two", 27, 0.006) is None
