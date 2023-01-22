import socket
import struct
from time import sleep


class Network:

    def __init__(self, msg):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "localhost"
        # For this to work on your machine this must be equal to the ipv4 address of the machine running the server
        # You can find this address by typing ipconfig in CMD and copying the ipv4 address. Again this must be the servers
        # ipv4 address. This feild will be the same for all your clients.
        self.port = 5555
        self.addr = (self.host, self.port)
        self.id, self.session_id = self.connect_lobby(msg)
        # self.gid, self.id = self.connect()

    def connect_lobby(self, p):
        """
        create a connection, and transmit the session_id, or select a map using a map name
        :param p: session_id or map name
        :return: player_id and session_id, if player_id = 5 error message in session_id
        """
        self.client.connect(self.addr)
        self.client.sendall(str.encode(p))
        pid, msg = self.client.recv(2048).decode().split(",")
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


if __name__ == '__main__':
    # create networkelement also creates connection
    net = Network("basicmap")
    # net = Network("ASDF")
    # check for errors, like full lobby, or unknown session_id or server, or if none no connection
    if net.id == 5 or net.id is None:
        print(net.session_id)
    pressed_button = False
    while True:
        sleep(1)
        try:
            number_of_players_connected = int(net.check_lobby())
            print(number_of_players_connected)

            # display connected players
            # ...

            if pressed_button or number_of_players_connected == 4:
                break
        except ValueError:
            print(net.check_lobby())
            exit(1)

    net.
