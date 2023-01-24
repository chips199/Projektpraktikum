from src.game import game
from src.game.network import Network

if __name__ == "__main__":
    # net = Network()
    g = game.Game(1600, 900)
    g.run()
