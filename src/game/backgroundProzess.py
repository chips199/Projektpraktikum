import datetime
import os
import json

from src.game.network import Network
from time import sleep
from multiprocessing.connection import Connection

wrk_dir = os.path.abspath(os.path.dirname(__file__))
config_file = wrk_dir + r'\configuration.json'


class backgroundProzess:
    def __init__(self, msg, connection: Connection):
        print("IN PROZESS")
        print(msg)
        self.net = Network(msg)
        self.conn = connection

        self.counter = 0
        self.timer = datetime.datetime.now()
        self.reply = "empty"
        self.game_started = False

        # self.net.send("ready")

        while True:
            # print()
            # print("SET_background")
            # print()
            # if connection.poll():
            #     msg = connection.recv()
            #     print(msg)
            #     self.net.send_new_session_id(msg)
            if datetime.datetime.now() - self.timer >= datetime.timedelta(seconds=1):
                self.timer = datetime.datetime.now()
                print("count in Background:", self.counter)
                print(self.reply)
                self.counter = 0
            else:
                self.counter += 1

            if not self.game_started:
                self.check_game_started()
                if not self.game_started:
                    self.send_menu()
                else:
                    self.send_game()
            else:
                self.send_game()

            # print(id)
            sleep(0.01)

    # def get_session_id(self):
    #     return self.net.id

    def check_game_started(self):
        if self.conn.poll():
            msg = self.conn.recv()
            print(msg)
            if msg == "start":
                self.net.start_game()
                print("SHOULD START GAME")
                self.game_started = True
                return
        self.game_started = False

    def send_menu(self):
        # print("send menu")
        data = {
            "id": self.net.id,
            "s_id": self.net.session_id,
            "amount_player": self.net.check_lobby(),
            "game_started": self.net.game_started(),
            # "net": self.net
        }
        self.conn.send(data)

    def send_game(self):
        print("now send game data")
        with open(config_file) as file:
            sample = json.load(file)

        data = sample[str(self.net.id)]
        data['id'] = int(self.net.id)
        data['position'] = [int(100), int(100)]
        data['connected'] = True
        data['mouse'] = [int(100), int(100)]
        self.reply = self.net.send(json.dumps(data))
        self.conn.send(data)

