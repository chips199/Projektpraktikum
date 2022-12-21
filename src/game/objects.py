import os

import pygame

from src.game import game
import imageio.v3 as iio


class Object:

    def __init__(self, c, pos=(0, 0), img=None, size=(1600, 900), color=(255, 255, 225)):
        self.canvas = c
        self.pos = pos
        self.size = size
        if (img is not None):
            try:
                self.img = iio.imread(img)
            except:
                self.img = iio.imread(os.path.abspath(os.path.dirname(__file__)) + r'\ImgNotFound.png')
        else:
            self.img = pygame.Rect(self.pos, self.size)
        self.color = color

    def is_coliding(self, point):
        pass

    def draw(self):
        if type(self.img) == pygame.Rect:
            pygame.draw.rect(self.canvas, self.color, self.img)
        else:
            print('Noch keine Ahnung wie das geht')