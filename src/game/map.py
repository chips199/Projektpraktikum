import imageio.v3 as iio
import os
import matplotlib.pyplot as plt
import numpy as np
import pygame
from typing import List
from typing import Tuple


class Map():
    solid = list()  # type: List[Tuple[int, int]]
    solid_x_splited = list()  # type: List[List[int]]
    solid_y_splited = list()  # type: List[List[int]]
    staticimages = list()  # type: List[pygame.surface.Surface]
    player_uris = list()  # type: List[str]

    def __init__(self, game, uri):
        self.game = game
        self.directory = uri

        # load background
        try:
            self.background = pygame.image.load(uri + r'\background.png')
            self.background.convert()
        except:
            self.background = "no image found"  # type: ignore[assignment]

        for filename in os.listdir(self.directory + r'\player'):
            playerimg = os.path.join(self.directory + r'\player', filename)
            if not os.path.isfile(playerimg):
                print(str(playerimg) + ' is not a file')
                continue
            self.player_uris.append(playerimg)

        # load solid images and add solid pixels to list
        # print(self.directory + r'\solid')
        for filename in os.listdir(self.directory + r'\solid'):
            simg = os.path.join(self.directory + r'\solid', filename)
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

            # add solid Pixels
            # col_img = iio.imread(simg)
            # for yi, y in enumerate(col_img):
            #    for xi, x in enumerate(y):
            #        # print(e1)
            #        if x[3] > 200:
            #            self.solid.append((xi, yi))

        # combine all static images into one, then use laplace to detect edges.
        # use these to generate array of edge pixels and save it in solid.
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
                    # print(e1)
                    if x > 100:
                        self.solid.append((xi, yi))
        # Add surface borders
        # horizontal edges
        for x in range(self.game.width):
            self.solid.append((x, 0))
            self.solid.append((x, self.game.height))
        # vertical edges
        for y in range(self.game.height):
            self.solid.append((0, y))
            self.solid.append((self.game.width, y))

        # load unsolid images
        for filename in os.listdir(self.directory + r'\not_solid'):
            nsimg = os.path.join(self.directory + r'\not_solid', filename)
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

        # generate splited lists
        # self.solid_x_splited = [list() for x in range(self.game.width // 10)]
        # self.solid_y_splited = [list() for x in range(self.game.height // 10)]
        # for i, point in enumerate(self.solid):
        #     self.solid_x_splited[(point[0] // 10)].append(i)
        #     self.solid_y_splited[(point[1] // 10)].append(i)
        # print(self.solid_x_splited[159])

    def colides(self, edge_array):
        # checks if a list of pixels intersects with the list of solid pixels of the map
        a = self.solid
        b = edge_array
        c = list(map(lambda x: str(x[0]) + ',' + str(x[1]), a))
        d = list(map(lambda x: str(x[0]) + ',' + str(x[1]), b))
        # print(b)
        # print(a)
        return len(np.intersect1d(c, d)) != 0

    def is_coliding(self, p):
        # x Group
        x_ps = self.solid_x_splited[p[0] // 10]
        # y Group
        y_ps = self.solid_x_splited[p[1] // 10]
        # Intersektion of the two groups provides max 100 points to check
        candidates = set(x_ps).intersection(set(y_ps))
        for i in candidates:
            if self.solid[i] == p:
                # returns True when Point inside solid Object
                return True
        # returns True when point outside Gamearea
        return not pygame.Rect(0, 0, self.game.width, self.game.height).collidepoint(p)

    def draw(self, screen):
        canvas_rec = pygame.Rect(0, 0, self.game.width, self.game.height)
        if type(self.background) == pygame.Surface:
            screen.blit(self.background, canvas_rec)
            if len(self.staticimages) != 0:
                screen.blit(self.static_objects_img, canvas_rec)
                # screen.blit(self.edge_surface, canvas_rec)

        else:
            screen.fill((41, 41, 41))

        # for img in self.staticimages:
        #    screen.blit(img, canvas_rec)
