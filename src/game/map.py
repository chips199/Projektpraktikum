import os
import pandas as pd
import pygame
from typing import List
from pandas import DataFrame


class Map():
    solid_df: DataFrame
    staticimages = list()  # type: List[pygame.surface.Surface]
    player_uris = list()  # type: List[str]

    def __init__(self, game, uri):
        self.game = game
        self.directory = uri

        # load background
        try:
            self.background = pygame.image.load(uri + r'/background.png')
            self.background.convert()
        except:
            self.background = "no image found"  # type: ignore[assignment]

        # load player images
        for filename in os.listdir(self.directory + r'/player'):
            playerimg = os.path.join(self.directory + r'/player', filename)
            if not os.path.isfile(playerimg) or filename[-3:] != 'png':
                print(str(playerimg) + ' is not a  png file')
                continue
            self.player_uris.append(playerimg)

        # load solid images and add solid pixels to solid list
        for filename in os.listdir(self.directory + r'/solid'):
            simg = os.path.join(self.directory + r'/solid', filename)
            if not os.path.isfile(simg):
                print(str(simg) + ' is not a file')
                continue

            # load image for displaying
            try:
                img = pygame.image.load(simg)
                img.convert_alpha()
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
            combinded_solid_image.convert_alpha()
            self.edge_surface = pygame.transform.laplacian(combinded_solid_image).convert_alpha()
            alpha_array = pygame.surfarray.pixels_alpha(self.edge_surface)
            alpha_array = alpha_array.swapaxes(0, 1)
            for yi, y in enumerate(alpha_array):
                for xi, x in enumerate(y):
                    if x > 100:
                        solid.append((xi, yi))
        # Add surface borders
        # horizontal edges
        for x in range(self.game.width):
            solid.append((x, 0))
            solid.append((x, self.game.height))
        # vertical edges
        for y in range(self.game.height):
            solid.append((0, y))
            solid.append((self.game.width, y))

        self.solid_df = pd.DataFrame(solid, columns=['x', 'y'])

        # load unsolid images
        for filename in os.listdir(self.directory + r'/not_solid'):
            nsimg = os.path.join(self.directory + r'/not_solid', filename)
            if not os.path.isfile(nsimg):
                print(str(nsimg) + ' is not a file')
                continue

            # load image for displaying
            try:
                img = pygame.image.load(nsimg)
                img.convert_alpha()
            except:
                continue
            print(str(nsimg) + ' erfolgreich in pygame geladen')
            self.staticimages.append(img)

        # generate one picture out of all solid and not solid images.
        comb_images = self.staticimages.copy()
        if len(comb_images) != 0:
            self.static_objects_img = comb_images.pop()
            for image in comb_images:
                self.static_objects_img.blit(image, (0, 0))
            self.static_objects_img.convert_alpha()

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

        else:
            screen.fill((41, 41, 41))
