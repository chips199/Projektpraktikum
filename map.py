import imageio.v3 as iio
import os
import matplotlib.pyplot as plt
import pygame
import game
from functools import reduce
from operator import add
from _thread import *


class Map():
    solid = list()
    solid_x_splited = list()
    solid_y_splited = list()
    staticimages = list()

    def __init__(self, game, uri):
        self.game = game
        self.directory = uri
        # load background
        try:
            self.background = pygame.image.load(uri + r'\background.png')
            self.background.convert()
        except:
            self.background = None

        # load solid images and add solid pixels to list
        # print(self.directory + r'\solid')
        for filename in os.listdir(self.directory + r'\solid'):
            simg = os.path.join(self.directory + r'\solid', filename)
            if not os.path.isfile(simg):
                print(str(simg) + ' is not a file')
                continue

            # load image for displaying
            try:
                img = pygame.image.load(simg)
                self.staticimages.append(img)
            except:
                continue

            # add solid Pixels
            # col_img = iio.imread(simg)
            col_img = pygame.surfarray.array_alpha(img)
            col_img = col_img.swapaxes(0, 1)
            col_img = list(col_img)
            # print(col_img)
            # t = list(map(add, col_img))
            for yi, y in enumerate(col_img):
                for xi, x in enumerate(y):
                    # print(x)
                    if x >= 100:
                        self.solid.append((xi, yi))

        # load unsolid images
        for filename in os.listdir(self.directory + r'\not_solid'):
            nsimg = os.path.join(self.directory + r'\not_solid', filename)
            if not os.path.isfile(nsimg):
                print(str(nsimg) + ' is not a file')
                continue

            # load image for displaying
            try:
                img = pygame.image.load(nsimg)
            except:
                continue

            print(str(nsimg) + ' erfolgreich in pygame geladen')
            self.staticimages.append(img)

        # combine all images for faster refreshrates
        if self.background is not None:
            self.arena_img = self.background.copy()
            self.arena_img.convert_alpha()
            for simg in self.staticimages:
                simg.convert_alpha()
                self.arena_img.blit(simg, (0, 0))
            self.arena_img.convert_alpha()

        # generate splited lists
        self.solid_x_splited = [list() for x in range(self.game.width // 10)]
        self.solid_y_splited = [list() for x in range(self.game.height // 10)]
        for i, point in enumerate(self.solid):
            self.solid_x_splited[(point[0] // 10)].append(i)
            self.solid_y_splited[(point[1] // 10)].append(i)
        # print(self.solid_x_splited[159])

    def is_coliding(self, p):
        # x Group
        if p[0] not in range(self.game.width) or p[1] not in range(self.game.height):
            return True
        x_ps = self.solid_x_splited[p[0] // 10]
        # y Group
        y_ps = self.solid_y_splited[p[1] // 10]
        # Intersektion of the two groups provides max 100 points to check
        candidates = set(x_ps).intersection(set(y_ps))
        # print(candidates)
        for i in list(candidates):
            # print(self.solid[i])
            if self.solid[i][0] == p[0] and self.solid[i][1] == p[1]:
                # returns True when Point inside solid Object
                return True
        # returns True when point outside Gamearea
        return not game.Game.pointInRec(p, (0, 0, self.game.width, self.game.height))
        # return not pygame.Rect(0, 0, self.game.width, self.game.height).collidepoint(p)

    def draw(self, screen):
        canvas_rec = pygame.Rect(0, 0, self.game.width, self.game.height)
        if self.arena_img is not None:
            screen.blit(self.arena_img, canvas_rec)
        else:
            screen.fill((41, 41, 41))

        # for img in self.staticimages:
        #    screen.blit(img, canvas_rec)
