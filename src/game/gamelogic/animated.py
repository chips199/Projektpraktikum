import os
from copy import copy
from typing import List, Tuple

import pandas as pd
import pygame

wrk_dir = os.path.abspath(os.path.dirname(__file__))
wrk_dir = wrk_dir + r"\..\basicmap\player\animation"


class Animated:
    def __init__(self, start, directory):
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
        self.x = start[0]
        self.y = start[1]
        self.scale = 0.8
        self.animation_direction = 0  # 0 mean right, 1 means left
        self.animation_running = False

        self.images_right, self.images_left = self.load_images()

        self.frame_count = len(self.images_right) - 1  # amount of frames of animation, starting at index 0
        self.frame_width = self.images_left[0].get_width()  # width of each frame
        self.frame_height = self.images_left[0].get_height()  # height of each frame
        self.current_frame = 0

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def draw(self, **kwargs):
        """
        displays a player to the canvas
        :param g: pygame canvas
        """
        if self.animation_direction == 0:
            self.animate(kwargs["g"], self.images_right)
        else:
            self.animate(kwargs["g"], self.images_left)

    def cut_frames(self, n: int):
        self.images_right = list(x for i, x in enumerate(self.images_right) if i % int(n) == 0)
        self.images_left = list(x for i, x in enumerate(self.images_left) if i % int(n) == 0)
        self.frame_count = len(self.images_right) - 1  # amount of frames of animation, starting at index 0

    def double_frames(self, factor: int):
        copy_right = self.images_right[:]
        copy_left = self.images_left[:]
        for index, (image_right, image_left) in reversed(list(enumerate(zip(copy_right, copy_left)))):
            for _ in range(factor):
                self.images_right.insert(index, image_right)
                self.images_left.insert(index, image_left)
        self.frame_count = len(self.images_right) - 1

    def animate(self, g, images):
        player_rec = pygame.Rect(self.x, self.y, self.frame_width, self.frame_height)
        if self.current_frame < self.frame_count and self.animation_running:
            g.blit(images[self.current_frame + 1], player_rec)
            self.current_frame += 1
        else:
            g.blit(images[0], player_rec)
            self.current_frame = 0
            self.animation_running = False

    def draw_animation_once(self, g, reset=False, direction=None):

        if self.current_frame < self.frame_count:
            self.animation_running = True
            self.draw(g=g)
        else:
            self.animation_running = False
            if reset:
                self.current_frame = 0

    def stop_animation(self):
        self.animation_running = False

    def start_animation_in_direction(self, direction):
        self.animation_direction = direction
        self.animation_running = True

    def load_images(self):
        """
        Loads all images in directory. The directory must only contain images.
        Returns:
            List of images.
        """
        images_right = []  # type:ignore[var-annotated]
        images_left = []

        for filename in sorted(os.listdir(self.directory)):
            if filename[-3:] != 'png':
                print(str(filename) + ' is no png')
                continue
            image_path = self.directory + r"/" + filename
            try:
                image = pygame.image.load(image_path).convert_alpha()
                image = pygame.transform.scale(image, (image.get_width() * self.scale, image.get_height() * self.scale))
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

    def load_dfs(self):
        rel_l = list()
        rel_r = list()
        abs_l = list()
        abs_r = list()
        for il in self.images_left:
            aa = pygame.surfarray.pixels_alpha(pygame.transform.laplacian(il)).swapaxes(0, 1)
            relativ = list()
            absolut = list()
            for iy, y in enumerate(aa):
                for ix, x in enumerate(y):
                    if x > 100:
                        absolut.append((ix + self.x, iy + self.y))
                        relativ.append((ix, iy))
            abs_l.append(pd.DataFrame(absolut, columns=['x', 'y']))
            rel_l.append(pd.DataFrame(relativ, columns=['x', 'y']))

        for ir in self.images_right:
            aa = pygame.surfarray.pixels_alpha(pygame.transform.laplacian(ir)).swapaxes(0, 1)
            relativ = list()
            absolut = list()
            for iy, y in enumerate(aa):
                for ix, x in enumerate(y):
                    if x > 100:
                        absolut.append((ix + self.x, iy + self.y))
                        relativ.append((ix, iy))
            abs_r.append(pd.DataFrame(absolut, columns=['x', 'y']))
            rel_r.append(pd.DataFrame(relativ, columns=['x', 'y']))

        return abs_l, abs_r, rel_l, rel_r
