import json
import os
from time import sleep
import pygame
import datetime
import player as Player
import canvas
from map import Map
from network import Network
from pip._internal import configuration

wrk_dir = os.path.abspath(os.path.dirname(__file__))
config_file = wrk_dir + r'\configuration.json'
test_map = wrk_dir + r"\src\testmap"
basic_map = wrk_dir + r"\src\basicmap"

class Game:

    def __init__(self, w, h):
        self.net = Network()
        self.width = w
        self.height = h
        with open(config_file) as file:
            config = json.load(file)
        self.playerList = [Player.Player(config['0']['position'][0], config['0']['position'][1], (0, 255, 0)),
                           Player.Player(config['1']['position'][0], config['1']['position'][1], (255, 255, 0)),
                           Player.Player(config['2']['position'][0], config['2']['position'][1], (0, 255, 255)),
                           Player.Player(config['3']['position'][0], config['3']['position'][1], (255, 0, 255))]
        # self.player = Player(50, 50, (0,255,0))
        # self.player2 = Player(100,100, (255,255,0))
        # self.player3 = Player(150,150, (0,255,255))
        # self.player4 = Player(200,200, (255,0,255))
        self.canvas = canvas.Canvas(self.width, self.height, str(self.net.id) + " Testing...")
        self.map = Map(self, basic_map)

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

            keys = pygame.key.get_pressed()

            if keys[pygame.K_d]:
                self.playerList[id].move(0, self.nextToSolid(self.playerList[id], 0, self.playerList[id].velocity))

            if keys[pygame.K_a]:
                self.playerList[id].move(1, self.nextToSolid(self.playerList[id], 1, self.playerList[id].velocity))

            # Jump
            if keys[pygame.K_SPACE] and self.playerList[id].last_jump + datetime.timedelta(
                    seconds=1) <= datetime.datetime.now() and self.playerList[id].status_jump == 0:
                if self.playerList[id].y >= self.playerList[id].height_jump and self.nextToSolid(self.playerList[id], 3,
                                                                                                 1) == 0:
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

    def pointInRec(self, point, p):
        x1, y1, w, h = p
        x2, y2 = x1 + w, y1 + h
        x, y = point
        if x in range(x1, x2):
            if y in range(y1, y2):
                return True
        return False

    def collision_with_other_players(self, point):
        # checks if a point collides with any other player
        otherPlayers = self.playerList[:int(self.net.id)] + self.playerList[int(self.net.id) + 1:]
        for p in otherPlayers:
            rec = pygame.Rect(p.x, p.y, p.width, p.height)
            if rec.collidepoint(point):
                return True
        return False

    def nextToSolid(self, player, dirn, distance):
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
                #if self.map.is_coliding(top_right):
                #    return erg
                #if self.map.is_coliding(bottem_right):
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



