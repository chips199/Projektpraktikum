from copy import copy

import pandas as pd
import pygame


import player


class WeaponShot:
    def __init__(self, pos, velocity, color, direction):
        """
        pygame.Color(231, 24, 55)
        param: direction: +1 --> left, -1 --> right
        """
        self.x, self.y = pos
        self.velocity = velocity
        self.color = color
        self.height = 2
        self.width = 10
        self.direction = direction
        solid = []
        for x in range(self.width):
            solid.append((x, 0))
            solid.append((x, self.height - 1))
        for y in range(self.height):
            solid.append((0, y))
            solid.append((self.width, y))
        self.solid_df = pd.DataFrame(solid, columns=["x", "y"])

    def get_dataframe(self):
        df = copy(self.solid_df)
        if self.direction == -1:
            df['x'] = df['x'].map(lambda x: x + self.x - self.width)
            df['y'] = df['y'].map(lambda y: y + self.y - self.height / 2)
        else:
            df['x'] = df['x'].map(lambda x: x + self.x)
            df['y'] = df['y'].map(lambda y: y + self.y - self.height / 2)

    def move(self):

    def draw(self, g):
        pygame.draw.line(surface=g,
                         color=self.color,
                         start_pos=(self.x, self.y + self.height / 2),
                         end_pos=(self.x + self.width * self.direction, self.y - self.height),
                         width=self.height)
