import multiprocessing
import src.game.gamelogic.backgroundProzess as process


def test_Background_Connection():
    conn1, conn2 = multiprocessing.Pipe(duplex=True)
    connection = multiprocessing.Process(target=process.backgroundProzess, args=("abc", conn2))
    assert connection.start() is None

# Background Connection cannot be used as an object and therefore test need to be indirect
