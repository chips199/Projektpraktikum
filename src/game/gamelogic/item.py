import pandas as pd
import pygame.image
from src.game.gamelogic import weapon


class Item:
    def __init__(self, weapontype, pos, img):
        self.type = weapontype
        self.img = pygame.image.load(img).convert_alpha()
        self.x, self.y = pos

        edge_surface = pygame.transform.laplacian(self.img).convert_alpha()
        alpha_array = pygame.surfarray.pixels_alpha(edge_surface)
        alpha_array = alpha_array.swapaxes(0, 1)
        solid = list()
        for yi, y in enumerate(alpha_array):
            for xi, x in enumerate(y):
                if x > 100:
                    solid.append((xi + self.x, yi + self.y))
        self.solid_df = pd.DataFrame(solid, columns=['x', 'y'])

    def getItem(self, df, wt):
        if not pd.merge(self.solid_df, df, how='inner', on=['x', 'y']).empty and wt != self.type:
            return self.type
        return None

    def draw(self, g):
        rec = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        g.blit(self.img, rec)
