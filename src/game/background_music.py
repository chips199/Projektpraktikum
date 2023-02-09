import os

import pygame.mixer
from pygame import mixer


class Music:

    def __init__(self, sound_path, volume):
        """
        Initialize the class Music
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
                pygame.mixer.music.set_volume(volume)
            else:
                # Other songs added to the queue
                pygame.mixer.music.queue(f"{sound_path}/{sound_file}")

    def play(self, loops=0):
        """
        Plays a sound
        :return: None
        """
        pygame.mixer.music.play(loops=loops)

    def stop(self):
        """
        Stops the music
        :return:
        """
        pygame.mixer.music.stop()

    def fadeout(self, time):
        """
        fade out the volume before stopping
        :param time: time in ms
        :return: None
        """
        pygame.mixer.music.fadeout(time)
