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
        self.directory = directory
        self.solid_df = None
        self.relativ_solids_df = None
        self.edge_surface = None
        self.solid = []  # type: List[Tuple[int, int]]
        self.relativ_solids = []  # type: List[Tuple[int, int]]
        self.current_frame = None
        self.width = width
        self.height = height
        self.x = startx
        self.y = starty
        # self.do_animation_right = False
        # self.do_animation_left = False
        self.animation_direction = 1  # 1 mean right, 2 means left
        self.animation_running = False
        # self.image_path = os.path.join(directory + r'/0.png')

        self.images_right, self.images_left = self.load_images()
        self.images_right = list(x for i, x in enumerate(self.images_right) if i % 2 == 0)
        self.images_left = list(x for i, x in enumerate(self.images_left) if i % 2 == 0)

        print(len(self.images_right))

        self.frame_count = len(self.images_right) - 1  # amount of frames of animation, starting at index 0
        self.current_frame = 0

    def draw(self, g):
        """
        displays a player to the canvas
        :param g: pygame canvas
        """
        if self.animation_direction == 1:
            self.animate(g, self.images_right)
        else:
            self.animate(g, self.images_left)
        # draw Player
        # player_rec = pygame.Rect(self.x, self.y, self.width, self.height)
        # if self.current_frame < self.frame_count and self.animation_running:
        #     if self.do_animation_right:
        #         g.blit(self.images_right[self.current_frame + 1], player_rec)
        #     else:
        #         g.blit(self.images_left[self.current_frame + 1], player_rec)
        #     self.current_frame += 1
        # else:
        #     g.blit(self.images_right[0], player_rec)
        #     self.current_frame = 0
        #     self.animation_running = False

    def animate(self, g, images):
        player_rec = pygame.Rect(self.x, self.y, self.width, self.height)
        if self.current_frame < self.frame_count and self.animation_running:
            g.blit(images[self.current_frame + 1], player_rec)
            self.current_frame += 1
        else:
            g.blit(images[0], player_rec)
            self.current_frame = 0
            self.animation_running = False

    def stop_animation(self):
        self.animation_running = False

    def set_animation_direction(self, direction: int = 1):
        self.animation_direction = direction
        self.animation_running = True

    def load_images(self):
        """
        Loads all images in directory. The directory must only contain images.
        Returns:
            List of images.
        """
        images_right = []
        images_left = []

        for filename in sorted(os.listdir(self.directory)):
            print(filename)
            if filename[-3:] != 'png':
                print(str(filename) + ' is no png')
                continue
            # image_path = os.path.join(self.directory + filename)
            image_path = self.directory + r"/" + filename
            # print(image_path)
            try:
                image = pygame.image.load(image_path).convert_alpha()
                if len(images_right) == 0:
                    self.edge_surface = pygame.transform.laplacian(image).convert_alpha()
                    alpha_array = pygame.surfarray.pixels_alpha(self.edge_surface)
                    alpha_array = alpha_array.swapaxes(0, 1)
                    for yi, y in enumerate(alpha_array):
                        for xi, x in enumerate(y):
                            if x > 200:
                                self.solid.append((xi + self.x, yi + self.y))
                                self.relativ_solids.append((xi, yi))
                images_right.append(image)
                images_left.append(pygame.transform.flip(image, True, False))
            except:
                print("is not image:", images_right)
        self.relativ_solids_df = pd.DataFrame(self.relativ_solids, columns=['x', 'y'])
        self.solid_df = pd.DataFrame(self.solid, columns=['x', 'y'])
        return images_right, images_left


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
