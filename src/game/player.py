import datetime
from copy import copy

import pygame.draw

from src.game import weapon
from src.game.animated import Animated


class Player(Animated):
    last_jump = datetime.datetime.now()
    height_jump = 200
    status_jump = 0
    is_connected = False
    mousepos = (0, 0)
    health = 100

    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)

        self.falling_time = datetime.datetime.now()
        self.jumping_time = datetime.datetime.now()
        # self.x = startx
        # self.y = starty
        self.velocity = 7
        self.velocity_gravity = 1
        self.velocity_jumping = self.max_jumping_speed = 20
        self.velocity_time = 15
        self.landed = False
        self.is_jumping = False
        self.is_falling = True
        self.block_x_axis = False
        self.cut_frames(2)
        # self.color = color
        self.weapon = weapon
        self.velocity_counter = 0
        self.velocity_counter2 = 0
        self.health = 50
        map_dir = "\\".join(str(self.directory).split('\\')[:-3])
        fist_path = map_dir + f"\\waffen\\faeuste\\animation\\fists_{self.get_color(self.directory)}_animation"
        # sword_path = map_dir + f"\\waffen\\schwert\\animation\\sword_hold_animation_{self.get_color(self.directory)}"
        self.weapon = weapon.Weapon(weapon.WeaponType.Fist, [self.x, self.y], fist_path)
        # self.weapon = weapon.Weapon(weapon.WeaponType.Sword, [self.x, self.y], sword_path)

    def draw(self, g):
        super(Player, self).draw(g=g)
        pygame.draw.line(g, pygame.Color(231, 24, 55), (self.x, self.y - 5), (self.x + self.frame_width, self.y - 5), 3)
        if self.health > 0:
            pygame.draw.line(g, pygame.Color(45, 175, 20), (self.x, self.y - 5),
                             (self.x + (self.frame_width * (self.health / 100)), self.y - 5), 3)
        self.weapon.animation_direction = self.animation_direction
        self.weapon.draw(g=g, x=self.x, y=self.y, width=self.frame_width, height=self.frame_height)

    @staticmethod
    def shift_df(df, dirn, n):
        """
        "moves" dataframe of coordinates
        :param df: dataframe
        :param dirn: direction
        :param n: distance
        :return: new dataframe
        """
        if dirn == 0:
            df['x'] = df['x'].map(lambda x: x + n)
        elif dirn == 1:
            df['x'] = df['x'].map(lambda x: x - n)
        elif dirn == 2:
            df['y'] = df['y'].map(lambda y: y - n)
        else:
            df['y'] = df['y'].map(lambda y: y + n)
        return df

    def move(self, dirn, v=-99):
        """
        :param dirn: 0 - 3 (right, left, up, down)
        :param    v: velocity
        :return: None
        """
        if v == -99:
            v = self.velocity

        if dirn == 0:
            self.animation_direction = 1
            self.x += v
            self.weapon.x += v
        elif dirn == 1:
            self.animation_direction = 2
            self.x -= v
            self.weapon.x -= v
        elif dirn == 2:
            self.y -= v
            self.weapon.y -= v
        else:
            self.y += v
            self.weapon.y += v

        self.solid_df = Player.shift_df(self.solid_df, dirn, v)  # type:ignore[has-type]

    def jump(self, func):
        """
        moves player upwards when possible
        :param func: function to check if there is no collision while jumping
        """

        # when player is not falling
        if not self.is_falling:

            # check is moving upwards is possible
            vel = func(player=self, dirn=2, distance=int(self.velocity_jumping))

            # when upwards is possible
            if vel > 0:

                # initialize jumping when velocity_jumping is reseted (= max_jumping_speed) and the player
                # is currently not jumping
                if not self.is_jumping:
                    self.is_jumping = True
                    # reset timer to current time
                    self.jumping_time = datetime.datetime.now()

                # after certain time, decrease jumping speed
                # elif datetime.datetime.now() - self.jumping_time > datetime.timedelta(milliseconds=self.velocity_time):
                elif self.velocity_counter2 >= self.velocity_counter:
                    self.velocity_jumping -= 1
                    # reset timer to current time
                    self.jumping_time = datetime.datetime.now()
                    self.velocity_counter2 = 0

                else:
                    self.velocity_counter2 += 1

                # jump with speed calculated in func()
                self.move(2, vel)

            # when jumping speed reaches 0 or jumping is not possible, stop jumping
            if vel <= 0:
                self.is_jumping = False
                self.velocity_jumping = self.max_jumping_speed

    def beaten(self, weapon_enemy):
        """
        player was beaten
        player is subtracted the damage of the weapon and it is checked if the player died during the attack
        :param weapon_enemy The weapon with which the player was hit
        :return None
        """
        self.health -= weapon_enemy.damage
        if self.health <= 0:
            print("Player died")
            # TODO: Anzeige auf Screen und Spieler ausblenden?
            self.health = 0

    def is_alive(self):
        """
        Returns whether the player is still alive
        :return: boolean: True: Is alive;  False: Isn't alive
        """
        return self.health > 0

    def refresh_solids(self):
        new_pos = copy(self.relativ_solids_df)
        new_pos['x'] = new_pos['x'].map(lambda x: x + self.x)
        new_pos['y'] = new_pos['y'].map(lambda y: y + self.y)
        self.solid_df = new_pos

    def gravity(self, func):
        """
        moves player downwards when possible
        :param func: function to check if there is no collision while falling
        """
        # when player is not jumping
        if not self.is_jumping:

            # calculate if player is able to fall (vel > 0 means yes)
            vel = func(player=self, dirn=3, distance=int(self.velocity_gravity))

            # if able to fall
            if vel > 0:

                # initialize falling when the player is currently not falling
                if not self.is_falling:
                    self.is_falling = True
                    self.landed = False
                    # reset timer to current time
                    self.falling_time = datetime.datetime.now()

                # after certain time increase the falling speed until it's maximum
                # elif datetime.datetime.now() - self.falling_time > datetime.timedelta(milliseconds=self.velocity_time):
                elif self.velocity_counter2 >= self.velocity_counter:
                    self.velocity_gravity += 1
                    # reset timer to current time
                    self.falling_time = datetime.datetime.now()
                    self.velocity_counter2 = 0

                    # limit the falling speed to it's maximum
                    if self.velocity_gravity > self.max_jumping_speed:
                        self.velocity_gravity = self.max_jumping_speed

                else:
                    self.velocity_counter2 += 1

                # move player down with speed calculated in func()
                self.move(dirn=3, v=int(vel))
                self.block_x_axis = False

            # otherwise check if the player is really landed or may standing/hanging on an edge
            elif vel <= 0:

                if not self.landed:
                    # shift players df to the right and check if falling would then be possible
                    # in addition block the movement on x-axis for the player (for the keyboard)
                    self.block_x_axis = True
                    self.shift_df(df=self.solid_df, dirn=0, n=self.velocity * 2)
                    vel = func(player=self, dirn=3, distance=int(self.velocity_gravity * 2))

                    # if falling is then possible
                    if vel > 0:
                        # shift back the df and move to the right so in next cycle the player will continue to fall
                        self.shift_df(df=self.solid_df, dirn=1, n=self.velocity * 2)
                        self.move(dirn=0, v=int(self.velocity * 2))

                    else:
                        # try the same for direction left
                        self.shift_df(df=self.solid_df, dirn=1, n=self.velocity * 4)
                        vel = func(player=self, dirn=3, distance=int(self.velocity_gravity))

                        # if falling is possible after shifting to left, shift df back to original position and move left
                        if vel > 0:
                            self.shift_df(df=self.solid_df, dirn=0, n=self.velocity * 2)
                            self.move(dirn=1, v=int(self.velocity * 2))

                        # otherwise it means that the player is standing on its feet, so he is landed correctly
                        # so stop falling and reset the parameters
                        else:
                            self.shift_df(df=self.solid_df, dirn=0, n=self.velocity * 2)
                            self.landed = True
                            self.block_x_axis = False
                            self.is_falling = False
                            self.velocity_gravity = 1

    @staticmethod
    def get_color(p):
        if p.__contains__("magenta"):
            return "magenta"
        elif p.__contains__("orange"):
            return "orange"
        elif p.__contains__("purple"):
            return "purple"
        else:
            return "turquoise"
