import src.game.menu.MyFrame as frame
import src.game.menu.MyWindow as window
import pytest
from unittest.mock import MagicMock


@pytest.fixture(scope="session")
def setup():
    test_frame = frame.MyFrame(window.MyWindow(), 50, 50)
    return test_frame


def test_clear_frame(setup):
    for widget in setup.winfo_children():
        widget.place_forget = MagicMock()
        widget.destroy = MagicMock()
    assert setup.clear_frame() is None
    for widget in setup.winfo_children():
        widget.place_forget.assert_called()
        widget.destroy.assert_called()
    setup.destroy()
