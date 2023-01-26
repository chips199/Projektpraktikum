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
        self.net = Network(msg)
        self.conn = connection

        self.counter = 0
        self.timer = datetime.datetime.now()
        self.reply = "empty"

        self.net.send("ready")

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

            with open(config_file) as file:
                sample = json.load(file)

            data = sample[str(self.net.id)]
            data['id'] = int(self.net.id)
            data['position'] = [int(100), int(100)]
            data['connected'] = True
            data['mouse'] = [int(100), int(100)]
            self.reply = self.net.send(json.dumps(data))

            data = {
                "id": self.net.id,
                "s_id": self.net.session_id,
                # "amount_player": self.net.check_lobby(),
                # "game_started": self.net.game_started()
            }
            # print("background Prozess")
            # data.append(self.net.id),
            # data.append(self.net.session_id)
            self.conn.send(data)
            # print(id)
            sleep(0.005)

    # def get_session_id(self):
    #     return self.net.id
