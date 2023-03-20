import pygame.mixer
from pygame import mixer


class Sounds:

    def __init__(self, sound_file, volume):
        """
        Initialize the class Sounds
        param: sound_file: Path to the sound file
        param: volume: Volume of the sound-effect, can be between 0 and 1
        """
        mixer.init()
        self.sound = pygame.mixer.Sound(sound_file)
        self.sound.set_volume(volume*0.4)

    def play(self):
        """
        Starts the sound-effect
        :return:
        """
        pygame.mixer.Sound.play(self.sound)
