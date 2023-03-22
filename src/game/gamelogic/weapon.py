from copy import copy
from datetime import datetime
from enum import Enum

import pandas as pd
import pygame.image

from src.game.gamelogic.animated import Animated
from src.game.gamelogic.sounds import Sounds


class WeaponType(Enum):
    Fist = {"Damage": 10, "damage_to_weapon_per_hit": 0, "Cooldown": 1, "IsShortRange": True, "shot_speed": 0, "sound_level": 1, "abs_l": None, "abs_r": None, "rel_l": None, "rel_r": None}
    Sword = {"Damage": 20, "damage_to_weapon_per_hit": 10, "Cooldown": 2, "IsShortRange": True, "shot_speed": 0, "sound_level": 1, "abs_l": None, "abs_r": None, "rel_l": None, "rel_r": None}
    Laser = {"Damage": 15, "damage_to_weapon_per_hit": 10, "Cooldown": 2, "IsShortRange": False, "shot_speed": 15, "sound_level": 0.9, "abs_l": None, "abs_r": None, "rel_l": None, "rel_r": None}

    @staticmethod
    def getObj(string):
        for e in WeaponType:
            if e.name == string:
                return e
        return WeaponType.Fist


class Weapon(Animated):

    def __init__(self, weapon_type, impact_sound_path, *args, **kwargs):
        """
        Initialize the class weapon
        :param impact_sound_path: Path to the sound-file
        :param impact_sound_path_volume: Volume of the sound: Range: [0:1]
        """
        super(Weapon, self).__init__(*args, **kwargs)
        self.destroyed = False
        self.weapon_type = weapon_type
        if self.weapon_type == WeaponType.Fist:
            self.cut_frames(2)
        self.drop_img = None
        try:
            self.drop_img = pygame.image.load(
                "\\".join(self.directory.split("\\")[:-2]) + "\\" + self.weapon_type.name + ".png").convert_alpha()
        except FileNotFoundError:
            pass
        self.last_hit = int(round(datetime.now().timestamp()))
        self.hitted = list()
        self.hitted_me = False
        self.durability = 100
        if self.weapon_type.value["abs_l"] is None:
            self.abs_l, self.abs_r, self.rel_l, self.rel_r = self.load_dfs()
            self.weapon_type.value["abs_l"] = self.abs_l
            self.weapon_type.value["abs_r"] = self.abs_r
            self.weapon_type.value["rel_l"] = self.rel_l
            self.weapon_type.value["rel_r"] = self.rel_r
        else:
            self.abs_l = self.weapon_type.value["abs_l"]
            self.abs_r = self.weapon_type.value["abs_r"]
            self.rel_l = self.weapon_type.value["rel_l"]
            self.rel_r = self.weapon_type.value["rel_r"]
            # Loads the sound of the weapon
        impact_sound_path_volume = self.weapon_type.value['sound_level']
        self.sound_hit = Sounds(impact_sound_path + r"\sound_effects\sound_hit.mp3", impact_sound_path_volume)
        self.sound_destroy = Sounds(impact_sound_path + r"\sound_effects\sound_destroy.mp3", impact_sound_path_volume)

    def get_dataframe(self, frame=-99):
        try:
            if self.animation_direction == 0:
                erg = copy(self.rel_r[frame])
                erg['x'] = erg['x'].map(lambda x: x + self.x)
                erg['y'] = erg['y'].map(lambda y: y + self.y)
                return erg
            else:
                erg = copy(self.rel_l[frame])
                erg['x'] = erg['x'].map(lambda x: x + self.x)
                erg['y'] = erg['y'].map(lambda y: y + self.y)
                return erg
        except IndexError:
            if self.animation_direction == 0:
                erg = copy(self.rel_r[self.current_frame])
                erg['x'] = erg['x'].map(lambda x: x + self.x)
                erg['y'] = erg['y'].map(lambda y: y + self.y)
                return erg
            else:
                erg = copy(self.rel_l[self.current_frame])
                erg['x'] = erg['x'].map(lambda x: x + self.x)
                erg['y'] = erg['y'].map(lambda y: y + self.y)
                return erg

    def draw(self, **kwargs):
        """

        :param kwargs:
        """
        self.y = kwargs["y"] + kwargs["height"] - self.frame_height
        if self.animation_direction == 1:
            self.x = kwargs["x"] + kwargs["width"] - self.frame_width
            super(Weapon, self).draw(g=kwargs["g"])
        else:
            self.x = kwargs["x"]
            super(Weapon, self).draw(g=kwargs["g"])

    def get_position_for_weapon_shot(self, **kwargs):
        """
        Returns the position for the shot
        """
        if self.animation_direction == 1:
            # player direction: left
            x_pos = kwargs["x"] + kwargs["width"] - self.frame_width - 5
        else:
            # player direction: right
            x_pos = kwargs["x"] + self.frame_width - 5
        y_pos = kwargs["y"] + kwargs["height"] - self.frame_height + 46
        return x_pos, y_pos

    def can_hit(self):
        """
        Returns whether the weapon can currently hit
        The following conditions must be met:
         - Shelf life not yet used up
         - Cooldown must have expired
        """
        return self.durability > 0 and self.last_hit + self.weapon_type.value["Cooldown"] <= int(round(datetime.now().timestamp()))

    def hit(self):
        """
        Weapon has hit another Player:
         - reduces durability
         - saves the current time for dhe cooldown
        :return: None
        """
        self.durability -= self.weapon_type.value["damage_to_weapon_per_hit"]
        self.last_hit = int(round(datetime.now().timestamp()))
        print(f"durability: {self.durability}")
        # Play sound of the weapon
        if self.durability <= 0:
            self.destroyed = True
            self.sound_destroy.play()
        else:
            self.sound_hit.play()

    def is_short_range_weapon(self):
        """
        returns whether the weapon is a short range weapon
        """
        return self.weapon_type.value["IsShortRange"]

    def get_shot_speed(self):
        """
        returns the speed of a shoot
        """
        return self.weapon_type.value["shot_speed"]

    def get_weapon_damage(self):
        """
        Returns the damage caused by the weapon
        """
        return self.weapon_type.value["Damage"]

    @staticmethod
    def check_hit(player, players, map_df, g):
        player_df = player.solid_df
        # check if player is hitting me
        for player_other in players:
            if player_other.weapon.animation_running:
                if not player_other.weapon.hitted_me and not pd.merge(player_other.weapon.get_dataframe(), player_df, how='inner', on=['x', 'y']).empty:
                    Weapon.player_hit(g, player_other, player, player_other.weapon.weapon_type.value["Damage"])
            else:
                player_other.weapon.hitted_me = False
            # check if a weapon shot has hit a player
            for shot in player_other.weapon_shots:
                if not pd.merge(shot.get_dataframe(), player_df, how='inner', on=['x', 'y']).empty:
                    Weapon.player_hit(g, player_other, player, shot.damage)
                    shot.active = False

        # hitting wall
        if player.weapon.animation_running:
            if not player.weapon.hitted_me and not pd.merge(player.weapon.get_dataframe(), map_df, how='inner', on=['x', 'y']).empty:
                if player.is_blocking:
                    player.health -= (player_other.weapon.weapon_type.value["Damage"] / 2)
                else:
                    player.health -= player_other.weapon.weapon_type.value["Damage"]
                player.blood_frame = 0
                player.weapon.hitted_me = True
                if not player.is_alive():
                    player.killed_by[4] += 1
                    player.death_time = datetime.now()
                else:
                    player.sound_hurt.play()
        else:
            player.weapon.hitted_me = False

    @staticmethod
    def player_hit(canvas, other_player, player, damage):
        """
        Method executed when a player is hit by a weapon or a gunshot
        param: canvas: Canvas on which the blood splatters are painted
        param: other_player: The other player who hit player
        param: player: Player who gets the damage
        param: damage: the damage the player gets off
        """
        if player.is_blocking:  # reduced Damage if the player is blocking
            player.health -= (damage / 2)
        else:  # Normal Damage
            player.health -= damage
        # Blood animation
        player.blood_animation.set_pos(player.x - 47, player.y + 15)
        player.blood_animation.draw_animation_once(g=canvas, reset=True)

        other_player.weapon.hitted_me = True
        # Check if player is dead
        if not player.is_alive():
            player.killed_by[int(other_player.id)] += 1
            player.death_time = datetime.now()
        else:
            # Play Sound that player was hurt
            player.sound_hurt.play()
