import os

import pygame

from src.game import game


class Object:

    def __init__(self, c, pos=(0, 0), img=None, size=(1600, 900), color=(255, 255, 225)):
        self.canvas = c
        self.pos = pos
        self.size = size
        try:
            self.ima = pygame.image.load(img).convert_alpha()
        except:
            self.ima = "no image found"  # type: ignore[assignment]
        self.color = color

    def is_coliding(self, point):
        pass

    def draw(self):
        # draw Object
        obj_rec = pygame.Rect(self.pos, self.size)
        if type(self.ima) == pygame.Surface:
            self.canvas.get_canvas().blit(self.ima, obj_rec)
        else:
            pygame.draw.rect(self.canvas.get_canvas(), self.color, obj_rec, 0)
