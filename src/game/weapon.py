from datetime import datetime
from enum import Enum

from src.game.Animated import Animated


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

    def draw(self, **kwargs):
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

    def hit(self):
        """
        Weapon has hit another Player:
         - reduces durability
         - saves the current time for dhe cooldown
        :return: None
        """
        self.weapon_type.value["Durability"] -= 1
        self.last_hit = int(round(datetime.now().timestamp()))
