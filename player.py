import datetime

import pygame


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

