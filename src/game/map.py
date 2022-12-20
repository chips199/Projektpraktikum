import imageio.v3 as iio
import os
import matplotlib.pyplot as plt
import pygame
from typing import List


class Map():
    solid = list() # type: List[tuple]
    solid_x_splited = list() # type: List[int]
    solid_y_splited = list() # type: List[int]
    staticimages = list() # type: List[pygame.Surface]

    def __init__(self, game, uri):
        self.game = game
        self.directory = uri

        # load background
        try:
            self.background = pygame.image.load(uri + r'\background.png')
            self.background.convert()
        except:
            self.background = "no image found"

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
                img.convert()
            except:
                continue
            print(str(simg) + ' erfolgreich in pygame geladen')
            self.staticimages.append(img)

            # add solid Pixels
            col_img = iio.imread(simg)
            for yi, y in enumerate(col_img):
                for xi, x in enumerate(y):
                    # print(e1)
                    if x[3] > 200:
                        self.solid.append((xi, yi))

        # load unsolid images
        for filename in os.listdir(self.directory + r'\not_solid'):
            nsimg = os.path.join(self.directory + r'\not_solid', filename)
            if not os.path.isfile(nsimg):
                print(str(nsimg) + ' is not a file')
                continue

            # load image for displaying
            try:
                img = pygame.image.load(nsimg)
                img.convert()
            except:
                continue
            print(str(nsimg) + ' erfolgreich in pygame geladen')
            self.staticimages.append(img)

        # generate splited lists
        self.solid_x_splited = [list() for x in range(self.game.width // 10)]
        self.solid_y_splited = [list() for x in range(self.game.height // 10)]
        for i, point in enumerate(self.solid):
            self.solid_x_splited[(point[0] // 10)].append(i)
            self.solid_y_splited[(point[1] // 10)].append(i)
        #print(self.solid_x_splited[159])

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
        else:
            screen.fill((41, 41, 41))

        #for img in self.staticimages:
        #    screen.blit(img, canvas_rec)
