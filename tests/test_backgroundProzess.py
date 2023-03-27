import multiprocessing
import src.game.gamelogic.backgroundProcess as process
import time


def test_background_connection():
    conn1, conn2 = multiprocessing.Pipe(duplex=True)
    connection = multiprocessing.Process(target=process.backgroundProzess, args=("abc", conn2))
    connection.start()
    assert connection.terminate() is None
    time.sleep(15)
    assert connection.close() is None

# Background Connection cannot be used as an object and therefore testsneed to be indirect
