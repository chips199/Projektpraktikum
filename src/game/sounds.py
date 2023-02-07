import time

import pygame.mixer
from pygame import mixer


class Sounds:

    def __init__(self, sound_file, volume):
        mixer.init()
        self.sound = pygame.mixer.Sound(sound_file)
        self.sound.set_volume(volume)

    def play(self):
        """
        Plays a sound
        :return:
        """
        pygame.mixer.Sound.play(self.sound)
