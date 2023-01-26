import json
import socket
# from src.game import game


class Network:

    def __init__(self, msg):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(2)
        # use the url for connecting to an external server
        # use tht second line to connect to a local server, which is visible in a network
        # use the third if it is just local
        # self.host, self.port = "6.tcp.eu.ngrok.io", 19252
        # self.host, self.port = "10.170.48.131", 17586
        # self.host, self.port = socket.gethostbyname(socket.gethostname()), 5556
        self.host, self.port = "localhost", 5556
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
        if len(p) == 0:
            return "5", "Enter Session ID"
        try:
            self.client.connect(self.addr)
            self.client.sendall(str.encode(p))
            rply = self.client.recv(2048).decode()
        except socket.timeout:
            rply = "5,No connection possible"
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
        print(self.spawnpoints)
        return self.send("ready")

    def getSpawnpoint(self, id):
        return self.spawnpoints[str(id)]

    def get_max_number_of_players(self):
        return self.send("get max players")

    def get_map(self):
        return self.send("get Mapname")

    def game_started(self):
        rpl = self.send("game started")
        # print("rpl: " + rpl)
        # print("bool: " + str(rpl == "True"))
        return rpl == "True"


def sth(str):
    # create networkelement also creates connection
    net = Network(str)
    # check for errors, like full lobby, or unknown session_id or server, or if none no connection
    if net.id == 5 or net.id is None:
        print(net.session_id)
        exit(1)
    pressed_button = True
    while not net.game_started():
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
    net.start_game()
    # g = game.Game(1600, 900, net)
    # g.run()


if __name__ == '__main__':
    try:
        sth("basicmap")
    except ConnectionRefusedError:
        print("Connection failed")
