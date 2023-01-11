import datetime
from itertools import repeat
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pygame

import weapon
import src.game.game as Game


class Player():
    width, height = 50, 100
    last_jump = datetime.datetime.now()
    height_jump = 200
    status_jump = 0
    is_connected = False
    mousepos = (0, 0)
    weapon = weapon.Weapon(100, 10, 10, 100)
    health = 100

    def __init__(self, startx, starty, game, image=None, color=(255, 0, 0)):
        self.x = startx
        self.y = starty
        self.game = game
        self.velocity = 5
        self.color = color
        self.weapon = weapon
        self.solid = []  # type: List[Tuple[int, int]]
        self.relativ_solids = []
        if image is not None and len(self.solid) == 0:
            try:
                self.image = pygame.image.load(image).convert_alpha()
                self.image.convert_alpha()
                self.edge_surface = pygame.transform.laplacian(self.image).convert_alpha()
                alpha_array = pygame.surfarray.pixels_alpha(self.edge_surface)
                alpha_array = alpha_array.swapaxes(0, 1)
                for yi, y in enumerate(alpha_array):
                    for xi, x in enumerate(y):
                        # print(e1)
                        if x > 200:
                            # print((xi + self.x, yi + self.y))
                            self.solid.append((xi + self.x, yi + self.y))
                            self.relativ_solids.append((xi, yi))
            except:
                self.image = "no image found"  # type: ignore[assignment]
                # horizontal edges
                for x in range(self.width):
                    self.solid.append((x + self.x, self.y))
                    self.relativ_solids.append((x, self.y))
                    self.solid.append((x + self.x, self.y + self.height))
                    self.relativ_solids.append((x, self.y + self.height))
                # vertical edges
                for y in range(self.height):
                    self.solid.append((self.x, self.y + y))
                    self.relativ_solids.append((self.x, y))
                    self.solid.append((self.x + self.width, self.y + y))
                    self.relativ_solids.append((self.x + self.width, y))
        else:
            self.image = "no image found"  # type: ignore[assignment]
            # horizontal edges
            for x in range(self.width):
                self.solid.append((x + self.x, self.y))
                self.relativ_solids.append((x, self.y))
                self.solid.append((x + self.x, self.y + self.height))
                self.relativ_solids.append((x, self.y + self.height))
            # vertical edges
            for y in range(self.height):
                self.solid.append((self.x, self.y + y))
                self.relativ_solids.append((self.x, y))
                self.solid.append((self.x + self.width, self.y + y))
                self.relativ_solids.append((self.x + self.width, y))
        self.solid_df = pd.DataFrame(self.solid, columns=['x', 'y'])

    def draw(self, g):
        # draw Player
        player_rec = pygame.Rect(self.x, self.y, self.width, self.height)
        if type(self.image) == pygame.Surface:
            g.blit(self.image, player_rec)
            # g.blit(self.edge_surface, player_rec)
        else:
            pygame.draw.rect(g, self.color, player_rec, 0)

        # draw weapon
        # ...

    @staticmethod
    def shift_df(df, dirn, n):
        if dirn == 0:
            df['x'] = df['x'].map(lambda x: x + n)
        elif dirn == 1:
            df['x'] = df['x'].map(lambda x: x - n)
        elif dirn == 2:
            df['y'] = df['y'].map(lambda y: y - n)
        else:
            df['y'] = df['y'].map(lambda y: y + n)
        return df

    def move(self, dirn, v=-99):
        """
        :param dirn: 0 - 3 (right, left, up, down)
        :return: None
        """
        if v == -99:
            v = self.velocity

        delta_x = 0
        delta_y = 0

        if dirn == 0:
            self.x += v
            delta_x += v
        elif dirn == 1:
            self.x -= v
            delta_x -= v
        elif dirn == 2:
            self.y -= v
            delta_y -= v
        else:
            self.y += v
            delta_y += v
        self.solid_df = Player.shift_df(self.solid_df, dirn, v)
        return

        # move solid pixels
        self.solid = list(map(lambda p: (p[0] + delta_x, p[1] + delta_y), self.solid))
        self.solid_df['x'] = self.solid_df['x'].map(lambda x: x + delta_x)
        self.solid_df['y'] = self.solid_df['y'].map(lambda y: y + delta_y)

    def colides(self, edge_array):
        """
        intersects the given dataframe with the dataframe of this instance
        :param edge_array: dataframne
        :return: boolean
        """
        return not pd.merge(self.solid_df, edge_array, how='inner', on=['x', 'y']).empty

        # checks if a list of pixels intersects with the list of solid pixels of the player
        a = self.solid
        b = edge_array
        # c = list(map(lambda x: str(x[0]) + ',' + str(x[1]), a))
        # d = list(map(lambda x: str(x[0]) + ',' + str(x[1]), b))
        c = list(map(Game.Game.coordToDezimal, a, repeat(self.game.width)))
        d = list(map(Game.Game.coordToDezimal, b, repeat(self.game.width)))
        return len(np.intersect1d(c, d)) != 0

    def jump(self, h):
        self.move(2, h)
        self.status_jump += h

    def hit(self):
        self.weapon.durability -= 1

    def beaten(self, weapon_enemy):
        self.health -= weapon_enemy.damage

    def refresh_solids(self):
        # self.solid = list(map(lambda p: (p[0] + self.x, p[1] + self.y), self.relativ_solids))
        self.solid_df = pd.DataFrame(list(map(lambda p: (p[0] + self.x, p[1] + self.y), self.relativ_solids)), columns=['x', 'y'])
