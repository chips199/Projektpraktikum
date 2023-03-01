from copy import copy
from datetime import datetime
from enum import Enum

import pandas as pd

from src.game.gamelogic.animated import Animated
from src.game.gamelogic.sounds import Sounds


class WeaponType(Enum):
    Fist = {"Damage": 10, "damage_to_weapon_per_hit": 0, "Cooldown": 1, "IsShortRange": True, "shot_speed": 0}
    Sword = {"Damage": 20, "damage_to_weapon_per_hit": 10, "Cooldown": 2, "IsShortRange": True, "shot_speed": 0}
    Laser = {"Damage": 15, "damage_to_weapon_per_hit": 10, "Cooldown": 2, "IsShortRange": False, "shot_speed": 1}

    @staticmethod
    def getObj(string):
        for e in WeaponType:
            if e.name == string:
                return e
        return WeaponType.Sword


class Weapon(Animated):

    def __init__(self, weapon_type, impact_sound_path, impact_sound_path_volume, *args, **kwargs):
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
        self.last_hit = int(round(datetime.now().timestamp()))
        self.hitted = list()
        self.hitted_me = False
        self.durability = 100
        self.abs_l, self.abs_r, self.rel_l, self.rel_r = self.load_dfs()
        # Loads the sound of the weapon
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

    def get_position_weapon_shot(self, **kwargs):
        """
        Returns the position for the shot
        """
        if self.animation_direction == 1:
            x_pos = kwargs["x"] + kwargs["width"] - self.frame_width - 5
        else:
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
        return self.durability > 0 and self.last_hit + self.weapon_type.value["Cooldown"] <= int(
            round(datetime.now().timestamp()))

    def hit(self):
        """
        Weapon has hit another Player:
         - reduces durability
         - saves the current time for dhe cooldown
        :return: None
        """
        self.durability -= self.weapon_type.value["damage_to_weapon_per_hit"]
        self.last_hit = int(round(datetime.now().timestamp()))
        # Play the sound of the weapon
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
    def check_hit(pl, players, map_df, g):
        pldf = pl.solid_df
        # check if player is hitting me
        for p in players:
            if p.weapon.animation_running:
                if not p.weapon.hitted_me and not pd.merge(p.weapon.get_dataframe(), pldf, how='inner',
                                                           on=['x', 'y']).empty:
                    Weapon.player_hit(g, p, pl, p.weapon.weapon_type.value["Damage"])
            else:
                p.weapon.hitted_me = False
            # check if a weapon shot has hit a player
            for shot in p.weapon_shots:
                if not pd.merge(shot.get_dataframe(), pldf, how='inner', on=['x', 'y']).empty:
                    Weapon.player_hit(g, p, pl, shot.damge)

        # hitting wall
        if pl.weapon.animation_running:
            if not pl.weapon.hitted_me and not pd.merge(pl.weapon.get_dataframe(), map_df, how='inner',
                                                        on=['x', 'y']).empty:
                if pl.is_blocking:
                    pl.health -= (p.weapon.weapon_type.value["Damage"] / 2)
                    pl.blood_animation.set_pos(pl.x - 47, pl.y + 15)
                    pl.blood_animation.draw_animation_once(g=g, reset=True)
                else:
                    pl.health -= p.weapon.weapon_type.value["Damage"]
                pl.weapon.hitted_me = True
                if not pl.is_alive():
                    pl.killed_by[4] += 1
                    pl.death_time = datetime.now()
                else:
                    pl.sound_hurt.play()
        else:
            pl.weapon.hitted_me = False

    @staticmethod
    def player_hit(g, p, pl, damage):
        """
        Method executed when a player is hit by a weapon or a gunshot
        """
        if pl.is_blocking:
            print("blocked")
            pl.health -= (damage / 2)
            pl.blood_animation.set_pos(pl.x - 47, pl.y + 15)
            pl.blood_animation.draw_animation_once(g=g, reset=True)
        else:
            pl.health -= damage
        p.weapon.hitted_me = True
        if not pl.is_alive():
            pl.killed_by[int(p.id)] += 1
            pl.death_time = datetime.now()
        else:
            pl.sound_hurt.play()
