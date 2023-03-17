import src.game.gamelogic.game as game
import pytest
import multiprocessing
import src.game.gamelogic.backgroundProzess as process


@pytest.fixture
def setup():
    conn1, conn2 = multiprocessing.Pipe(duplex=True)
    test_process = multiprocessing.Process(target=process.backgroundProzess, args=("abc", conn2))
    test_process.start()
    return game.Game(50, 50, conn1, test_process)


#looping
# def test_print_loading(setup):
#    x = 0
#    while x < 1:
#        x = x + 0.1
#        assert setup.print_loading(x) is None
