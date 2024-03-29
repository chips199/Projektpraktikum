import os

import pygame.mixer
from pygame import mixer


class Music:

    def __init__(self, sound_path, volume):
        """
        Initialize the class Music
        param: sound_path: path to the music file
        param: volume:  Volume of the music
        """
        # Initialize mixer
        mixer.init()

        # define new type of event
        self.MUSIC_END = pygame.USEREVENT + 1

        # assign event to `endevent`
        pygame.mixer.music.set_endevent(self.MUSIC_END)

        # Adds all songs from the music folder to the playlist
        for i, sound_file in enumerate(os.listdir(sound_path)):
            if i == 0:
                # First song will be loaded directly into the music player
                pygame.mixer.music.load(f"{sound_path}/{sound_file}")
                pygame.mixer.music.set_volume(volume * 0.5)
            else:
                # Other songs added to the queue
                pygame.mixer.music.queue(f"{sound_path}/{sound_file}")

    @staticmethod
    def play(loops=0):
        """
        Plays a sound
        param: loops: Number repetition of music; -1 for infinite repetitions
        :return: None
        """
        pygame.mixer.music.play(loops=loops)

    @staticmethod
    def stop():
        """
        Stops the music
        :return:
        """
        pygame.mixer.music.stop()

    @staticmethod
    def fadeout(time):
        """
        fade out the volume before stopping
        :param time: time in ms
        :return: None
        """
        pygame.mixer.music.fadeout(time)

    @staticmethod
    def get_status():
        """
        Returns whether music is currently being played or not
        :return: boolean
        """
        return pygame.mixer.music.get_busy()
