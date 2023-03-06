import os
import pandas as pd
import pygame
from typing import List
from pandas import DataFrame

from src.game.gamelogic import weapon
from src.game.gamelogic.item import Item
from src.game.gamelogic.weapon import *

from src.game.gamelogic.background_music import Music


class Map:
    solid_df: DataFrame
    staticimages = list()  # type: List[pygame.surface.Surface]
    player_uris = list()  # type: List[str]

    def __init__(self, game, uri):
        self.game = game
        self.directory = uri
        self.items = list()
        self.weapon_path = {
            weapon.WeaponType.Sword.name: self.directory + f"\\waffen\\schwert\\Sword.png",
            weapon.WeaponType.Laser.name: self.directory + f"\\waffen\\laser\\laser.png"
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
            print(str(simg) + ' erfolgreich in pygame geladen')
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

        # load unsolid images
        # for filename in os.listdir(self.directory + r'/not_solid'):
        #     nsimg = os.path.join(self.directory + r'/not_solid', filename)
        #     if not os.path.isfile(nsimg):
        #         print(str(nsimg) + ' is not a file')
        #         continue
        #
        #     # load image for displaying
        #     try:
        #         img = pygame.image.load(nsimg)
        #         img = img.convert_alpha()
        #     except:
        #         continue
        #     print(str(nsimg) + ' erfolgreich in pygame geladen')
        #     self.staticimages.append(img)

        # generate one picture out of all solid and not solid images.
        comb_images = self.staticimages.copy()
        if len(comb_images) != 0:
            self.static_objects_img = comb_images.pop()
            for image in comb_images:
                self.static_objects_img.blit(image, (0, 0))
            self.static_objects_img = self.static_objects_img.convert_alpha()

    def setitems(self, item_dict):
        # self.items = list()
        new_items = list()
        for k, v in item_dict.items():
            for pos in v:
                # if not list(map(lambda i: [i.x, i.y], self.items)).__contains__(pos):
                new_items.append(Item(WeaponType.getObj(k), pos, self.weapon_path[k]))
        self.items = new_items
        # print(item_dict)
        # for i in self.items:
        #     if item_dict[i.type.name].__contains__((i.x, i.y)):
        #         self.items.remove(i)
        # print(list(map(lambda x: x.type.name, self.items)))

    def draw(self, screen):
        """
        displays all map objects to the canvas
        :param screen: pygame canvas
        """
        canvas_rec = pygame.Rect(0, 0, self.game.width, self.game.height)
        if isinstance(self.background, pygame.Surface):
            screen.blit(self.background, canvas_rec)
            if len(self.staticimages) != 0:
                screen.blit(self.static_objects_img, canvas_rec)
        for i in self.items:
            i.draw(screen)

    def music_load(self):
        """
        Loads the music from the folder and starts playing it
        :return:
        """
        # Load Music
        self.music = Music(self.directory + r"\music", 1.0)
        # Start Music
        self.music.play()
