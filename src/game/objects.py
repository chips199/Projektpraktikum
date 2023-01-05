import os

import pygame

from src.game import game
import imageio.v3 as iio


class Object:

    def __init__(self, c, pos=(0, 0), img=None, size=(1600, 900), color=(255, 255, 225)):
        self.canvas = c
        self.pos = pos
        self.size = size
        try:
            self.ima = pygame.image.load(img).convert_alpha()
        except:
            self.img = pygame.Rect(self.pos, self.size) # type: ignore[assignment]
        self.color = color

    def is_coliding(self, point):
        pass

    def draw(self):
        if type(self.img) == pygame.Surface:
            self.canvas.get_canvas().blit(self.image, player_rec)
        else:
            pygame.draw.rect(self.canvas, self.color, self.img)
