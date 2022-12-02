import json
import os
from time import sleep
import pygame
import datetime
from network import Network
from pip._internal import configuration

config_file = os.path.abspath(os.path.dirname(__file__)) + '\configuration.json'


class Map():

    def __init__(self, c, w, h, color=(255, 255, 225)):
        self.canvas = c
        self.width = w
        self.height = h
        self.color = color


class Player():
    width, height = 50, 100
    last_jump = datetime.datetime.now()
    height_jump = 500
    status_jump = 0
    is_connected = False
    mousepos = (0, 0)

    def __init__(self, startx, starty, color=(255, 0, 0)):
        self.x = startx
        self.y = starty
        self.velocity = 5
        self.color = color

    def draw(self, g):
        pygame.draw.rect(g, self.color, (self.x, self.y, self.width, self.height), 0)

    def move(self, dirn, v=-99):
        """
        :param dirn: 0 - 3 (right, left, up, down)
        :return: None
        """
        if v == -99:
            v = self.velocity

        if dirn == 0:
            self.x += v
        elif dirn == 1:
            self.x -= v
        elif dirn == 2:
            self.y -= v
        else:
            self.y += v

    def jump(self, h):
        self.move(2, h)
        self.status_jump += h


class Game:

    def __init__(self, w, h):
        self.net = Network()
        self.width = w
        self.height = h
        with open(config_file) as file:
            config = json.load(file)
        self.playerList = [Player(config['0']['position'][0], config['0']['position'][1], (0, 255, 0)),
                           Player(config['1']['position'][0], config['1']['position'][1], (255, 255, 0)),
                           Player(config['2']['position'][0], config['2']['position'][1], (0, 255, 255)),
                           Player(config['3']['position'][0], config['3']['position'][1], (255, 0, 255))]
        # self.player = Player(50, 50, (0,255,0))
        # self.player2 = Player(100,100, (255,255,0))
        # self.player3 = Player(150,150, (0,255,255))
        # self.player4 = Player(200,200, (255,0,255))
        self.canvas = Canvas(self.width, self.height, str(self.net.id) + " Testing...")
        self.map = Map(self.canvas, self.width, self.height, (41, 41, 41))

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
                if self.nextToSolid(self.playerList[id])[1] >= self.playerList[id].velocity:
                    self.playerList[id].move(0)
                elif self.nextToSolid(self.playerList[id])[1] > 0:
                    self.playerList[id].move(0, self.nextToSolid(self.playerList[id])[1])

            if keys[pygame.K_a]:
                if self.nextToSolid(self.playerList[id])[0] >= self.playerList[id].velocity:
                    self.playerList[id].move(1)
                elif self.nextToSolid(self.playerList[id])[0] > 0:
                    self.playerList[id].move(1, self.nextToSolid(self.playerList[id])[0])

            # Jump
            if keys[pygame.K_SPACE] and self.playerList[id].last_jump + datetime.timedelta(
                    seconds=1) <= datetime.datetime.now() and self.playerList[id].status_jump == 0:
                if self.playerList[id].y >= self.playerList[id].height_jump and self.onsolid(self.playerList[id]) == 0:
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
            if self.onsolid(self.playerList[id]) >= 5:
                self.playerList[id].move(3, 5)
            else:
                self.playerList[id].move(3, self.onsolid(self.playerList[id]))

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
            # self.player3.x, self.player3.y = self.parse_data(self.send_data())
            # self.player4.x, self.player3.y = self.parse_data(self.send_data())

            # Update Canvas
            self.canvas.draw_background()
            # Draw Map

            # Draw Player
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

    def colision(self, player, newpos):
        # dist = []
        # Linke Wand
        if newpos[0] < 0: return True
        # Rechte Wand
        if self.width - (player.width + newpos[0]) < 0: return True
        # Distanz zu anderen Spielern
        r1x = newpos[0]
        r1y = newpos[1]
        r1w = player.width
        r1h = player.height
        points = [(r1x, r1y), (r1x + r1w, r1y), (r1x, r1y + r1h), (r1x + r1w, r1y + r1h)]
        player = self.playerList[:int(self.net.id)] + self.playerList[int(self.net.id) + 1:]
        for point in points:
            for p in player:
                if self.pointInRec(point, (p.x, p.y, p.width, p.height)): return True
        return False

    def nextToSolid(self, player):
        # Returns (distance to next left object, distance to next right object)
        ldist = []
        rdist = []
        # distance to left Wall
        ldist.append(player.x)
        # distance to right Wall
        rdist.append(self.width - (player.width + player.x))
        # List of all other Players
        otherPlayers = self.playerList[:int(self.net.id)] + self.playerList[int(self.net.id) + 1:]
        # distances to other players on same level:
        for op in otherPlayers:
            if player.y in range(op.y, op.y + op.height) or player.y + player.height in range(op.y, op.y + op.height):
                ldist.append(player.x - (op.x + op.width))
                rdist.append(op.x - (player.x + player.width))
        ldist = list(filter(lambda x: x >= 0, ldist))
        rdist = list(filter(lambda x: x >= 0, rdist))
        return min(ldist), min(rdist)

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


class Canvas:

    def __init__(self, w, h, name="None"):
        self.width = w
        self.height = h
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption(name)

    @staticmethod
    def update():
        pygame.display.update()

    def draw_text(self, text, size, x, y):
        pygame.font.init()
        font = pygame.font.SysFont("comicsans", size)
        render = font.render(text, 1, (0, 0, 0))

        self.screen.draw(render, (x, y))

    def get_canvas(self):
        return self.screen

    def draw_background(self):
        self.screen.fill((41, 41, 41))
