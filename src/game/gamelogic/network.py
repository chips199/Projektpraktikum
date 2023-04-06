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
        self.host, self.port = "4.tcp.eu.ngrok.io", 10337
        # self.host, self.port = "localhost", 5556
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
            print("REPLY:", rply)
        except socket.timeout:
            rply = "5,No connection possible"
        print(rply)
        pid, msg = rply.split(",")
        return pid, msg

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
        """
        returns the number of players in the lobby provided by the server
        """
        return self.send("lobby_check")

    def start_game(self):
        """
        sets the spawnpoints provided by the server and starts a game
        """
        self.spawnpoints = json.loads(self.send("get_spawnpoints"))
        return self.send("ready")

    def get_map(self):
        """
        returns the name of the map selected in the lobby
        """
        return self.send("get Mapname")

    def game_started(self):
        """
        checks if the game has started
        """
        rpl = self.send("game started")
        return rpl == "True"
