import json
import os
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
map_names_dict = {"basicmap": basic_map}


class Game:

    def __init__(self, w, h, net):
        self.net = net
        self.width = w
        self.height = h
        self.canvas = canvas.Canvas(self.width, self.height, str(self.net.id) + " Testing...")
        self.map = Map(self, map_names_dict[net.map_name])
        with open(config_file) as file:
            config = json.load(file)
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

            if self.playerList[id].is_alive():
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

                keys = pygame.key.get_pressed()

                if keys[pygame.K_d]:
                    self.playerList[id].move(0, self.nextToSolid(self.playerList[id], 0, self.playerList[id].velocity))

                if keys[pygame.K_a]:
                    self.playerList[id].move(1, self.nextToSolid(self.playerList[id], 1, self.playerList[id].velocity))

                # Jump
                if keys[pygame.K_SPACE] and self.playerList[id].last_jump + datetime.timedelta(
                        seconds=1) <= datetime.datetime.now() and self.playerList[id].status_jump == 0:
                    if self.playerList[id].y >= self.playerList[id].height_jump and self.nextToSolid(
                            self.playerList[id], 3,
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

            # Mouse Position
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

    def collision_with_other_players(self, point):
        # checks if a point collides with any other player
        otherPlayers = self.playerList[:int(self.net.id)] + self.playerList[int(self.net.id) + 1:]
        for p in otherPlayers:
            rec = pygame.Rect(p.x, p.y, p.width, p.height)
            if rec.collidepoint(point):
                return True
        return False

    def nextToSolid(self, player, dirn, distance):
        other_players = self.playerList[:int(self.net.id)] + self.playerList[int(self.net.id) + 1:]
        simulated_solid = player.solid.copy()
        erg = 0
        for i in range(distance):
            v = 1
            delta_x = 0
            delta_y = 0
            if dirn == 0:
                delta_x += v
            elif dirn == 1:
                delta_x -= v
            elif dirn == 2:
                delta_y -= v
            else:
                delta_y += v
            simulated_solid = list(map(lambda p: (p[0] + delta_x, p[1] + delta_y), simulated_solid))
            if self.map.colides(simulated_solid):
                # print('map colision')
                return erg
            for p in other_players:
                if p.colides(simulated_solid):
                    # print('player colision')
                    return erg
            erg += 1
        return erg

    def nextToSolid1(self, player, dirn, distance):
        # checks in a direction for each pixel of the distance for collision and returns the remaining distance
        # only check the direction in which the player wants to move
        top_left = [player.x, player.y]
        top_right = [player.x + player.width, player.y]
        bottem_left = [player.x, player.y + player.width]
        bottem_right = [player.x + player.width, player.y + player.height]
        erg = 0
        if dirn == 0:
            # right
            for i in range(distance):
                top_right[0] += 1
                bottem_right[0] += 1
                if self.collision_with_other_players(top_right):
                    return erg
                if self.collision_with_other_players(bottem_right):
                    return erg
                # if self.map.is_coliding(top_right):
                #    return erg
                # if self.map.is_coliding(bottem_right):
                #    return erg
                erg += 1
        elif dirn == 1:
            # left
            for i in range(distance):
                top_left[0] -= 1
                bottem_left[0] -= 1
                if self.collision_with_other_players(top_left):
                    return erg
                if self.collision_with_other_players(bottem_left):
                    return erg
                if self.map.is_coliding(top_left):
                    return erg
                if self.map.is_coliding(bottem_left):
                    return erg
                erg += 1
        elif dirn == 2:
            # down
            for i in range(distance):
                top_left[1] -= 1
                top_right[1] -= 1
                if self.collision_with_other_players(top_left):
                    return erg
                if self.collision_with_other_players(top_right):
                    return erg
                if self.map.is_coliding(top_left):
                    return erg
                if self.map.is_coliding(top_right):
                    return erg
                erg += 1
        else:
            # up
            for i in range(distance):
                bottem_left[1] += 1
                bottem_right[1] += 1
                if self.collision_with_other_players(bottem_left):
                    return erg
                if self.collision_with_other_players(bottem_right):
                    return erg
                if self.map.is_coliding(bottem_left):
                    return erg
                if self.map.is_coliding(bottem_right):
                    return erg
                erg += 1
        return erg

    def onsolid(self, player):
        dist = []
        # steht auf boden?
        dist.append(self.height - player.height - player.y)
        # Steht auf anderem Spieler?
        for p in self.playerList:
            if player.x in range(p.x, p.x + p.width) or player.x + player.width in range(p.x, p.x + p.width):
                dist.append(p.y - player.y - player.height)
        dist = list(filter(lambda x: x >= 0, dist))
        return min(dist)
