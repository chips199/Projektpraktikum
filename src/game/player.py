import datetime
from copy import copy
from typing import List, Tuple
import pandas as pd
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

    def __init__(self, startx, starty, game, image=None, color=(255, 0, 0)):
        self.x = startx
        self.y = starty
        self.game = game
        self.velocity = 5
        self.color = color
        self.weapon = weapon
        solid = []  # type: List[Tuple[int, int]]
        relativ_solids = []  # type: List[Tuple[int, int]]
        try:
            self.image = pygame.image.load(image).convert_alpha()
            self.image.convert_alpha()
            self.edge_surface = pygame.transform.laplacian(self.image).convert_alpha()
            alpha_array = pygame.surfarray.pixels_alpha(self.edge_surface)
            alpha_array = alpha_array.swapaxes(0, 1)
            for yi, y in enumerate(alpha_array):
                for xi, x in enumerate(y):
                    if x > 200:
                        solid.append((xi + self.x, yi + self.y))
                        relativ_solids.append((xi, yi))
        except:
            self.image = "no image found"  # type: ignore[assignment]
            # horizontal edges
            for x in range(self.width):
                solid.append((x + self.x, self.y))
                relativ_solids.append((x, self.y))
                solid.append((x + self.x, self.y + self.height))
                relativ_solids.append((x, self.y + self.height))
            # vertical edges
            for y in range(self.height):
                solid.append((self.x, self.y + y))
                relativ_solids.append((self.x, y))
                solid.append((self.x + self.width, self.y + y))
                relativ_solids.append((self.x + self.width, y))
        self.relativ_solids_df = pd.DataFrame(relativ_solids, columns=['x', 'y'])
        self.solid_df = pd.DataFrame(solid, columns=['x', 'y'])

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

    @staticmethod
    def shift_df(df, dirn, n):
        """
        "moves" dataframe of coordinates
        :param df: dataframe
        :param dirn: direction
        :param n: distance
        :return: new dataframe
        """
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

        if dirn == 0:
            self.x += v
        elif dirn == 1:
            self.x -= v
        elif dirn == 2:
            self.y -= v
        else:
            self.y += v
        self.solid_df = Player.shift_df(self.solid_df, dirn, v)

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
        new_pos = copy(self.relativ_solids_df)
        new_pos['x'] = new_pos['x'].map(lambda x: x + self.x)
        new_pos['y'] = new_pos['y'].map(lambda y: y + self.y)
        self.solid_df = new_pos
