import json
import os
from copy import copy
import datetime
from threading import Thread

import pandas as pd
import pygame

from src.game import canvas
from src.game.map import Map
from src.game import player as Player
from src.game.network import Network
from src.game import weapon as Weapon

wrk_dir = os.path.abspath(os.path.dirname(__file__))
config_file = wrk_dir + r'\configuration.json'
basic_map = wrk_dir + r"\..\basicmap"
platformmap = wrk_dir + r"\..\platformmap"
map_names_dict = {"basicmap": basic_map,
                  "platformmap": platformmap}

clock = pygame.time.Clock()


class Game:

    def __init__(self, w, h, net):
        self.net = net
        self.width = w
        self.height = h
        self.canvas = canvas.Canvas(self.width, self.height, str(self.net.id) + "Stick  Wars")
        self.map = Map(self, map_names_dict[net.map_name])
        # load the config for default values
        # this will later be done in the map to configure spawnpoints
        with open(config_file) as file:
            config = json.load(file)

        # if a map has player images generate use them if not don't
        if len(self.map.player_uris) == 4:
            self.playerList = [
                Player.Player(config['0']['position'][0], config['0']['position'][1], self, self.map.player_uris[0]),
                Player.Player(config['1']['position'][0], config['1']['position'][1], self, self.map.player_uris[1]),
                Player.Player(config['2']['position'][0], config['2']['position'][1], self, self.map.player_uris[2]),
                Player.Player(config['3']['position'][0], config['3']['position'][1], self, self.map.player_uris[3])]
        else:
            self.playerList = [
                Player.Player(config['0']['position'][0], config['0']['position'][1], (0, 255, 0)),
                Player.Player(config['1']['position'][0], config['1']['position'][1], (255, 255, 0)),
                Player.Player(config['2']['position'][0], config['2']['position'][1], (0, 255, 255)),
                Player.Player(config['3']['position'][0], config['3']['position'][1], (255, 0, 255))]

    def run(self):
        """
        the core method of the game containing the game loop
        """
        # pygame stuff
        # clock = pygame.time.Clock()
        run = True

        # just for comfort
        id = int(self.net.id)

        thread = Thread(target=self.send_data)
        thread.start()
        thread.join()

        # game loop
        while run:
            # pygame stuff for the max fps
            clock.tick(60)
            print()
            print("FPS:", self.update_fps())
            if self.playerList[id].is_alive():
                time = datetime.datetime.now()
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
                print("Handling Events:", datetime.datetime.now() - time)
                time = datetime.datetime.now()

                # get the key presses
                keys = pygame.key.get_pressed()

                if keys[pygame.K_d] and not self.playerList[id].block_x_axis:
                    self.playerList[id].move(0, self.nextToSolid(self.playerList[id], 0, self.playerList[id].velocity))

                if keys[pygame.K_a] and not self.playerList[id].block_x_axis:
                    self.playerList[id].move(1, self.nextToSolid(self.playerList[id], 1, self.playerList[id].velocity))

                # Jump
                if keys[pygame.K_SPACE] or self.playerList[id].is_jumping:
                    self.playerList[id].jump(func=self.nextToSolid)

                # gravity
                self.playerList[id].gravity(func=self.nextToSolid)

                print("Handling Keys:", datetime.datetime.now() - time)
                time = datetime.datetime.now()

            # Mouse Position
            self.playerList[id].mousepos = pygame.mouse.get_pos()
            print("Handling mouse:", datetime.datetime.now() - time)
            time = datetime.datetime.now()

            # Send Data about this player and get some over the others als reply
            # reply = self.send_data()
            # synchronise positions
            # pos = self.parse_pos(reply)
            # for i, position in enumerate(pos):
            #     self.playerList[i].x, self.playerList[i].y = position
            # for p in self.playerList:
            #     if p == self.playerList[id]:
            #         continue
            #     p.refresh_solids()
            # # synchronise Online stati
            # online = self.parse_online(reply)
            # for i, on in enumerate(online):
            #     self.playerList[i].is_connected = on
            # # sync mouse
            # mouse = self.parse_mouse(reply)
            # for i, on in enumerate(mouse):
            #     self.playerList[i].mousepos = on

            print("Handling Data:", datetime.datetime.now() - time)
            time = datetime.datetime.now()

            # Draw Map
            self.map.draw(self.canvas.get_canvas())
            # Draw Players
            for p in self.playerList:
                if p.is_connected:
                    p.draw(self.canvas.get_canvas())
                    pygame.draw.circle(self.canvas.get_canvas(), (255, 0, 0), p.mousepos, 20)
            # Update Canvas
            self.canvas.update()

            print("Handling redraw:", datetime.datetime.now() - time)
            time = datetime.datetime.now()

        pygame.quit()

    def send_data(self):
        """
        Send position to server
        :return: String with data of all players
        """
        with open(config_file) as file:
            sample = json.load(file)

        data = sample[str(self.net.id)]
        data['id'] = int(self.net.id)
        data['position'] = [int(self.playerList[int(self.net.id)].x), int(self.playerList[int(self.net.id)].y)]
        data['connected'] = True
        data['mouse'] = self.playerList[int(self.net.id)].mousepos
        reply = self.net.send(json.dumps(data))

        pos = self.parse_pos(reply)
        for i, position in enumerate(pos):
            self.playerList[i].x, self.playerList[i].y = position
        for p in self.playerList:
            if p == self.playerList[int(self.net.id)]:
                continue
            p.refresh_solids()
        # synchronise Online stati
        online = self.parse_online(reply)
        for i, on in enumerate(online):
            self.playerList[i].is_connected = on
        # sync mouse
        mouse = self.parse_mouse(reply)
        for i, on in enumerate(mouse):
            self.playerList[i].mousepos = on
        # return reply

    # def send_data(self):
    #     """
    #     Send position to server
    #     :return: String with data of all players
    #     """
    #     while self.running:
    #         print("ASYNC")
    #         with open(config_file) as file:
    #             sample = json.load(file)
    #
    #         data = sample[str(self.net.id)]
    #         data['id'] = int(self.net.id)
    #         data['position'] = [int(self.playerList[int(self.net.id)].x), int(self.playerList[int(self.net.id)].y)]
    #         data['connected'] = True
    #         data['mouse'] = self.playerList[int(self.net.id)].mousepos
    #         reply = self.net.send(json.dumps(data))
    #         self.reply = reply
    #
    #         self.online = self.parse_online(self.reply)
    #         self.pos = self.parse_pos(self.reply)
    #         self.mouse = self.parse_mouse(self.reply)
    #         # return  # reply

    @staticmethod
    def update_fps():
        fps = str(int(clock.get_fps()))
        return fps

    @staticmethod
    def parse_pos(data):
        """
        extracts positions from server data
        :param data: string from server
        :return: list of player positions
        """
        erg = []
        try:
            jdata = json.loads(data)
            for d in jdata:
                erg.append(jdata[d]["position"])
            return erg
        except:
            erg.clear()
            with open(config_file) as file:
                sample = json.load(file)
            for p in sample:
                erg.append(sample[p]["position"])
            return erg

    @staticmethod
    def parse_online(data):
        """
        extracts online information from server data
        :param data: string from server
        :return: list of online stati
        """
        erg = []
        try:
            jdata = json.loads(data)
            for d in jdata:
                erg.append(jdata[d]["connected"])
            return erg
        except:
            erg.clear()
            with open(config_file) as file:
                sample = json.load(file)
            for p in sample:
                erg.append(sample[p]["connected"])
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
        other_players = self.playerList[:int(self.net.id)] + self.playerList[int(self.net.id) + 1:]
        solid_pixels_df = copy(self.map.solid_df)
        for op in other_players:
            solid_pixels_df = pd.concat([solid_pixels_df, op.solid_df])
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
