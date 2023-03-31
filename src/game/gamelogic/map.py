import os
import pandas as pd
import pygame
from typing import List

from matplotlib import pyplot as plt
from pandas import DataFrame

from src.game.gamelogic import weapon
from src.game.gamelogic.item import Item
from src.game.gamelogic.weapon import WeaponType

from src.game.gamelogic.background_music import Music


class Map:
    solid_df: DataFrame
    staticimages = list()  # type: List[pygame.surface.Surface]
    player_uris = list()  # type: List[str]

    def __init__(self, game, uri: str) -> None:
        """
        Initialize a new instance of the Inventory class.

        :param game: The instance of the game
        :param uri: A string containing the path to the directory.
        """
        self.game = game
        self.directory = uri
        self.items = list()  # type: ignore[var-annotated]
        self.weapon_path = {
            weapon.WeaponType.Sword.name: self.directory + "\\waffen\\schwert\\Sword.png",
            weapon.WeaponType.Laser.name: self.directory + "\\waffen\\laser\\laser.png"
        }
        self.music = None
        self.music_load()

        # load background
        try:
            self.background = pygame.image.load(uri + r'/background.png').convert_alpha()
        except:
            self.background = "no image found"  # type: ignore[assignment]

        # load player images
        for directory in next(os.walk(self.directory + r'\player\animation'))[1]:
            if directory[-3:] == 'png':
                print(str(directory) + ' is no folder')
                continue
            self.player_uris.append(os.path.join(self.directory + r'\player\animation', directory))
            print("directory:", os.path.join(self.directory + r'\player', directory))

        # load solid images and add solid pixels to solid list
        for filename in os.listdir(self.directory + r'/solid'):
            simg = os.path.join(self.directory + r'/solid', filename)
            if not os.path.isfile(simg):
                print(str(simg) + ' is not a file')
                continue

            # load image for displaying
            try:
                img = pygame.image.load(simg)
                img = img.convert_alpha()
            except:
                continue
            print(str(simg) + ' successfully loaded into pygame')
            self.staticimages.append(img)

        # combine all static images into one, then use laplace to detect edges.
        # use these to generate array of edge pixels and save it in solid.
        solid = list()
        solid_images = self.staticimages.copy()
        if len(solid_images) != 0:
            combinded_solid_image = solid_images.pop()
            for image in solid_images:
                combinded_solid_image.blit(image, (0, 0))
            combinded_solid_image = combinded_solid_image.convert_alpha()
            self.edge_surface = pygame.transform.laplacian(combinded_solid_image).convert_alpha()
            alpha_array = pygame.surfarray.pixels_alpha(self.edge_surface)
            alpha_array = alpha_array.swapaxes(0, 1)
            for yi, y in enumerate(alpha_array):
                for xi, x in enumerate(y):
                    if x > 100:
                        solid.append((xi, yi))

        # Add surface borders
        # vertical edges
        for y in range(-self.game.height, self.game.height):
            solid.append((0, y))
            solid.append((self.game.width, y))

        self.solid_df = pd.DataFrame(solid, columns=['x', 'y'])

        # generate one picture out of all solid and not solid images.
        comb_images = self.staticimages.copy()
        if len(comb_images) != 0:
            self.static_objects_img = comb_images.pop()
            for image in comb_images:
                self.static_objects_img.blit(image, (0, 0))
            self.static_objects_img = self.static_objects_img.convert_alpha()

    def setitems(self, item_dict) -> None:
        """
        Set the items on the game board based on the item dictionary.
        :param item_dict: Dictionary containing weapon names as keys and a list of positions as values.
        """
        # Iterate through each item in the dictionary
        for k, v in item_dict.items():
            # Iterate through each position for the current item
            for pos in v:
                # Check if the item is already in the game
                if not list(map(lambda i: [i.x, i.y], self.items)).__contains__(pos):
                    # Create a new Item object for the current position and add it to the game's items list
                    self.items.append(Item(WeaponType.getObj(k), pos, self.weapon_path[k]))

        # Iterate through each item in the game's items list
        for i in self.items:
            # Check if the item's position is in the dictionary
            if not item_dict[i.type.name].__contains__([i.x, i.y]):
                # If the item is not in the dictionary, remove it from the game's items list
                self.items.remove(i)

    def draw_items(self, screen: pygame.Surface) -> None:
        """
        Draw all items in the game on the given screen.

        :param screen: The surface on which to draw the items.
        """
        for i in self.items:
            i.draw(screen)

    def draw_background(self, screen: pygame.Surface) -> None:
        """
        Draws the game background on the screen using Pygame blit function

        :param screen: Pygame screen object to blit the background on
        :return: None
        """
        canvas_rec = pygame.Rect(0, 0, self.game.width, self.game.height)
        if isinstance(self.background, pygame.Surface):
            screen.blit(self.background, canvas_rec)

    def draw_solids(self, screen: pygame.Surface) -> None:
        """
        Draw the static objects (solids) on the screen

        :param screen: Pygame screen object to blit the solids on
        """
        canvas_rec = pygame.Rect(0, 0, self.game.width, self.game.height)
        if len(self.staticimages) != 0:
            screen.blit(self.static_objects_img, canvas_rec)

    def music_load(self):
        """
        Loads the music from the folder and starts playing it
        :return:
        """
        # Load Music
        self.music = Music(self.directory + r"\music", 1.0)
        # Start Music
        self.music.play()
