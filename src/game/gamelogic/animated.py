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

    def set_pos(self, x: int, y: int) -> None:
        """
        Set the absolute position of the widget in the parent widget

        :param x: The absolute x position of the widget
        :param y: The absolute y position of the widget
        """
        self.x = x
        self.y = y

    def draw(self, **kwargs):
        """
        displays an object to the canvas
        :param g: pygame canvas
        """
        if self.animation_direction == 0:
            self.animate(kwargs["g"], self.images_right)
        else:
            self.animate(kwargs["g"], self.images_left)

    def cut_frames(self, n: int):
        """
        Cuts the number of frames of animation by a factor of n by deleting
        the frames between the current frame and n - 1.
        """
        # Cut the number of frames for the right facing images
        self.images_right = list(x for i, x in enumerate(self.images_right) if i % int(n) == 0)
        # Cut the number of frames for the left facing images
        self.images_left = list(x for i, x in enumerate(self.images_left) if i % int(n) == 0)
        # Set the total number of frames
        self.frame_count = len(self.images_right) - 1  # amount of frames of animation, starting at index 0

    def double_frames(self, factor: int) -> None:
        """
        Duplicate each frame in the animation by a given factor.

        :param factor: The factor by which to duplicate the frames.
        """
        # Create copies of the lists of images so we can safely insert the duplicates.
        copy_right = self.images_right[:]
        copy_left = self.images_left[:]

        # Iterate through the images in reverse order so we can safely insert new elements at their current index.
        for index, (image_right, image_left) in reversed(list(enumerate(zip(copy_right, copy_left)))):
            # For each image, insert a copy of it into the list the given number of times.
            for _ in range(factor):
                self.images_right.insert(index, image_right)
                self.images_left.insert(index, image_left)

        # Update the frame count based on the new length of the lists.
        self.frame_count = len(self.images_right) - 1

    def animate(self, g, images):
        """
        Animate the object

        :param g: Pygame game object to render the animation onto
        :param images: List of images used for the animation
        """
        player_rec = pygame.Rect(self.x, self.y, self.frame_width, self.frame_height)
        if self.current_frame < self.frame_count and self.animation_running:
            # Render the current frame of the animation
            g.blit(images[self.current_frame + 1], player_rec)
            self.current_frame += 1
        else:
            # If the animation is finished, render the first frame
            g.blit(images[0], player_rec)
            # Reset the frame count and stop the animation
            self.current_frame = 0
            self.animation_running = False

    def draw_animation_once(self, g, reset=False):
        """
        Draw animation frames once

        :param g: Pygame game object to render the animation onto
        :param reset: if True, resets current frame counter to 0
        """
        if self.current_frame < self.frame_count:
            self.animation_running = True
            self.draw(g=g)
        else:
            self.animation_running = False
            if reset:
                self.current_frame = 0

    def stop_animation(self):
        """
        Stop the animation
        """
        self.animation_running = False

    def start_animation_in_direction(self, direction):
        self.animation_direction = direction
        self.animation_running = True

    def start_animation_in_direction(self, direction: int) -> None:
        """
        Start the animation in the given direction

        :param direction: A int representing the direction of the animation.
                          Should be one of either 0 means 'right', 1 means 'left'
        """
        # Set the direction of the animation
        self.animation_direction = direction
        # Set the flag to indicate that the animation is running
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

    def load_dfs(self) -> Tuple[List[pd.DataFrame], List[pd.DataFrame], List[pd.DataFrame], List[pd.DataFrame]]:
        """
        Load the absolute and relative positions of the images for left and right sides using Laplacian transform.
        Returns a tuple of four lists containing pandas dataframes for the absolute positions of images on left
        and right side, and the relative positions of images on left and right side.
        """
        # Initialize empty lists for the positions
        rel_l = list()
        rel_r = list()
        abs_l = list()
        abs_r = list()
        # Iterate over the images on the left
        for il in self.images_left:
            # Apply Laplacian transform to the image and get the alpha channel pixels
            aa = pygame.surfarray.pixels_alpha(pygame.transform.laplacian(il)).swapaxes(0, 1)
            # Initialize empty lists for the relative and absolute positions
            relativ = list()
            absolut = list()
            # Iterate over each pixel in the image and check if the alpha value is greater than 100
            for iy, y in enumerate(aa):
                for ix, x in enumerate(y):
                    if x > 100:
                        absolut.append((ix + self.x, iy + self.y))
                        relativ.append((ix, iy))
            # Append the pandas dataframe of the absolute and relative positions to the lists
            abs_l.append(pd.DataFrame(absolut, columns=['x', 'y']))
            rel_l.append(pd.DataFrame(relativ, columns=['x', 'y']))
        # Iterate over the images on the right
        for ir in self.images_right:
            # Apply Laplacian transform to the image and get the alpha channel pixels
            aa = pygame.surfarray.pixels_alpha(pygame.transform.laplacian(ir)).swapaxes(0, 1)
            # Initialize empty lists for the relative and absolute positions
            relativ = list()
            absolut = list()
            # Iterate over each pixel in the image and check if the alpha value is greater than 100
            for iy, y in enumerate(aa):
                for ix, x in enumerate(y):
                    if x > 100:
                        absolut.append((ix + self.x, iy + self.y))
                        relativ.append((ix, iy))
            # Append the pandas dataframe of the absolute and relative positions to the lists
            abs_r.append(pd.DataFrame(absolut, columns=['x', 'y']))
            rel_r.append(pd.DataFrame(relativ, columns=['x', 'y']))
        # Return the tuple of four lists containing pandas dataframes of positions
        return abs_l, abs_r, rel_l, rel_r

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
