import time

import pygame.mixer
from pygame import mixer


class Sounds:

    def __init__(self, sound_file, volume):
        """
        Initialize the class Sounds
        """
        mixer.init()
        self.sound = pygame.mixer.Sound(sound_file)
        self.sound.set_volume(volume*0.4)

    def play(self):
        """
        Plays a sound
        :return:
        """
        pygame.mixer.Sound.play(self.sound)
