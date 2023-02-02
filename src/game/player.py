import datetime
import math
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
        self.current_moving_velocity = 7
        self.moving_velocity_on_ground = self.moving_velocity_in_air = 7
        self.velocity_gravity = 1
        self.velocity_jumping = self.max_jumping_speed = 20
        self.velocity_time = 15
        self.landed = False
        self.is_jumping = False
        self.is_falling = True
        self.block_x_axis = False
        self.cut_frames(2)
        self.weapon = weapon
        self.velocity_counter = 0
        self.velocity_counter2 = 0
        self.sliding_counter = self.max_sliding_time = 50
        map_dir = "\\".join(str(self.directory).split('\\')[:-3])
        self.fist_path = map_dir + f"\\waffen\\faeuste\\animation\\fists_{self.get_color(self.directory)}_animation"
        self.sword_path = map_dir + f"\\waffen\\schwert\\animation\\sword_hold_animation_{self.get_color(self.directory)}"
        # self.weapon = weapon.Weapon(weapon.WeaponType.Fist, [self.x, self.y], self.fist_path)
        self.weapon = weapon.Weapon(weapon.WeaponType.Sword, [self.x, self.y], self.sword_path)
        self.death_animation = Animated(start=[self.x, self.y], directory=map_dir + f"\\player\\death_animation\\death_animation_{self.get_color(self.directory)}")
        self.blood_animation = Animated(start=[self.x+5, self.y-20], directory=map_dir + f"\\player\\blood_animation")
        self.blood_animation.start_animation_in_direction(drn=1)
        self.blood_animation.double_frames(factor=2)

    def set_velocity(self, data=(1, 1, 0)):
        self.moving_velocity_on_ground = data[0]
        self.moving_velocity_in_air = data[1]
        self.velocity_jumping = self.max_jumping_speed = data[2]
        self.velocity_counter = data[3]

    def keep_sliding(self, func):
        if self.landed and not self.is_jumping and self.sliding_counter > 1:
            if self.animation_direction == 0:
                self.move(dirn=0,
                          v=int(func(player=self, dirn=0, distance=int(self.current_moving_velocity)) *
                                math.sqrt(self.sliding_counter / self.max_sliding_time)))
                self.sliding_counter -= 1
            if self.animation_direction == 1:
                self.move(dirn=1,
                          v=int(func(player=self, dirn=1, distance=int(self.current_moving_velocity)) *
                                math.sqrt(self.sliding_counter / self.max_sliding_time)))
                self.sliding_counter -= 1

    def reset_sliding_counter(self):
        self.sliding_counter = self.max_sliding_time

    def stop_sliding(self):
        self.sliding_counter = 1

    def draw(self, g):
        if self.health > 0:
            super(Player, self).draw(g=g)
            pygame.draw.line(g, pygame.Color(231, 24, 55), (self.x, self.y - 5), (self.x + self.frame_width, self.y - 5), 3)
            if self.health > 0:
                pygame.draw.line(g, pygame.Color(45, 175, 20), (self.x, self.y - 5),
                                 (self.x + (self.frame_width * (self.health / 100)), self.y - 5), 3)
            pygame.draw.line(g, pygame.Color(20, 20, 20), (self.x, self.y - 10), (self.x + self.frame_width, self.y - 10),
                             3)
            if self.weapon.durability > 0:
                pygame.draw.line(g, pygame.Color(25, 25, 200), (self.x, self.y - 10),
                                 (self.x + (self.frame_width * (self.weapon.durability / 100)), self.y - 10),
                                 3)
            self.weapon.animation_direction = self.animation_direction
            self.weapon.draw(g=g, x=self.x, y=self.y, width=self.frame_width, height=self.frame_height)
            self.weapon.draw(g=g, x=self.x, y=self.y, width=self.frame_width, height=self.frame_height)
            if self.weapon.hitted_me or self.blood_animation.current_frame > 0:
                self.blood_animation.set_pos(self.x-47, self.y+15)
                self.blood_animation.draw_animation_once(g=g, reset=True)
        else:
            self.death_animation.set_pos(self.x, self.y)
            self.death_animation.draw_animation_once(g=g)

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
            v = self.current_moving_velocity

        if dirn == 0:
            self.animation_direction = 0
            self.x += v
            self.weapon.x += v
        elif dirn == 1:
            self.animation_direction = 1
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
            self.current_moving_velocity = self.moving_velocity_in_air

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
        moving_factor = int(self.current_moving_velocity * 2)
        # when player is not jumping
        if not self.is_jumping:

            # calculate if player is able to fall (vel > 0 means yes)
            vel = func(player=self, dirn=3, distance=int(self.velocity_gravity))

            # if able to fall
            if vel > 0:
                self.stop_sliding()
                self.current_moving_velocity = self.moving_velocity_in_air

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
                    self.shift_df(df=self.solid_df, dirn=0, n=moving_factor)
                    vel = func(player=self, dirn=3, distance=int(self.velocity_gravity))

                    # if falling is then possible
                    if vel > 0:
                        # shift back the df and move to the right so in next cycle the player will continue to fall
                        self.shift_df(df=self.solid_df, dirn=1, n=moving_factor)
                        self.move(dirn=0, v=int(moving_factor))

                    else:
                        # try the same for direction left
                        self.shift_df(df=self.solid_df, dirn=1, n=moving_factor * 2)
                        vel = func(player=self, dirn=3, distance=int(self.velocity_gravity))

                        # if falling is possible after shifting to left, shift df back to original position and move left
                        if vel > 0:
                            self.shift_df(df=self.solid_df, dirn=0, n=moving_factor)
                            self.move(dirn=1, v=int(moving_factor))

                        # otherwise it means that the player is standing on its feet, so he is landed correctly
                        # so stop falling and reset the parameters
                        else:
                            self.shift_df(df=self.solid_df, dirn=0, n=moving_factor)
                            self.landed = True
                            self.block_x_axis = False
                            self.is_falling = False
                            self.velocity_gravity = 1
                            self.current_moving_velocity = self.moving_velocity_on_ground

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
