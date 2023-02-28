from copy import copy

import pandas as pd
import pygame

from src.game.gamelogic import animated


class WeaponShot:
    def __init__(self, pos, velocity, color, direction, damage):
        """
        pygame.Color(231, 24, 55)
        param: direction: +1, -1 (left, right)
        """
        self.x, self.y = pos
        self.velocity = velocity
        self.color = color
        self.height = 4
        self.width = 20
        self.direction = direction
        self.damage = damage
        solid = []
        for x in range(self.width):
            solid.append((x, 0))
            solid.append((x, self.height - 1))
        for y in range(self.height):
            solid.append((0, y))
            solid.append((self.width, y))
        self.solid_df = pd.DataFrame(solid, columns=["x", "y"])

    def get_dataframe(self):
        """
        returns the data frame of the shot
        """
        df = copy(self.solid_df)
        if self.direction == -1:
            df['x'] = df['x'].map(lambda x: x + self.x - self.width)
            df['y'] = df['y'].map(lambda y: y + self.y - self.height / 2)
        else:
            df['x'] = df['x'].map(lambda x: x + self.x)
            df['y'] = df['y'].map(lambda y: y + self.y - self.height / 2)

    def move(self, direction, velocity=-99):
        """
        Moves the shot object
        param: direction: +1, -1 (left, right)
        param: velocity: velocity of the shot
        """
        if velocity == -99:
            velocity = self.velocity

        self.x += direction * velocity
        # Shift dataframe
        self.solid_df = animated.shift_df(self.solid_df, direction, velocity)

    def draw(self, g):
        """
        Draws the shot as a line on the canvas
        """
        # shift the shot when shooting to the left
        direction_left_shift = 0
        if self.direction == -1:
            direction_left_shift = self.width
        # Draw the shot
        pygame.draw.rect(surface=g,
                         color=self.color,
                         rect=[self.x - direction_left_shift, self.y + self.height / 2, self.width, self.height],
                         width=0)

    def is_active(self):
        """
        Returns whether the shot is still active or has already hit something
        """
        return self.direction != 0
