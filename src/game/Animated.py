import pygame
from PIL import Image
from PIL import GifImagePlugin


class Animated():
    def __init__(self, gif):
        self.gif = gif
        imageObject = Image.open(self.gif)
        self.images = list()
        strFormat = 'RGBA'
        for frame in range(0, imageObject.n_frames):
            imageObject.seek(frame)
            imageObject.show()
            raw = imageObject.ostring("raw", strFormat)
            #surface = pygame.image.fromstring(raw, img.size, strFormat).convert_alpha()

        #print(pygame.surfarray.pixels3d(self.images[0]))

if __name__ == '__main__':
    Animated(r"C:\Users\thseb\PycharmProjects\Projektpraktikum\src\basicmap\player\basic_player_purple_animation.gif")
