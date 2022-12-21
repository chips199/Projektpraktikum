import datetime
from typing import List, Tuple

import numpy as np
import pygame

import weapon


class Player():
    width, height = 50, 100
    solid = list()  # type: List[Tuple[int, int]]
    last_jump = datetime.datetime.now()
    height_jump = 500
    status_jump = 0
    is_connected = False
    mousepos = (0, 0)
    weapon = weapon.Weapon(100, 10, 10, 100)
    health = 100

    def __init__(self, startx, starty, image=None, color=(255, 0, 0)):
        self.x = startx
        self.y = starty
        self.velocity = 5
        self.color = color
        self.weapon = weapon
        if image is not None:
            try:
                self.image = pygame.image.load(image).convert_alpha()
                solid_image = self.image.copy()
                solid_image.convert_alpha()
                edge_surface = pygame.transform.laplacian(solid_image).convert_alpha()
                alpha_array = pygame.surfarray.pixels_alpha(edge_surface)
                alpha_array.swapaxes(0, 1)
                for yi, y in enumerate(alpha_array):
                    for xi, x in enumerate(y):
                        # print(e1)
                        if x > 200:
                            self.solid.append((xi + self.x, yi + self.y))
            except:
                self.image = "no image found"
                # horizontal edges
                for x in range(self.width):
                    self.solid.append((x + self.x, self.y))
                    self.solid.append((x + self.x, self.y + self.height))
                # vertical edges
                for y in range(self.height):
                    self.solid.append((self.x, self.y + y))
                    self.solid.append((self.x + self.width, self.y + y))

    def draw(self, g):
        # draw Player
        player_rec = pygame.Rect(self.x, self.y, self.width, self.height)
        if type(self.image) == pygame.Surface:
            g.blit(self.image, player_rec)
        else:
            pygame.draw.rect(g, self.color, player_rec, 0)

        # draw weapon
        # ...


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

        # move solid pixels
        self.solid = list(map(lambda p: (p[0] + delta_x, p[1] + delta_y), self.solid))

    def colides(self, edge_array):
        # checks if a list of pixels intersects with the list of solid pixels of the player
        a = self.solid
        b = edge_array
        a = list(map(lambda x: str(x[0]) + str(x[1]), a))
        b = list(map(lambda x: str(x[0]) + str(x[1]), b))
        return len(np.intersect1d(a, b)) != 0

    def jump(self, h):
        self.move(2, h)
        self.status_jump += h

    def hit(self):
        self.weapon.durability -= 1

    def beaten(self, weapon_enemy):
        self.health -= weapon_enemy.damage
