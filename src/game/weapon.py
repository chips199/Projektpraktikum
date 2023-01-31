from copy import copy
from datetime import datetime
from enum import Enum

import pandas as pd

from src.game.animated import Animated


class WeaponType(Enum):
    Fist = {"Damage": 10, "damage_to_weapon_per_hit": 0, "Cooldown": 1, "IsShortRange": True}
    Sword = {"Damage": 20, "damage_to_weapon_per_hit": 10, "Cooldown": 2, "IsShortRange": True}


class Weapon(Animated):

    def __init__(self, waepon_type, *args, **kwargs):
        """
        Initialize the class weapon
        """
        super(Weapon, self).__init__(*args, **kwargs)
        self.destroyed = False
        self.weapon_type = waepon_type
        if self.weapon_type == WeaponType.Fist:
            self.cut_frames(2)
        self.last_hit = int(round(datetime.now().timestamp()))
        self.hitted = list()
        self.hitted_me = False
        self.durebility = 100
        self.abs_l, self.abs_r, self.rel_l, self.rel_r = self.load_dfs()

    def get_dataframe(self, frame=-99):
        try:
            if self.animation_direction == 1:
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
            if self.animation_direction == 1:
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
        if self.animation_direction == 2:
            self.x = kwargs["x"] + kwargs["width"] - self.frame_width
            super(Weapon, self).draw(g=kwargs["g"])
        else:
            self.x = kwargs["x"]
            super(Weapon, self).draw(g=kwargs["g"])

    def can_hit(self):
        """
        Returns whether the weapon can currently hit
        The following conditions must be met:
         - Shelf life not yet used up
         - Cooldown must have expired
        """
        return self.durebility > 0 and self.last_hit + self.weapon_type.value["Cooldown"] <= int(
            round(datetime.now().timestamp()))

    def hit(self):
        """
        Weapon has hit another Player:
         - reduces durability
         - saves the current time for dhe cooldown
        :return: None
        """
        self.durebility -= self.weapon_type.value["damage_to_weapon_per_hit"]
        self.last_hit = int(round(datetime.now().timestamp()))
        self.destroyed = self.durebility <= 0

    def check_hit1(self, pl, players, map_df):
        pl_hitted = self.hitted.__contains__(-99)
        wdf = self.get_dataframe(self.current_frame)
        for ip, p in enumerate(players):
            if not pd.merge(wdf, p.solid_df, how='inner', on=['x', 'y']).empty:
                if not self.hitted.__contains__(ip):
                    self.hitted.append(ip)
                    p.health -= self.weapon_type.value["Damage"]
        if not pd.merge(wdf, map_df, how='inner', on=['x', 'y']).empty and not pl_hitted:
            self.hitted.append(-99)
            pl.health -= self.weapon_type.value["Damage"]
        if self.current_frame == self.frame_count:
            self.hitted = list()
            self.destroyed = self.durebility <= 0

    @staticmethod
    def check_hit(pl, players, map_df):
        pldf = pl.solid_df
        for p in players:
            if p.weapon.animation_running:
                if not p.weapon.hitted_me and not pd.merge(p.weapon.get_dataframe(), pldf, how='inner', on=['x', 'y']).empty:
                    pl.health -= p.weapon.weapon_type.value["Damage"]
                    p.weapon.hitted_me = True
            else:
                p.weapon.hitted_me = False
        if pl.weapon.animation_running:
            if not pl.weapon.hitted_me and not pd.merge(pl.weapon.get_dataframe(), map_df, how='inner', on=['x', 'y']).empty:
                pl.health -= pl.weapon.weapon_type.value["Damage"]
                pl.weapon.hitted_me = True
        else:
            pl.weapon.hitted_me = False
