import json
import os
import time
from copy import copy
import datetime

import pandas as pd
import pygame

import multiprocessing

from src.game import canvas
from src.game.map import Map
from src.game import player as Player
from src.game import weapon as Weapon

wrk_dir = os.path.abspath(os.path.dirname(__file__))
config_file = wrk_dir + r'\configuration.json'
basic_map = "\\".join(str(wrk_dir).split("\\")[:-1]) + r"\basicmap"
platformmap = "\\".join(str(wrk_dir).split("\\")[:-1]) + r"\platformmap"
schneemap = "\\".join(str(wrk_dir).split("\\")[:-1]) + r"\schneemap"
map_names_dict = {"basicmap": basic_map,
                  "platformmap": platformmap,
                  "schneemap": schneemap}

clock = pygame.time.Clock()


class Game:

    def __init__(self, w, h, conn):
        self.counter = 0
        self.conn = conn
        # self.data = {
        #     "1": {
        #         "id": 0,
        #         "position": [50, 50],
        #         "mouse": [50, 50],
        #         "connected": False,
        #         "health": 100
        #     },
        #     "2": {
        #         "id": 0,
        #         "position": [50, 50],
        #         "mouse": [50, 50],
        #         "connected": False,
        #         "health": 100
        #     },
        #     "3": {
        #         "id": 0,
        #         "position": [50, 50],
        #         "mouse": [50, 50],
        #         "connected": False,
        #         "health": 100
        #     },
        #     "4": {
        #         "id": 0,
        #         "position": [50, 50],
        #         "mouse": [50, 50],
        #         "connected": False,
        #         "health": 100
        #     },
        #     "id": 0
        # }
        self.timer = datetime.datetime.now()
        self.update_background_process()
        self.id = int(self.data['id'])
        print(self.data)


        # pygame.init()
        pygame.display.set_icon(pygame.image.load(wrk_dir + r"\..\stick_wars_logo.png"))
        self.width = w
        self.height = h
        self.canvas = canvas.Canvas(self.width, self.height, str(self.id) + "Stick  Wars")
        # self.map = Map(self, map_names_dict[self.data['map_name']])
        self.map = Map(self, map_names_dict[self.data["metadata"]["map"]])
        self.online = [False, False, False, False]
        self.this_player_pos = [700, 50]
        self.pos = [[100, 100], [200, 100], [300, 100], [400, 100]]
        self.mouse = [[0, 0], [0, 0], [0, 0], [0, 0]]
        self.player_frames = [[0, False, 1], [0, False, 1], [0, False, 1], [0, False, 1]]
        self.weapon_frames = [[0, False, 1], [0, False, 1], [0, False, 1], [0, False, 1]]
        # load the config for default values
        # this will later be done in the map to configure spawnpoints
        with open(config_file) as file:
            config = json.load(file)

        self.playerList = [
            Player.Player(self.data["metadata"]["spawnpoints"]["0"], directory=self.map.player_uris[0]),
            Player.Player(self.data["metadata"]["spawnpoints"]["1"], directory=self.map.player_uris[1]),
            Player.Player(self.data["metadata"]["spawnpoints"]["2"], directory=self.map.player_uris[2]),
            Player.Player(self.data["metadata"]["spawnpoints"]["3"], directory=self.map.player_uris[3])]

    def run(self):
        """
        the core method of the game containing the game loop
        """
        # pygame stuff
        # clock = pygame.time.Clock()
        run = True

        # just for comfort
        id = self.id

        # game loop
        while run:
            fps_timer = datetime.datetime.now()

            # pygame stuff for the max fps
            clock.tick(100)
            # print()
            print("FPS:", self.update_fps())
            # timer = datetime.datetime.now()
            if self.playerList[id].is_alive():
                # handling pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False

                    if event.type == pygame.K_ESCAPE:
                        run = False

                # print("Handling Events:", datetime.datetime.now() - time)
                # time = datetime.datetime.now()

                # get the key presses
                keys = pygame.key.get_pressed()

                # Hit
                if keys[pygame.K_s]:
                    # Check if Player can use his weapon
                    if self.playerList[id].weapon.can_hit():
                        # Check if an enemy player is in range
                        self.playerList[id].weapon.hit()
                        self.playerList[id].weapon.set_animation_direction(self.playerList[id].animation_direction)

                if keys[pygame.K_d] and not self.playerList[id].block_x_axis:
                    if self.playerList[id].landed:
                        self.playerList[id].set_animation_direction(1)
                    self.playerList[id].move(0, self.nextToSolid(self.playerList[id], 0, self.playerList[id].velocity))

                elif keys[pygame.K_a] and not self.playerList[id].block_x_axis:
                    if self.playerList[id].landed:
                        self.playerList[id].set_animation_direction(2)
                    self.playerList[id].move(1, self.nextToSolid(self.playerList[id], 1, self.playerList[id].velocity))

                # Jump
                if keys[pygame.K_SPACE] or self.playerList[id].is_jumping or keys[pygame.K_w]:
                    self.playerList[id].stop_animation()
                    self.playerList[id].jump(func=self.nextToSolid)

                # gravity
                self.playerList[id].gravity(func=self.nextToSolid)

                # print("Handling Keys:", datetime.datetime.now() - timer)
                # timer = datetime.datetime.now()

            # Mouse Position
            self.playerList[id].mousepos = pygame.mouse.get_pos()
            # print("Handling mouse:", datetime.datetime.now() - timer)
            # timer = datetime.datetime.now()

            # Send Data about this player and get some over the others als reply
            self.send_to_background_process()
            # print("Handling send:", datetime.datetime.now() - timer)
            # timer = datetime.datetime.now()
            self.update_background_process()
            # print("Handling update:", datetime.datetime.now() - timer)
            # timer = datetime.datetime.now()

            # synchronise positions
            self.pos = self.parse_pos()
            for i, position in enumerate(self.pos):
                self.playerList[i].x, self.playerList[i].y = position
            for p in self.playerList:
                if p == self.playerList[id]:
                    continue
                p.refresh_solids()

            # synchronise Online stati
            self.online = self.parse_online()
            for i, on in enumerate(self.online):
                self.playerList[i].is_connected = on

            # sync mouse
            # mouse = self.parse_mouse(self.data)
            # for i, on in enumerate(self.mouse):
            #     self.playerList[i].mousepos = on

            # sync animation frames from player and weapon
            self.player_frames, self.weapon_frames = self.parse_frame()
            for i, (data_player, data_weapon) in enumerate(zip(self.player_frames, self.weapon_frames)):
                self.playerList[i].current_frame = data_player[0]
                self.playerList[i].animation_running = data_player[1]
                self.playerList[i].animation_direction = data_player[2]
                self.playerList[i].weapon.current_frame = data_weapon[0]
                self.playerList[i].weapon.animation_running = data_weapon[1]
                self.playerList[i].weapon.animation_direction = data_weapon[2]

            # print("Handling pos parsing:", datetime.datetime.now() - timer)
            # timer = datetime.datetime.now()

            # Draw Map
            self.map.draw(self.canvas.get_canvas())
            # Draw Players
            for p in self.playerList:
                if p.is_connected:
                    p.draw(self.canvas.get_canvas())
                    pygame.draw.circle(self.canvas.get_canvas(), (255, 0, 0), p.mousepos, 20)
            # Update Canvas
            self.canvas.update()
            # print("Handling redraw:", datetime.datetime.now() - timer)
            # timer = datetime.datetime.now()

            while datetime.datetime.now() - fps_timer < datetime.timedelta(milliseconds=16):
                continue
            self.send_to_background_process()

            # print("TOTAL TIME:", datetime.datetime.now() - fps_timer)

        # self.process.kill() # process muss noch aus MenuSetup übergeben werden
        pygame.quit()

    def update_background_process(self):
        # if datetime.datetime.now() - self.timer >= datetime.timedelta(seconds=1):
        #     self.timer = datetime.datetime.now()
        #     print("count in Menu:", self.counter)
        #     self.counter = 0
        # else:
        #     self.counter += 1
        new_data = None
        # while not self.conn.poll():
        #     continue
        while self.conn.poll():
            new_data = self.conn.recv()
        if type(new_data) == str:
            self.data = json.loads(new_data)

    def send_to_background_process(self):
        temp_data = {
            "position": [int(self.playerList[int(self.data["id"])].x), int(self.playerList[int(self.data["id"])].y)],
            "mouse": self.playerList[int(self.data['id'])].mousepos,
            "player_frame": [self.playerList[int(self.data['id'])].current_frame,
                             self.playerList[int(self.data['id'])].animation_running,
                             self.playerList[int(self.data['id'])].animation_direction],
            "weapon_frame": [self.playerList[int(self.data['id'])].weapon.current_frame,
                             self.playerList[int(self.data['id'])].weapon.animation_running,
                             self.playerList[int(self.data['id'])].weapon.animation_direction]
        }
        self.conn.send(temp_data)

    @staticmethod
    def update_fps():
        fps = str(int(clock.get_fps()))
        return fps

    def parse_frame(self):
        """
        extracts positions from server data
        :return: list of player frames [current_frame, animation_running, animation_direction],
                 list of weapon frames[current_frame, animation_running, animation_direction]
        """
        erg_player = []
        erg_weapon = []
        for key, value in self.data.items():
            # since a fifth dictionary entry named 'id' is added for the player id, ignore this key/entry
            if key != "id":
                for key2, value2 in value.items():
                    if key2 == "player_frame":
                        if key != str(self.id):
                            erg_player.append(value2)
                        else:
                            erg_player.append([self.playerList[int(self.data["id"])].current_frame,
                                               self.playerList[int(self.data["id"])].animation_running,
                                               self.playerList[int(self.data["id"])].animation_direction])
                    elif key2 == "weapon_frame":
                        if key != str(self.id):
                            erg_weapon.append(value2)
                        else:
                            erg_weapon.append([self.playerList[int(self.data["id"])].weapon.current_frame,
                                               self.playerList[int(self.data["id"])].weapon.animation_running,
                                               self.playerList[int(self.data["id"])].weapon.animation_direction])
            else:
                continue
        return erg_player, erg_weapon

    # @staticmethod
    def parse_pos(self):
        """
        extracts positions from server data
        :return: list of player positions
        """
        erg = []
        for key, value in self.data.items():
            if key != "id":
                for key2, value2 in value.items():
                    if key2 == "position":
                        if key != str(self.id):
                            erg.append(value2)
                        else:
                            erg.append([int(self.playerList[int(self.data["id"])].x),
                                        int(self.playerList[int(self.data["id"])].y)])
            else:
                continue
        return erg

    # @staticmethod
    def parse_online(self):
        """
        extracts online information from server data
        :return: list of online stati
        """
        erg = []
        for key, value in self.data.items():
            if key != "id":
                for key2, value2 in value.items():
                    if key2 == "connected":
                        if key != str(self.id):
                            erg.append(value2)
                        else:
                            erg.append(True)
            else:
                continue
        return erg

    @staticmethod
    def parse_mouse(data):
        """
        extracts mouse information from server data
        :param data: string from server
        :return: list of mouse positions
        """
        erg = []
        try:
            jdata = json.loads(data)
            for d in jdata:
                erg.append(jdata[d]["mouse"])
            return erg
        except:
            erg.clear()
            with open(config_file) as file:
                sample = json.load(file)
            for p in sample:
                erg.append(sample[p]["mouse"])
            return erg

    def nextToSolid(self, player, dirn, distance):
        """
        calculates the distance to the nearest object in one direction in a range
        :param player: the current player
        :param dirn: the direction
        :param distance: the range in which to check
        :return: integer representing the distance to the next object within the range
        """
        # first combining all solid pixels in one dataframe
        # other_players = self.playerList[:self.id] + self.playerList[self.id + 1:]
        solid_pixels_df = copy(self.map.solid_df)
        # for op in other_players:
        #     solid_pixels_df = pd.concat([solid_pixels_df, op.solid_df])
        # getting copy of the players solid dataframe
        simulated_player = copy(player.solid_df)
        erg = 0

        Player.Player.shift_df(simulated_player, dirn, distance)
        if pd.merge(simulated_player, solid_pixels_df, how='inner', on=['x', 'y']).empty:
            erg = distance
            return erg
        Player.Player.shift_df(simulated_player, dirn, -distance)

        # checking for each pixel if a move ment would cause a collision
        for _ in range(distance):
            Player.Player.shift_df(simulated_player, dirn, 1)
            if not pd.merge(simulated_player, solid_pixels_df, how='inner', on=['x', 'y']).empty:
                return erg
            erg += 1
        return erg
