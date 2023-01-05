import datetime
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pygame

import weapon


class Player():
    width, height = 50, 100
    last_jump = datetime.datetime.now()
    height_jump = 200
    status_jump = 0
    is_connected = False
    mousepos = (0, 0)
    user_weapon = weapon.Weapon(100, 15, 15, 1)
    health = 100

    def __init__(self, startx, starty, image=None, color=(255, 0, 0)):
        self.x = startx
        self.y = starty
        self.velocity = 5
        self.color = color
        self.solid = []  # type: List[Tuple[int, int]]
        self.relativ_solids = []
        print(len(self.solid))
        if image is not None and len(self.solid) == 0:
            try:
                self.image = pygame.image.load(image).convert_alpha()
                self.image.convert_alpha()
                self.edge_surface = pygame.transform.laplacian(self.image).convert_alpha()
                alpha_array = pygame.surfarray.pixels_alpha(self.edge_surface)
                alpha_array = alpha_array.swapaxes(0, 1)
                for yi, y in enumerate(alpha_array):
                    for xi, x in enumerate(y):
                        if x > 200:
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

    def draw(self, g):
        """
        displays a player to the canvas
        :param g: pygame canvas
        """
        # draw Player
        player_rec = pygame.Rect(self.x, self.y, self.width, self.height)
        if type(self.image) == pygame.Surface:
            g.blit(self.image, player_rec)
        else:
            pygame.draw.rect(g, self.color, player_rec, 0)

        # draw weapon
        # ...wip...

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
        """
        checks if a list of pixels intersects with the list of solid pixels of the player
        :param edge_array:  list of tupels
        :return: boolean if collides then true
        """
        a = self.solid
        b = edge_array
        c = list(map(lambda x: str(x[0]) + ',' + str(x[1]), a))
        d = list(map(lambda x: str(x[0]) + ',' + str(x[1]), b))
        return len(np.intersect1d(c, d)) != 0

    def jump(self, h):
        """
        moves player upwards
        :param h: hight of the jump
        """
        self.move(2, h)
        self.status_jump += h

    def beaten(self, weapon_enemy):
        """
        player was beaten
        player is subtracted the damage of the weapon and it is checked if the player died during the attack
        :param weapon_enemy The weapon with which the player was hit
        :return None
        """
        self.health -= weapon_enemy.damage
        if self.health <= 0:
            print("Player died")
            # TODO: Anzeige auf Screen und Spieler ausblenden?
            self.health = 0

    def is_alive(self):
        """
        Returns whether the player is still alive
        :return: boolean: True: Is alive;  False: Isn't alive
        """
        return self.health > 0

    def refresh_solids(self):
        """
        refreshes the solid list used when receiving player positions from server
        """
        self.solid = list(map(lambda p: (p[0] + self.x, p[1] + self.y), self.relativ_solids))
