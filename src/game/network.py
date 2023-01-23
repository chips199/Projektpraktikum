import json
import socket
import struct
from _thread import start_new_thread
from time import sleep
from src.game import game


class Network:

    def __init__(self, msg):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "localhost"
        # For this to work on your machine this must be equal to the ipv4 address of the machine running the server
        # You can find this address by typing ipconfig in CMD and copying the ipv4 address. Again this must be the servers
        # ipv4 address. This feild will be the same for all your clients.
        self.port = 5556
        self.addr = (self.host, self.port)
        self.id, self.session_id = self.connect_lobby(msg)
        self.map_name = self.get_map()
        # self.gid, self.id = self.connect()

    def connect_lobby(self, p):
        """
        create a connection, and transmit the session_id, or select a map using a map name
        :param p: session_id or map name
        :return: player_id and session_id, if player_id = 5 error message in session_id
        """
        self.client.connect(self.addr)
        # sth = self.client.recv(2048)
        self.client.sendall(str.encode(p))
        rply = self.client.recv(2048).decode()
        print(rply)
        pid, msg = rply.split(",")
        return pid, msg

    def connect(self):
        self.client.connect(self.addr)
        msg = self.client.recv(2048).decode()
        gid, pid = msg.split(',')
        return gid, pid

    def send(self, data):
        """
        :param data: str
        :return: str
        """
        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error as e:
            return str(e)

    def check_lobby(self):
        return self.send("lobby_check")

    def start_game(self):
        self.spawnpoints = json.loads(self.send("get_spawnpoints"))
        return self.send("ready")

    def getSpawnpoint(self, id):
        return self.spawnpoints[str(id)]

    def get_max_number_of_players(self):
        return self.send("get max players")

    def get_map(self):
        return self.send("get Mapname")


def sth(str):
    # create networkelement also creates connection
    net = Network(str)
    # net = Network("ASDF")
    # check for errors, like full lobby, or unknown session_id or server, or if none no connection
    if net.id == 5 or net.id is None:
        print(net.session_id)
        exit(1)
    pressed_button = True
    while True:
        try:
            number_of_players_connected = int(net.check_lobby())
            # print(number_of_players_connected)

            # display connected players
            # ...

            if pressed_button or number_of_players_connected == int(net.get_max_number_of_players()):
                break
        except ValueError:
            print(net.check_lobby())
            exit(1)
    # start game
    map = net.start_game()
    g = game.Game(1600, 900, net, net.map_name)
    g.run()


if __name__ == '__main__':
    try:
        sth("basicmap")
    except ConnectionRefusedError:
        print("Connection failed")
