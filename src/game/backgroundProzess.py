import datetime
import os
import json
import time

from src.game.network import Network
from multiprocessing.connection import Connection

wrk_dir = os.path.abspath(os.path.dirname(__file__))
config_file = wrk_dir + r'\configuration.json'


class backgroundProzess:
    def __init__(self, msg, connection: Connection):
        print("IN PROZESS")
        print(msg)
        self.net = Network(msg)
        self.conn: Connection = connection

        self.counter = 0
        self.timer = datetime.datetime.now()
        self.reply = "empty"
        self.game_started = False

        self.position = [int(100), int(100)]
        self.mouse = [int(100), int(100)]
        self.player_frame = [0, False, 1]
        self.weapon_frame = [0, False, 1]

        while True:
            # fps_timer = datetime.datetime.now()
            # if datetime.datetime.now() - self.timer >= datetime.timedelta(seconds=1):
            #     self.timer = datetime.datetime.now()
            #     print("count in Background:", self.counter)
            #     self.counter = 0
            # else:
            #     self.counter += 1
            # timer = datetime.datetime.now()

            if not self.game_started:
                self.check_game_started()
            # check again if game started cause could have changed due to the check_game_started() func
            if not self.game_started:
                self.send_menu()
            else:
                self.update_game_pos()
                self.send_game()

    def check_game_started(self):
        if self.conn.poll():
            msg = self.conn.recv()
            if msg == "start":
                self.net.start_game()
                print("SHOULD START GAME")
                self.game_started = True
                time.sleep(1)
                return
        self.game_started = False

    def send_menu(self):
        data = {
            "id": self.net.id,
            "s_id": self.net.session_id,
            "amount_player": self.net.check_lobby(),
            "game_started": self.net.game_started(),
        }
        self.conn.send(data)

    def send_game(self):
        # print("now send game data")
        with open(config_file) as file:
            sample = json.load(file)

        data = sample[str(self.net.id)]
        data['id'] = int(self.net.id)
        data['position'] = self.position
        data['connected'] = True
        data['mouse'] = self.mouse
        data['player_frame'] = self.player_frame
        data['weapon_frame'] = self.weapon_frame
        self.reply = self.net.send(json.dumps(data))
        self.reply = json.loads(self.reply)
        self.reply["id"] = self.net.id
        self.reply = json.dumps(self.reply)
        self.conn.send(self.reply)

    def update_game_pos(self):
        while self.conn.poll():
            data = self.conn.recv()
            self.position = data['position']
            self.mouse = data['mouse']
            self.player_frame = data['player_frame']
            self.weapon_frame = data['weapon_frame']
