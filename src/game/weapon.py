from copy import copy
from datetime import datetime
from enum import Enum

import pandas as pd

from src.game.animated import Animated


class WeaponType(Enum):
    Fist = {"Damage": 20, "Durability": float('inf'), "Cooldown": 0, "IsShortRange": True}
    Sword = {"Damage": 40, "Durability": 20, "Cooldown": 4, "IsShortRange": True}


class Weapon(Animated):

    def __init__(self, waepon_type, *args, **kwargs):
        """
        Initialize the class weapon
        """
        super(Weapon, self).__init__(*args, **kwargs)
        self.weapon_type = waepon_type
        if self.weapon_type == WeaponType.Fist:
            self.cut_frames(2)
        self.last_hit = int(round(datetime.now().timestamp()))
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
        return self.weapon_type.value["Durability"] > 0 and self.last_hit + self.weapon_type.value["Cooldown"] <= int(
            round(datetime.now().timestamp()))

    def hit(self, players):
        """
        Weapon has hit another Player:
         - reduces durability
         - saves the current time for dhe cooldown
        :return: None
        """
        self.weapon_type.value["Durability"] -= 1
        self.last_hit = int(round(datetime.now().timestamp()))
        wdf = self.get_dataframe()
        for p in players:
            if pd.merge(wdf, p.solid_df, how='inner', on=['x', 'y']).empty:
                p.health -= self.weapon_type.value["Damage"]
