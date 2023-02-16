import src.game.menu.MyLabel as label
import src.game.menu.MyFrame as frame
import src.game.menu.MyWindow as window
import pytest
import customtkinter as tk
from PIL import Image


@pytest.fixture()
def setup():
    test_frame = frame.MyFrame(window.MyWindow(), 50, 50)
    test_image = tk.CTkImage(dark_image=Image.open("mock_filestructure/player/placeholder.png"), size=(3, 4))
    test_label = label.MyLabel(master=test_frame, text=None, image=test_image, fg_color="#212121")
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
    setup.label_hide_show(3, 4, 3, "test")
