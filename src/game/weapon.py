from datetime import datetime


class Weapon:

    def __init__(self, distance, damage, durability, cooldown):
        self.distance = distance
        self.damage = damage
        self.durability = durability
        self.cooldown = cooldown
        self.last_hit = int(round(datetime.now().timestamp()))

    def can_hit(self):
        """
        Returns whether the weapon can currently hit
        The following conditions must be met:
         - Shelf life not yet used up
         - Cooldown must have expired
        """
        return self.durability > 0 and self.last_hit + self.cooldown <= int(round(datetime.now().timestamp()))

    def hit(self):
        self.durability -= 1
        self.last_hit = int(round(datetime.now().timestamp()))
