import os
import re
import pandas as pd

from typing import List, Tuple

import pygame
from PIL import Image
from PIL import GifImagePlugin

wrk_dir = os.path.abspath(os.path.dirname(__file__))
# print(wrk_dir)
# wrk_dir = wrk_dir + r"\..\basicmap\player\basic_player_magenta.png"

wrk_dir = wrk_dir + r"\..\basicmap\player\animation"


class Animated:
    def __init__(self, width, height, startx, starty, directory):
        # self.wrk_dir = os.path.abspath(os.path.dirname(__file__))
        # self.wrk_dir = wrk_dir + r"\..\basicmap\player\animation"
        # self.image = directory + r"\0.png"
        self.width = width
        self.height = height
        self.x = startx
        self.y = starty
        self.image_path = os.path.join(directory + r'/0.png')

        solid = []  # type: List[Tuple[int, int]]
        relativ_solids = []  # type: List[Tuple[int, int]]
        print()

        try:
            self.image = pygame.image.load(self.image_path).convert_alpha()
            # self.image.convert_alpha()
            print("IMAGE FOUND")
            self.edge_surface = pygame.transform.laplacian(self.image).convert_alpha()
            alpha_array = pygame.surfarray.pixels_alpha(self.edge_surface)
            alpha_array = alpha_array.swapaxes(0, 1)
            for yi, y in enumerate(alpha_array):
                for xi, x in enumerate(y):
                    if x > 200:
                        solid.append((xi + self.x, yi + self.y))
                        relativ_solids.append((xi, yi))
        except:
            print("is not image:", self.image)
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

        # self.load_images()

    def draw(self, g):
        """
        displays a player to the canvas
        :param g: pygame canvas
        """
        # draw Player
        player_rec = pygame.Rect(self.x, self.y, self.width, self.height)
        if type(self.image) == pygame.Surface:
            g.blit(self.image, player_rec)
        # else:
        #     pygame.draw.rect(g, self.color, player_rec, 0)

    def load_images(self):
        """
        Loads all images in directory. The directory must only contain images.

        Args:
            path: The relative or absolute path to the directory to load images from.

        Returns:
            List of images.
        """
        if re.match(".*magenta.*", self.image):
            print("magenta")
            path = self.wrk_dir + r"\basic_player_magenta_animation"
            print(path)
        elif re.match(".*orange.*", self.image):
            print("orange")
            path = self.wrk_dir + r"\basic_player_magenta_animation"
        elif re.match(".*purple.*", self.image):
            print("purple")
            path = self.wrk_dir + r"\basic_player_magenta_animation"
        elif re.match(".*turquoise.*", self.image):
            print("turquoise")
            path = self.wrk_dir + r"\basic_player_magenta_animation"
        else:
            print("no player match")

        images = []
        for file_name in os.listdir(path):
            image = pygame.image.load(path + os.sep + file_name).convert()
            images.append(image)
        return images


if __name__ == '__main__':
    print(wrk_dir)
    print([x[0] for x in os.walk(wrk_dir)])

#     def __init__(self, gif):
#         self.gif = gif
#         imageObject = Image.open(self.gif)
#         self.images = list()
#         strFormat = 'RGBA'
#         for frame in range(0, imageObject.n_frames):
#             imageObject.seek(frame)
#             imageObject.show()
#             raw = imageObject.ostring("raw", strFormat)
#             #surface = pygame.image.fromstring(raw, img.size, strFormat).convert_alpha()
#
#         #print(pygame.surfarray.pixels3d(self.images[0]))
