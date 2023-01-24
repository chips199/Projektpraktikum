import datetime
from copy import copy
from typing import List, Tuple
import pandas as pd
import pygame
from src.game import weapon


class Player():
    width, height = 50, 100
    last_jump = datetime.datetime.now()
    height_jump = 200
    status_jump = 0
    is_connected = False
    mousepos = (0, 0)
    user_weapon = weapon.Weapon(100, 15, 15, 1)
    health = 100

    def __init__(self, startx, starty, game, image=None, color=(255, 0, 0)):
        self.falling_time = datetime.datetime.now()
        self.jumping_time = datetime.datetime.now()
        self.x = startx
        self.y = starty
        self.game = game
        self.velocity = 4
        self.velocity_gravity = 1
        self.velocity_jumping = self.max_jumping_speed = 12
        self.velocity_time = 50
        self.landed = False
        self.is_jumping = False
        self.is_falling = True
        self.block_x_axis = False
        self.color = color
        self.weapon = weapon
        solid = []  # type: List[Tuple[int, int]]
        relativ_solids = []  # type: List[Tuple[int, int]]
        try:
            self.image = pygame.image.load(image)  # .convert_alpha()
            # self.image.convert_alpha()
            self.edge_surface = pygame.transform.laplacian(self.image).convert_alpha()
            alpha_array = pygame.surfarray.pixels_alpha(self.edge_surface)
            alpha_array = alpha_array.swapaxes(0, 1)
            for yi, y in enumerate(alpha_array):
                for xi, x in enumerate(y):
                    if x > 200:
                        solid.append((xi + self.x, yi + self.y))
                        relativ_solids.append((xi, yi))
        except:
            self.image = "no image found"  # type: ignore[assignment]
            # horizontal edges
            for x in range(self.width):
                solid.append((x + self.x, self.y))
                relativ_solids.append((x, self.y))
                solid.append((x + self.x, self.y + self.height))
                relativ_solids.append((x, self.y + self.height))
            # vertical edges
            for y in range(self.height):
                solid.append((self.x, self.y + y))
                relativ_solids.append((self.x, y))
                solid.append((self.x + self.width, self.y + y))
                relativ_solids.append((self.x + self.width, y))
        self.relativ_solids_df = pd.DataFrame(relativ_solids, columns=['x', 'y'])
        self.solid_df = pd.DataFrame(solid, columns=['x', 'y'])

    def draw(self, g):
        """
        displays a player to the canvas
        :param g: pygame canvas
        """
        # draw Player
        player_rec = pygame.Rect(self.x, self.y, self.width, self.height)
        if type(self.image) == pygame.Surface:
            g.blit(self.image, player_rec)
        else:
            pygame.draw.rect(g, self.color, player_rec, 0)

        # draw weapon
        # ...wip...

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
            self.x += v
        elif dirn == 1:
            self.x -= v
        elif dirn == 2:
            self.y -= v
        else:
            self.y += v
        self.solid_df = Player.shift_df(self.solid_df, dirn, v)

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
                elif datetime.datetime.now() - self.jumping_time > datetime.timedelta(milliseconds=self.velocity_time):
                    self.velocity_jumping -= 1
                    # reset timer to current time
                    self.jumping_time = datetime.datetime.now()

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
                elif datetime.datetime.now() - self.falling_time > datetime.timedelta(milliseconds=self.velocity_time):
                    self.velocity_gravity += 1
                    # reset timer to current time
                    self.falling_time = datetime.datetime.now()

                    # limit the falling speed to it's maximum
                    if self.velocity_gravity > self.max_jumping_speed:
                        self.velocity_gravity = self.max_jumping_speed

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
