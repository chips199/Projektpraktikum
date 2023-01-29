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
basic_map = wrk_dir + r"\..\basicmap"
platformmap = wrk_dir + r"\..\platformmap"
schneemap = wrk_dir + r"\..\schneemap"
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

        # pygame.init()
        pygame.display.set_icon(pygame.image.load(wrk_dir + r"\..\stick_wars_logo.png"))
        self.width = w
        self.height = h
        self.canvas = canvas.Canvas(self.width, self.height, str(self.id) + "Stick  Wars")
        # self.map = Map(self, map_names_dict[self.data['map_name']])
        self.map = Map(self, basic_map)
        self.online = [False, False, False, False]
        self.this_player_pos = [700, 50]
        self.pos = [[100, 100], [200, 100], [300, 100], [400, 100]]
        self.mouse = [[0, 0], [0, 0], [0, 0], [0, 0]]
        # load the config for default values
        # this will later be done in the map to configure spawnpoints
        with open(config_file) as file:
            config = json.load(file)

        # if a map has player images generate use them if not don't
        if len(self.map.player_uris) == 4:
            self.playerList = [
                Player.Player(config['0']['position'][0], config['0']['position'][1], self.map.player_uris[0]),
                Player.Player(config['1']['position'][0], config['1']['position'][1], self.map.player_uris[1]),
                Player.Player(config['2']['position'][0], config['2']['position'][1], self.map.player_uris[2]),
                Player.Player(config['3']['position'][0], config['3']['position'][1], self.map.player_uris[3])]
        else:
            self.playerList = [
                Player.Player(config['0']['position'][0], config['0']['position'][1], (0, 255, 0)),
                Player.Player(config['1']['position'][0], config['1']['position'][1], (255, 255, 0)),
                Player.Player(config['2']['position'][0], config['2']['position'][1], (0, 255, 255)),
                Player.Player(config['3']['position'][0], config['3']['position'][1], (255, 0, 255))]

        self.min_timer = 0
        self.max_timer = 0
        self.counter_reset_timer = 0
        self.time_total = 0
        self.new_fps_timer = datetime.datetime.now()

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
            timer = datetime.datetime.now()
            if self.playerList[id].is_alive():
                # handling pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False

                    if event.type == pygame.K_ESCAPE:
                        run = False

                    # Hit
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Check if Player can use his weapon
                        if self.playerList[id].user_weapon.can_hit():
                            # Check if an enemy player is in range
                            self.playerList[id].user_weapon.hit()
                            for player in self.playerList:
                                #  Do not beat your own player
                                if player == self.playerList[id]:
                                    continue
                                # Check if the player was hit
                                # First check if the opponent is in range of the weapon
                                # Then check if the player's mouse is on the opponent
                                if player.x < self.playerList[id].x + self.playerList[id].width + self.playerList[
                                    id].user_weapon.distance and player.x + player.width > self.playerList[id].x - \
                                        self.playerList[
                                            id].user_weapon.distance and player.y < self.playerList[id].y + \
                                        self.playerList[id].height + self.playerList[
                                    id].user_weapon.distance and player.y + player.height > self.playerList[id].y - \
                                        self.playerList[
                                            id].user_weapon.distance and player.x < self.playerList[id].mousepos[
                                    0] < player.x + player.width \
                                        and player.y < self.playerList[id].mousepos[1] < player.y + player.height:
                                    # Draw damage from opponent
                                    player.beaten(self.playerList[id].user_weapon)
                                    break
                # print("Handling Events:", datetime.datetime.now() - timer)
                timer = datetime.datetime.now()

                # get the key presses
                keys = pygame.key.get_pressed()

                if keys[pygame.K_d] and not self.playerList[id].block_x_axis:
                    if self.playerList[id].landed:
                        self.playerList[id].set_animation_direction(1)
                    self.playerList[id].move(0, self.nextToSolid(self.playerList[id], 0, self.playerList[id].velocity))

                elif keys[pygame.K_a] and not self.playerList[id].block_x_axis:
                    if self.playerList[id].landed:
                        self.playerList[id].set_animation_direction(2)
                    self.playerList[id].move(1, self.nextToSolid(self.playerList[id], 1, self.playerList[id].velocity))

                # Jump
                if keys[pygame.K_SPACE] or self.playerList[id].is_jumping:
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
            # print("Position parsed:", self.pos)
            for i, position in enumerate(self.pos):
                # print("Type position:", type(position))
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
            for i, on in enumerate(self.mouse):
                self.playerList[i].mousepos = on

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

            # while datetime.datetime.now() - fps_timer < datetime.timedelta(milliseconds=20):
            #     continue
            self.send_to_background_process()

            # if self.counter_reset_timer > 0:
            #     print(round(self.time_total / 1000, 3) / self.counter_reset_timer)

            if self.counter_reset_timer > 0 and \
                    round(self.time_total / 1000, 3) / self.counter_reset_timer < 16:
                # print("counter reset timer:", self.counter_reset_timer)
                # print("time total:", round(self.time_total / 1000, 3))
                delay = self.counter_reset_timer * 16 - round(self.time_total / 1000, 3)
                # print("should wait:", delay)
                # print("---")
                # print("time now:", datetime.datetime.now())
                # print("delay:", datetime.timedelta(milliseconds=delay))
                # print("subtraktion:", datetime.datetime.now() - datetime.timedelta(milliseconds=delay))
                # print("in microseconds:", (datetime.datetime.now() - datetime.timedelta(milliseconds=delay)).microsecond)
                wait_time = datetime.datetime.now()
                while datetime.datetime.now() - wait_time < datetime.timedelta(microseconds=delay*1000):
                    # print("in while")
                    continue
                # print((datetime.datetime.now() - wait_time).microseconds / 1000)


            # while datetime.datetime.now() - fps_timer < datetime.timedelta(milliseconds=20):
            #     # print("wait Game")
            #     # self.send_to_background_process()
            #     continue

            # print("TOTAL TIME:", datetime.datetime.now() - fps_timer)

            # -----------------------------------------------
            this_time = int((datetime.datetime.now() - fps_timer).microseconds)
            # print("TYPE this time:", type(this_time), "VAL:", this_time)
            # print("TYPE min timer:", type(self.min_timer), "VAL:", self.min_timer)
            # print("TYPE max timer:", type(self.max_timer), "VAL:", self.max_timer)

            if self.counter_reset_timer == 0:
                # print("COUNTER RESET")
                self.min_timer = this_time
                self.max_timer = this_time
                self.time_total = 0
                # print(self.min_timer, type(self.min_timer))
                # print(self.max_timer, type(self.max_timer))
                # print(this_time < self.min_timer)
            elif this_time < self.min_timer:
                self.min_timer = this_time
            elif this_time > self.max_timer:
                self.max_timer = this_time
            self.counter_reset_timer += 1
            self.time_total += this_time

            # if self.counter_reset_timer == 60:
            if datetime.datetime.now() - self.new_fps_timer > datetime.timedelta(milliseconds=990):
                print("MIN TIME:", round(self.min_timer / 1000, 3))
                print("MAX TIME:", round(self.max_timer / 1000, 3))
                print("TIME TOTAL:", round(self.time_total / 1000, 3))
                print("COUNTER:", self.counter_reset_timer)
                print()
                self.counter_reset_timer = 0
                self.new_fps_timer = datetime.datetime.now()

            # -----------------------------------------------

        # self.process.kill() # muss noch übergeben werden
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
            "frame": self.playerList[int(self.data['id'])].current_frame
        }
        self.conn.send(temp_data)

    @staticmethod
    def update_fps():
        fps = str(int(clock.get_fps()))
        return fps

    # @staticmethod
    def parse_pos(self):
        """
        extracts positions from server data
        :param data: string from server
        :return: list of player positions
        """
        erg = []
        try:
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
        except Exception as e:
            print("EXCEPTION:", e)
            erg.clear()
            with open(config_file) as file:
                sample = json.load(file)
            for p in sample:
                erg.append(sample[p]["position"])
            return erg

    # @staticmethod
    def parse_online(self):
        """
        extracts online information from server data
        :param data: string from server
        :return: list of online stati
        """
        erg = []
        try:
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
        except:
            erg.clear()
            with open(config_file) as file:
                sample = json.load(file)
            for p in sample:
                erg.append(sample[p]["connected"])
            return erg

    @staticmethod
    def parse_mouse(data):  # noch nicht an background process angepasst
        """
        extracts mouse information from server data
        :param data: string from server
        :return: list of mouse positions
        """
        erg = []
        try:
            jdata = json.loads(data)
            for d in jdata:
                print("parse mouse d:", d)
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
        # other_players = self.playerList[:int(self.net.id)] + self.playerList[int(self.net.id) + 1:]
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
