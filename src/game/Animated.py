import os

import pygame
from PIL import Image
from PIL import GifImagePlugin

wrk_dir = os.path.abspath(os.path.dirname(__file__))
# print(wrk_dir)
# wrk_dir = wrk_dir + r"\..\basicmap\player\basic_player_magenta.png"

wrk_dir = wrk_dir + r"\..\basicmap\player\animation"


class Animated:
    def __init__(self):
        pass

    def load_images(path):
        """
        Loads all images in directory. The directory must only contain images.

        Args:
            path: The relative or absolute path to the directory to load images from.

        Returns:
            List of images.
        """
        images = []
        for file_name in os.listdir(path):
            image = pygame.image.load(path + os.sep + file_name).convert()
            images.append(image)
        return images


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

if __name__ == '__main__':
    print(wrk_dir)
    print([x[0] for x in os.walk(wrk_dir)])
