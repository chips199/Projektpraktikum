from typing import Union

import pandas as pd
import pygame.image


class Item:
    def __init__(self, weapontype: str, pos: tuple[int, int], img: str) -> None:
        """
        Initialize a weapon object

        :param weapontype: Type of weapon as string
        :param pos: Starting position of weapon in form of (x, y) tuple
        :param img: Path to image file
        """
        # Set weapon type
        self.type = weapontype
        # Load image and set weapon position
        self.img = pygame.image.load(img).convert_alpha()
        self.x, self.y = pos

        # Create solid dataframe for collision detection
        edge_surface = pygame.transform.laplacian(self.img).convert_alpha()
        alpha_array = pygame.surfarray.pixels_alpha(edge_surface)
        alpha_array = alpha_array.swapaxes(0, 1)
        solid = list()
        for yi, y in enumerate(alpha_array):
            for xi, x in enumerate(y):
                if x > 100:
                    solid.append((xi + self.x, yi + self.y))
        self.solid_df = pd.DataFrame(solid, columns=['x', 'y'])

    def getItem(self, df: pd.DataFrame, wt: str) -> Union[str, None]:
        """
        Check if the item can be picked up or not

        :param df: Dataframe containing the coordinates of items on the screen
        :param wt: Type of the item to pick up
        :return: Type of the item to pick up, or None if it can't be picked up
        """
        # Check if the current item can be picked up by comparing its type and the type of the player
        if not pd.merge(self.solid_df, df, how='inner', on=['x', 'y']).empty and wt != self.type:
            return self.type
        # If the item can't be picked up, return None
        return None

    def draw(self, g: pygame.Surface) -> None:
        """
        Draws the object onto a given Pygame surface

        :param g: The Pygame surface onto which to draw the object
        """
        # Create a new rectangle with the same size and position as the image
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        # Draw the image onto the surface using the rectangle as a position and size
        g.blit(self.img, rect)
