import os
from copy import copy
from typing import List, Tuple

import pandas as pd
import pygame

wrk_dir = os.path.abspath(os.path.dirname(__file__))
wrk_dir = wrk_dir + r"\..\basicmap\player\animation"


class Animated:
    def __init__(self, startx, starty, directory):
        # self.wrk_dir = os.path.abspath(os.path.dirname(__file__))
        # self.wrk_dir = wrk_dir + r"\..\basicmap\player\animation"
        # self.image = directory + r"\0.png"
        self.solid_df = None
        self.relativ_solids_df = None
        self.frame_dfs = list()  # type: List[pd.DataFrame]
        self.relativ_frame_dfs = list()  # type: List[pd.DataFrame]
        self.directory = directory
        self.edge_surface = None
        self.solid = []  # type: List[Tuple[int, int]]
        self.relativ_solids = []  # type: List[Tuple[int, int]]
        # self.current_frame = None
        self.x = startx
        self.y = starty
        self.animation_direction = 1  # 1 mean right, 2 means left
        self.animation_running = False

        self.images_right, self.images_left = self.load_images()

        self.frame_count = len(self.images_right) - 1  # amount of frames of animation, starting at index 0
        self.frame_width = self.images_left[0].get_width()  # width of each frame
        self.frame_height = self.images_left[0].get_height()  # height of each frame
        self.current_frame = 0
        self.frame_dfs, self.relativ_frame_dfs = self.load_dfs()

    def draw(self, **kwargs):
        """
        displays a player to the canvas
        :param g: pygame canvas
        """
        if self.animation_direction == 1:
            self.animate(kwargs["g"], self.images_right)
        else:
            self.animate(kwargs["g"], self.images_left)

    def cut_frames(self, n: int):
        self.images_right = list(x for i, x in enumerate(self.images_right) if i % int(n) == 0)
        self.images_left = list(x for i, x in enumerate(self.images_left) if i % int(n) == 0)
        self.frame_count = len(self.images_right) - 1  # amount of frames of animation, starting at index 0

    def animate(self, g, images):
        player_rec = pygame.Rect(self.x, self.y, self.frame_width, self.frame_height)
        if self.current_frame < self.frame_count and self.animation_running:
            g.blit(images[self.current_frame + 1], player_rec)
            self.current_frame += 1
        else:
            g.blit(images[0], player_rec)
            self.current_frame = 0
            self.animation_running = False

    def stop_animation(self):
        self.animation_running = False

    def set_animation_direction(self, drn):
        self.animation_direction = drn
        self.animation_running = True

    def load_images(self):
        """
        Loads all images in directory. The directory must only contain images.
        Returns:
            List of images.
        """
        images_right: List[pygame.image] = []
        images_left: List[pygame.image] = []

        for filename in sorted(os.listdir(self.directory)):
            if filename[-3:] != 'png':
                print(str(filename) + ' is no png')
                continue
            image_path = self.directory + r"/" + filename
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

    def get_dataframe(self, firstFrame=False):
        if firstFrame:
            return self.solid_df
        else:
            return self.frame_dfs[self.current_frame]

    def get_relativ_dataframe(self, firstFrame=False):
        if firstFrame:
            return self.relativ_frame_dfs[0]
        else:
            return self.relativ_frame_dfs[self.current_frame]

    def load_dfs(self):
        sprite_sheet = self.directory + ".png"
        image = pygame.image.load(sprite_sheet).convert_alpha()
        dfs = list()
        rdfs = list()
        # df = list()
        # rdf = list()
        for i in range(image.get_width() // self.frame_width):
            this_image = pygame.transform.chop(image, (i * self.frame_width, 0, self.frame_width, self.frame_height))
            edge_surface = pygame.transform.laplacian(this_image).convert_alpha()
            alpha_array = pygame.surfarray.pixels_alpha(edge_surface)
            alpha_array = alpha_array.swapaxes(0, 1)
            erg = list()
            erg2 = list()
            for iy, y in enumerate(alpha_array):
                for ix, x in enumerate(y):
                    if x > 100:
                        erg.append((ix + self.x, iy + self.y))
                        erg2.append((ix, iy))
            dfs.append(pd.DataFrame(erg, columns=['x', 'y']))
            rdfs.append(pd.DataFrame(erg2, columns=['x', 'y']))

        return dfs, rdfs
