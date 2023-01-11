import json
import os
from copy import copy

import pandas as pd
import pygame
import datetime
from matplotlib import pyplot as plt

import canvas
from map import Map
from src.game import player as Player
from src.game.network import Network
from src.game.weapon import Weapon

wrk_dir = os.path.abspath(os.path.dirname(__file__))
config_file = wrk_dir + r'\configuration.json'
basic_map = wrk_dir + r"\..\basicmap"


class Game:

    def __init__(self, w, h):
        self.net = Network()
        self.width = w
        self.height = h
        self.canvas = canvas.Canvas(self.width, self.height, str(self.net.id) + " Testing...")
        self.map = Map(self, basic_map)
        with open(config_file) as file:
            config = json.load(file)
        if len(self.map.player_uris) == 4:
            self.playerList = [
                Player.Player(config['0']['position'][0], config['0']['position'][1], self, self.map.player_uris[0]),
                Player.Player(config['1']['position'][0], config['1']['position'][1], self, self.map.player_uris[1]),
                Player.Player(config['2']['position'][0], config['2']['position'][1], self, self.map.player_uris[2]),
                Player.Player(config['3']['position'][0], config['3']['position'][1], self, self.map.player_uris[3])]
        else:
            self.playerList = [
                Player.Player(config['0']['position'][0], config['0']['position'][1], self, None, (0, 255, 0)),
                Player.Player(config['1']['position'][0], config['1']['position'][1], self, None, (255, 255, 0)),
                Player.Player(config['2']['position'][0], config['2']['position'][1], self, None, (0, 255, 255)),
                Player.Player(config['3']['position'][0], config['3']['position'][1], self, None, (255, 0, 255))]
        # self.player = Player(50, 50, (0,255,0))
        # self.player2 = Player(100,100, (255,255,0))
        # self.player3 = Player(150,150, (0,255,255))
        # self.player4 = Player(200,200, (255,0,255))

    def run(self):
        clock = pygame.time.Clock()
        run = True

        id = int(self.net.id)
        while run:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.K_ESCAPE:
                    run = False

                # Hit
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if Player can use his weapon
                    if self.playerList[id].weapon.can_hit():
                        # Check if an enemy player is in range
                        for player in self.playerList:
                            #  Do not beat your own player
                            if player == self.playerList[id]:
                                continue
                            # Check if the player was hit
                            # First check if the opponent is in range of the weapon
                            # Then check if the player's mouse is on the opponent
                            if player.x < self.playerList[id].x + self.playerList[id].width + self.playerList[
                                id].weapon.distance \
                                    and player.x + player.width > self.playerList[id].x - self.playerList[
                                id].weapon.distance \
                                    and player.y < self.playerList[id].y + self.playerList[id].height + self.playerList[
                                id].weapon.distance \
                                    and player.y + player.height > self.playerList[id].y - self.playerList[
                                id].weapon.distance \
                                    and player.x < self.playerList[id].mousepos[0] < player.x + player.width \
                                    and player.y < self.playerList[id].mousepos[1] < player.y + player.height:
                                # Draw damage from opponent
                                player.beaten(self.playerList[id].weapon.damage)
                                self.playerList[id].hit()
                                break

            keys = pygame.key.get_pressed()

            if keys[pygame.K_d]:
                self.playerList[id].move(0, self.nextToSolid(self.playerList[id], 0, self.playerList[id].velocity))

            if keys[pygame.K_a]:
                self.playerList[id].move(1, self.nextToSolid(self.playerList[id], 1, self.playerList[id].velocity))

            # Jump
            if keys[pygame.K_SPACE] and self.playerList[id].last_jump + datetime.timedelta(
                    seconds=1) <= datetime.datetime.now() and self.playerList[id].status_jump == 0:
                if self.playerList[id].y >= self.playerList[id].height_jump and self.nextToSolid(self.playerList[id], 3,
                                                                                                 1) < 2:
                    self.playerList[id].jump(10)
                    self.playerList[id].last_jump = datetime.datetime.now()
            if self.playerList[id].status_jump > 0:
                if self.playerList[id].status_jump >= self.playerList[id].height_jump:
                    self.playerList[id].status_jump = 0
                else:
                    self.playerList[id].jump(10)
            # if keys[pygame.K_SPACE]:
            #    if self.playerList[id].y <= self.height - self.playerList[id].velocity - self.playerList[id].height:
            #        self.playerList[id].move(3)
            # grafity
            self.playerList[id].move(3, self.nextToSolid(self.playerList[id], 3, 5))

            # Mouse Postion
            self.playerList[id].mousepos = pygame.mouse.get_pos()

            # Send Data about this player and get some over the others als reply
            reply = self.send_data()
            # synchronise positions
            pos = self.parse_pos(reply)
            for i, position in enumerate(pos):
                self.playerList[i].x, self.playerList[i].y = position
            for p in self.playerList:
                if p == self.playerList[id]:
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

            # Update Canvas
            # self.canvas.draw_background()
            # Draw Map

            # Draw Player
            # self.canvas.draw_background((41, 41, 41))
            self.map.draw(self.canvas.get_canvas())

            for p in self.playerList:
                if p.is_connected:
                    p.draw(self.canvas.get_canvas())
                    pygame.draw.circle(self.canvas.get_canvas(), (255, 0, 0), p.mousepos, 20)

            self.canvas.update()

        pygame.quit()

    def send_data(self):
        """
        Send position to server
        :return: None
        """
        with open(config_file) as file:
            sample = json.load(file)

        data = sample[str(self.net.id)]
        data['id'] = int(self.net.id)
        data['position'] = [int(self.playerList[int(self.net.id)].x), int(self.playerList[int(self.net.id)].y)]
        data['connected'] = True
        data['mouse'] = self.playerList[int(self.net.id)].mousepos
        # data = str(self.net.id) + ":" + str(self.playerList[int(self.net.id)].x) + "," + str(
        #    self.playerList[int(self.net.id)].y)
        # print(json.dumps(data))
        reply = self.net.send(json.dumps(data))
        return reply

    @staticmethod
    def parse_pos(data):
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
        # checking for each pixel if a move ment would cause a collision
        for _ in range(distance):
            Player.Player.shift_df(simulated_player, dirn, 1)
            if not pd.merge(simulated_player, solid_pixels_df, how='inner', on=['x', 'y']).empty:
                return erg
            erg += 1
        return erg
