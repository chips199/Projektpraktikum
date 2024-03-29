import math
from copy import copy
import datetime

import pygame.draw

from src.game.gamelogic import weapon
from src.game.gamelogic.animated import Animated
from src.game.gamelogic.sounds import Sounds
from src.game.gamelogic.weapon_shot import WeaponShot


class Player(Animated):
    last_jump = datetime.datetime.now()
    height_jump = 200
    status_jump = 0
    is_connected = False
    health = 100

    def __init__(self, pid, *args, killed_by=None, **kwargs):
        super(Player, self).__init__(*args, **kwargs)

        if killed_by is None:
            killed_by = [0, 0, 0, 0, 0]

        self.map = self.get_map(self.directory)
        self.falling_time = datetime.datetime.now()
        self.jumping_time = datetime.datetime.now()
        self.id = pid
        self.velocity = 7
        self.current_moving_velocity = 7
        self.moving_velocity_on_ground = self.moving_velocity_in_air = 7
        self.velocity_gravity = 1
        self.velocity_jumping = self.max_jumping_speed = 20
        self.velocity_time = 15
        self.landed = False
        self.is_jumping = False
        self.is_falling = True
        self.block_x_axis = False
        self.is_blocking = False
        self.moving_on_edge = False
        # self.cut_frames(2)
        self.killed_by = killed_by
        self.death_time = datetime.datetime.now()
        # self.color = color
        self.weapon = weapon
        # The shots of the long distance weapon
        self.weapon_shots = []
        self.velocity_counter = 0
        self.velocity_counter2 = 0
        self.sliding_frame_counter = self.max_sliding_frames = 50
        map_dir = "\\".join(str(self.directory).split('\\')[:-3])

        # Start Weapon
        self.weapon_path = {
            weapon.WeaponType.Fist.name: map_dir + f"\\waffen\\faeuste\\animation\\fists_{self.get_color(self.directory)}_animation",
            weapon.WeaponType.Sword.name: map_dir + f"\\waffen\\schwert\\animation\\sword_hold_animation_{self.get_color(self.directory)}",
            weapon.WeaponType.Laser.name: map_dir + f"\\waffen\\laser\\animation\\laser_hold_{self.get_color(self.directory)}"
        }
        self.weapon = weapon.Weapon(weapon.WeaponType.Fist, map_dir + r"\waffen\faeuste", [self.x, self.y],
                                    self.weapon_path[weapon.WeaponType.Fist.name])

        self.death_animation = Animated(start=[0, 0],
                                        directory=map_dir + f"\\player\\death_animation\\death_animation_{self.get_color(self.directory)}")
        self.death_animation.double_frames(2)
        self.blood_animation = Animated(start=[0, 0], directory=map_dir + r"\player\blood_animation")
        self.blood_animation.double_frames(factor=2)
        self.shield_right = pygame.image.load(map_dir + r"\waffen\shield\shield.png").convert_alpha()
        self.shield_left = pygame.transform.flip(self.shield_right, True, False)
        self.blocking_start_time = datetime.datetime.now().timestamp()
        self.last_block = datetime.datetime.now().timestamp()
        self.renew_shield_cooldown = 2
        self.hold_shield_cooldown = 1
        self.blood_frame = None

        # Sound effects:
        # Load sound effect hurt
        self.sound_hurt = Sounds(map_dir + r"\sounds\hurt_sound.mp3", 1.0)
        # Load sound effect die
        self.sound_die_played = False
        self.sound_die = Sounds(map_dir + r"\sounds\die_sound.mp3", 0.5)

    def set_velocity(self, data=(1, 1, 0, 0)) -> None:
        """
        Set the velocity of the player.

        Args:
            data: A tuple containing the following data in this order:
                - Ground moving velocity
                - Airborne moving velocity
                - Jumping velocity
                - Velocity counter
        """
        self.moving_velocity_on_ground = data[0]
        self.moving_velocity_in_air = data[1]
        self.velocity_jumping = self.max_jumping_speed = data[2]
        self.velocity_counter = data[3]

    def keep_sliding(self, func):
        """
        If the player has landed or is moving on the edge and not falling and still has sliding frames left,
        moves the player in the current direction, with distance calculated in the handed over function
        distance is calculated with math.sqrt to reach a quadratic behaviour instead of linear behaviour
        """
        # landed needed when player is landed, and moving_on_edge for when player is sliding down hill on snowmap
        if (self.landed or self.moving_on_edge) and \
                not self.is_falling and \
                self.sliding_frame_counter > 1:
            if self.animation_direction == 0:
                self.move(dirn=0,
                          v=int(func(player=self, dirn=0, distance=int(self.current_moving_velocity)) *
                                math.sqrt(self.sliding_frame_counter / self.max_sliding_frames)))
                self.sliding_frame_counter -= 1
            if self.animation_direction == 1:
                self.move(dirn=1,
                          v=int(func(player=self, dirn=1, distance=int(self.current_moving_velocity)) *
                                math.sqrt(self.sliding_frame_counter / self.max_sliding_frames)))
                self.sliding_frame_counter -= 1

    def reset_sliding_counter(self):
        """
        Reset the sliding frame counter to the maximum sliding frames
        """
        self.sliding_frame_counter = self.max_sliding_frames

    def stop_sliding(self):
        """
        Stop the sliding by setting the sliding frame counter to 1
        """
        self.sliding_frame_counter = 1

    def draw(self, g: pygame.Surface) -> None:
        """
        Draws the player onto the given surface.
        """
        if self.health > 0:
            # Call the superclass draw method to draw the player's sprite
            super(Player, self).draw(g=g)

            self.death_animation.current_frame = 0

            # Draw the health bar
            pygame.draw.line(surface=g,
                             color=pygame.Color(231, 24, 55),
                             start_pos=(self.x, self.y - 5),
                             end_pos=(self.x + self.frame_width, self.y - 5),
                             width=3)
            if self.health > 0:
                pygame.draw.line(surface=g,
                                 color=pygame.Color(45, 175, 20),
                                 start_pos=(self.x, self.y - 5),
                                 end_pos=(self.x + (self.frame_width * (self.health / 100)), self.y - 5),
                                 width=3)

            # Draw the weapon durability bar
            pygame.draw.line(surface=g,
                             color=pygame.Color(20, 20, 20),
                             start_pos=(self.x, self.y - 10),
                             end_pos=(self.x + self.frame_width, self.y - 10),
                             width=3)
            if self.weapon.durability > 0:
                pygame.draw.line(surface=g,
                                 color=pygame.Color(25, 25, 200),
                                 start_pos=(self.x, self.y - 10),
                                 end_pos=(self.x + (self.frame_width * (self.weapon.durability / 100)), self.y - 10),
                                 width=3)

            # Draw the shield if the player
            if self.is_blocking:
                player_rec = pygame.Rect(self.x - 1, self.y - 3, self.frame_width, self.frame_height)
                g.blit(self.shield_right, player_rec)
                player_rec = pygame.Rect(self.x - 42, self.y - 3, self.frame_width, self.frame_height)
                g.blit(self.shield_left, player_rec)

            self.weapon.animation_direction = self.animation_direction
            self.weapon.draw(g=g, x=self.x, y=self.y, width=self.frame_width, height=self.frame_height)

            # blood splash animation
            if self.blood_frame is not None:
                y = 0
                if self.map == "basic":
                    y = 40
                if self.map == "space":
                    y = 50
                if self.map == "snow":
                    y = 55
                if self.blood_animation.current_frame < self.blood_animation.frame_count:
                    self.blood_frame = self.blood_animation.current_frame
                else:
                    self.blood_frame = None
                self.blood_animation.animation_direction = self.animation_direction
                if self.animation_direction == 0:
                    self.blood_animation.set_pos(self.x + 4, self.y + y)
                else:
                    self.blood_animation.set_pos(self.x + 30, self.y + y)
                self.blood_animation.draw_animation_once(g=g, reset=True)

        # death animation
        else:
            self.death_animation.set_pos(self.x, self.y)
            self.death_animation.draw_animation_once(g=g)
            # Play sound effect die
            if not self.sound_die_played:
                self.sound_die.play()
                self.sound_die_played = True

    def move(self, dirn, v=-99):
        """
        :param dirn: 0 - 3 (right, left, up, down)
        :param    v: velocity
        :return: None
        """
        # set speed to current_moving_velocity value if v is -99
        if v == -99:
            v = self.current_moving_velocity

        if dirn == 0:  # Move right
            self.animation_direction = 0
            self.x += v
            self.weapon.x += v
        elif dirn == 1:  # Move left
            self.animation_direction = 1
            self.x -= v
            self.weapon.x -= v
        elif dirn == 2:  # Move up
            self.y -= v
            self.weapon.y -= v
        else:  # Move down
            self.y += v
            self.weapon.y += v

        # Adjust dataframe of the player according to the movement
        self.solid_df = self.shift_df(self.solid_df, dirn, v)  # type:ignore[has-type]

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
                    self.landed = False

                # after certain amount of frames, decrease jumping speed
                if self.velocity_counter2 >= self.velocity_counter:
                    self.velocity_jumping -= 1
                    # reset frame counter to 0
                    self.velocity_counter2 = 0

                # otherwise just increase frame counter
                else:
                    self.velocity_counter2 += 1

                # jump with speed calculated in func()
                self.move(2, vel)

            # when jumping speed reaches 0 or jumping is not possible, stop jumping
            if vel <= 0:
                self.is_jumping = False
                self.velocity_jumping = self.max_jumping_speed

    def start_blocking(self):
        """
        Begin blocking if not already blocking and the renew shield cooldown is over.
        Otherwise, stop blocking.
        """
        # If not already blocking and the renew shield cooldown is over, start blocking
        if not self.is_blocking and datetime.datetime.now().timestamp() > self.last_block + self.renew_shield_cooldown:
            self.blocking_start_time = datetime.datetime.now().timestamp()

        # If still holding shield, set blocking to True and block player moving on x-axis
        if datetime.datetime.now().timestamp() < self.blocking_start_time + self.hold_shield_cooldown:
            self.is_blocking = True
            self.block_x_axis = True

        # Otherwise, stop blocking
        else:
            self.stop_blocking()

    def stop_blocking(self):
        """
        Stop the blocking state and reset relevant variables.
        Set is_blocking to False and reset block_x_axis to False so player is allowed to move on x-axis again.
        """
        # If character is currently blocking, update last_block time to current time and subtract the
        # hold_shield_cooldown from blocking_start_time to simulate that the max holding time is reached
        if self.is_blocking:
            self.last_block = datetime.datetime.now().timestamp()
            self.blocking_start_time -= self.hold_shield_cooldown
        self.is_blocking = False
        self.block_x_axis = False

    def is_alive(self):
        """
        Returns whether the player is still alive
        :return: boolean: True: Is alive;  False: Isn't alive
        """
        return self.health > 0

    def refresh_solids(self):
        """
        Refresh the position of solids in the `solid_df` DataFrame by adding the current position
        of the element container to their position values.
        """
        # Create a new DataFrame with the same values as `relativ_solids_df`
        # (the position of each solid relative to the element container)
        new_pos = copy(self.relativ_solids_df)

        # Add the current position of the element container to the x and y values of each solid
        new_pos['x'] = new_pos['x'].map(lambda x: x + self.x)
        new_pos['y'] = new_pos['y'].map(lambda y: y + self.y)

        # Update the `solid_df` DataFrame with the new positions
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

                # after certain amount of frames, decrease jumping speed
                elif self.velocity_counter2 >= self.velocity_counter:
                    self.velocity_gravity += 1
                    self.velocity_counter2 = 0

                    # limit the falling speed to it's maximum
                    if self.velocity_gravity > self.max_jumping_speed:
                        self.velocity_gravity = self.max_jumping_speed

                else:
                    self.velocity_counter2 += 1

                # move player down with speed calculated in func()
                self.move(dirn=3, v=int(vel))
                if vel > 5:
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
                        self.move(dirn=3, v=int(vel))
                        # to be able to slide on snow-map after ending the hill
                        self.moving_on_edge = True
                        self.reset_sliding_counter()

                    else:
                        # try the same for direction left
                        self.shift_df(df=self.solid_df, dirn=1, n=moving_factor * 2)
                        vel = func(player=self, dirn=3, distance=int(self.velocity_gravity))

                        # if falling is possible after shifting to left, shift df back to original position and move left
                        if vel > 0:
                            self.shift_df(df=self.solid_df, dirn=0, n=moving_factor)
                            self.move(dirn=1, v=int(moving_factor))
                            self.move(dirn=3, v=int(vel))
                            # to be able to slide on snow-map after ending the hill
                            self.moving_on_edge = True
                            self.reset_sliding_counter()

                        # otherwise it means that the player is standing on its feet, so he is landed correctly
                        # so stop falling and reset the parameters
                        else:
                            self.shift_df(df=self.solid_df, dirn=0, n=moving_factor)
                            self.landed = True
                            self.block_x_axis = False
                            self.is_falling = False
                            self.moving_on_edge = False
                            self.velocity_gravity = 1
                            self.current_moving_velocity = self.moving_velocity_on_ground

    @staticmethod
    def get_color(p):
        """
        Returns the color of the player
        param: p: Player
        """
        if p.__contains__("magenta"):
            return "magenta"
        elif p.__contains__("orange"):
            return "orange"
        elif p.__contains__("purple"):
            return "purple"
        else:
            return "turquoise"

    @staticmethod
    def get_map(p: str) -> str:
        """
        Return the name of the map based on the given string parameter.

        :param p: String parameter that contains the name of the map
        :return: Name of the map, either "basic", "space", "snow", or "unknown map" if the name is not recognized

        """
        if p.__contains__("basic"):
            return "basic"
        elif p.__contains__("space"):
            return "space"
        elif p.__contains__("snow"):
            return "snow"
        else:
            return "unknown map"

    @staticmethod
    def get_color_rgb(p):
        """
        Returns the color of the player in rgb
        param: p: Player
        """
        if p.directory.__contains__("magenta"):
            return pygame.Color(227, 0, 113)  # magenta
        elif p.directory.__contains__("orange"):
            return pygame.Color(254, 174, 24)  # orange
        elif p.directory.__contains__("purple"):
            return pygame.Color(159, 2, 238)  # purple
        else:
            return pygame.Color(0, 195, 150)  # turquoise

    def add_shot(self):
        """
        Starts a new shot from a ranged weapon
        """
        # Direction of the shot
        shot_direction = self.animation_direction
        # Left
        if self.animation_direction == 0:
            shot_direction = 1
        # Right
        elif self.animation_direction == 1:
            shot_direction = -1
        # determine start position from shot
        pos = self.weapon.get_position_for_weapon_shot(x=self.x, y=self.y, width=self.frame_width, height=self.frame_height)
        # Add shot to array
        self.weapon_shots.append(
            WeaponShot(pos, self.weapon.get_shot_speed(), Player.get_color_rgb(self), shot_direction,
                       self.weapon.get_weapon_damage()))
