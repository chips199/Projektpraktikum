import pygame.mixer
from pygame import mixer


class Music:

    def __init__(self, sound_file, volume):
        mixer.init()
        self.music = pygame.mixer.Sound(sound_file)
        self.music.set_volume(volume)

    def play(self):
        """
        Plays a sound
        :return: None
        """
        pygame.mixer.Sound.play(self.music)

    def stop(self):
        """
        Stops the music
        :return:
        """
        self.music.stop()

    def fadeout(self, time):
        """
        fade out the volume before stopping
        :param time: time in ms
        :return: None
        """
        self.music.fadeout(time)
