import json
import os
import time
from copy import copy
import datetime

import pandas as pd
import pygame

import multiprocessing

from src.game.canvas import Canvas

from src.game import canvas, weapon
from src.game.map import Map
from src.game import player as Player
from src.game import weapon as Weapon

wrk_dir = os.path.abspath(os.path.dirname(__file__))
config_file = wrk_dir + r'\configuration.json'
basic_map = "\\".join(str(wrk_dir).split("\\")[:-1]) + r"\basicmap"
platformmap = "\\".join(str(wrk_dir).split("\\")[:-1]) + r"\platformmap"
schneemap = "\\".join(str(wrk_dir).split("\\")[:-1]) + r"\schneemap"
map_names_dict = {"basicmap": basic_map,
                  "platformmap": platformmap,
                  "schneemap": schneemap}

clock = pygame.time.Clock()
pygame.font.init()


class Game:

    def __init__(self, w, h, conn, process):
        self.counter = 0
        self.conn = conn
        self.process = process
        self.timer = datetime.datetime.now()
        self.update_background_process()
        self.id = int(self.data['id'])

        # pygame.init()
        pygame.display.set_icon(pygame.image.load(wrk_dir + r"\..\stick_wars_logo.png"))
        self.width = w
        self.height = h
        self.canvas = canvas.Canvas(self.width, self.height, str(self.id) + "Stick  Wars")
        self.printLoading(0.1)
        # self.map = Map(self, map_names_dict[self.data['map_name']])
        self.map = Map(self, map_names_dict[self.data["metadata"]["map"]])
        self.printLoading(0.2)
        print("MAP:", self.data["metadata"]["map"])
        print("SPAWNPOINTS:", self.data["metadata"]["spawnpoints"])
        self.online = [False, False, False, False]
        self.this_player_pos = [700, 50]
        self.pos = [[100, 100], [200, 100], [300, 100], [400, 100]]
        self.player_frames = [[0, False, 1], [0, False, 1], [0, False, 1], [0, False, 1]]
        self.weapon_frames = [[0, False, 1], [0, False, 1], [0, False, 1], [0, False, 1]]
        self.printLoading(0.5)
        self.playerList = [
            Player.Player(0, self.data["metadata"]["spawnpoints"]["0"], directory=self.map.player_uris[0]),
            Player.Player(1, self.data["metadata"]["spawnpoints"]["1"], directory=self.map.player_uris[1]),
            Player.Player(2, self.data["metadata"]["spawnpoints"]["2"], directory=self.map.player_uris[2]),
            Player.Player(3, self.data["metadata"]["spawnpoints"]["3"], directory=self.map.player_uris[3])]
        self.playerList[self.id].set_velocity(self.data["metadata"]["spawnpoints"]["velocity"])
        self.printLoading(0.7)
        self.min_timer = 0
        self.max_timer = 0
        self.counter_reset_timer = 0
        self.time_total = 0
        self.new_fps_timer = datetime.datetime.now()
        self.show_scoreboard = False

    def run(self):
        """
        the core method of the game containing the game loop
        """
        # pygame stuff
        # clock = pygame.time.Clock()
        run = True

        # just for comfort
        id = self.id

        # game loop
        while run:
            fps_timer = datetime.datetime.now()
            # timer = datetime.datetime.now()

            # pygame stuff for the max fps
            clock.tick(100)
            # print()
            # print("FPS:", self.update_fps())
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.K_ESCAPE:
                    run = False

            if self.playerList[id].is_alive():
                # check if weapon is destroyed and give player fists if true
                if self.playerList[id].weapon.destroyed and not self.playerList[id].weapon.animation_running:
                    self.playerList[id].weapon = weapon.Weapon(weapon.WeaponType.Fist,
                                                               [self.playerList[id].x, self.playerList[id].y],
                                                               self.playerList[id].weapon_path[
                                                                   weapon.WeaponType.Fist.name])
                Weapon.Weapon.check_hit(self.playerList[id], self.playerList[:self.id] + self.playerList[self.id + 1:],
                                        self.map.solid_df, self.canvas.get_canvas())
                if self.playerList[id].y > self.height:
                    self.playerList[id].health = 0
                    self.playerList[id].death_time = datetime.datetime.now()
                    self.playerList[id].killed_by[4] += 1
                # handling pygame events

                # print("Handling Events:", datetime.datetime.now() - timer)
                # timer = datetime.datetime.now()

                # get the key presses
                keys = pygame.key.get_pressed()

                # scoreboard
                if keys[pygame.K_TAB]:
                    self.show_scoreboard = True
                else:
                    self.show_scoreboard = False

                # blocking
                if keys[pygame.K_m]:
                    self.playerList[id].start_blocking()
                else:
                    self.playerList[id].stop_blocking()

                # Hit
                if keys[pygame.K_s]:
                    # Check if Player can use his weapon
                    if self.playerList[id].weapon.can_hit():
                        # Check if an enemy player is in range
                        self.playerList[id].weapon.hit()
                        self.playerList[id].weapon.start_animation_in_direction(self.playerList[id].animation_direction)

                if keys[pygame.K_d] and not self.playerList[id].block_x_axis:
                    if self.playerList[id].landed:
                        self.playerList[id].start_animation_in_direction(0)
                    self.playerList[id].move(0, self.nextToSolid(self.playerList[id], 0,
                                                                 self.playerList[id].current_moving_velocity))
                    self.playerList[id].reset_sliding_counter()

                elif keys[pygame.K_a] and not self.playerList[id].block_x_axis:
                    if self.playerList[id].landed:
                        self.playerList[id].start_animation_in_direction(1)
                    self.playerList[id].move(1, self.nextToSolid(self.playerList[id], 1,
                                                                 self.playerList[id].current_moving_velocity))
                    self.playerList[id].reset_sliding_counter()

                elif self.data["metadata"]["map"] == "schneemap":
                    self.playerList[id].keep_sliding(func=self.nextToSolid)

                # Jump
                if keys[pygame.K_SPACE] or self.playerList[id].is_jumping or keys[pygame.K_w]:
                    self.playerList[id].stop_sliding()
                    self.playerList[id].stop_animation()
                    self.playerList[id].jump(func=self.nextToSolid)

                # gravity
                self.playerList[id].gravity(func=self.nextToSolid)

                # print("Handling Keys:", datetime.datetime.now() - timer)
                # timer = datetime.datetime.now()
            else:
                # if player is dead, respawn
                if datetime.datetime.now() - self.playerList[id].death_time > datetime.timedelta(seconds=3):
                    self.playerList[id] = Player.Player(int(id), self.data["metadata"]["spawnpoints"][str(id)],
                                                        killed_by=self.playerList[id].killed_by,
                                                        directory=self.map.player_uris[int(id)])
                    self.playerList[self.id].set_velocity(self.data["metadata"]["spawnpoints"]["velocity"])

            # Send Data about this player and get some over the others als reply
            self.send_to_background_process()
            # print("Handling send:", datetime.datetime.now() - timer)
            # timer = datetime.datetime.now()
            self.update_background_process()
            # print("Handling update:", datetime.datetime.now() - timer)
            # timer = datetime.datetime.now()

            # sync data
            self.player_frames, self.weapon_frames, health, killed, pos, con = self.parse()
            for i, (data_player, data_weapon, health, killed, pos, con) in enumerate(
                    zip(self.player_frames, self.weapon_frames, health, killed, pos, con)):
                self.playerList[i].current_frame = data_player[0]
                self.playerList[i].animation_running = data_player[1]
                self.playerList[i].animation_direction = data_player[2]
                if self.playerList[i].weapon.weapon_type != weapon.WeaponType.getObj(data_weapon[3]):
                    self.playerList[i].weapon = weapon.Weapon(weapon.WeaponType.getObj(data_weapon[3]),
                                                              [self.playerList[i].x, self.playerList[i].y],
                                                              self.playerList[i].weapon_path[
                                                                  weapon.WeaponType.getObj(data_weapon[3]).name])
                self.playerList[i].weapon.durability = data_weapon[4]
                self.playerList[i].weapon.current_frame = data_weapon[0]
                self.playerList[i].weapon.animation_running = data_weapon[1]
                self.playerList[i].weapon.animation_direction = data_weapon[2]
                self.playerList[i].health = health
                self.playerList[i].killed_by = killed
                self.playerList[i].x, self.playerList[i].y = pos
                self.playerList[i].is_connected = con

            for p in self.playerList:
                if p == self.playerList[id]:
                    continue
                p.refresh_solids()
            # print("Handling pos parsing:", datetime.datetime.now() - timer)
            # timer = datetime.datetime.now()

            # Draw Map
            self.map.draw(self.canvas.get_canvas())
            # Draw Players
            for p in self.playerList:
                if p.is_connected:
                    p.draw(self.canvas.get_canvas())
            if not self.playerList[id].is_alive():
                # Draw Death-screen
                self.canvas.get_canvas().blit(pygame.image.load(wrk_dir + '\\wasted.png').convert_alpha(), (0, 0))
            if self.show_scoreboard:
                # Generate Scoreboard
                can = self.canvas.get_canvas()
                scoreboard = pygame.image.load(wrk_dir + '\\Scoreboard.png').convert_alpha()
                Canvas.draw_text(scoreboard, "Player 0", 20, (255, 0, 255), 40, 57)
                Canvas.draw_text(scoreboard, "Player 1", 20, (226, 200, 0), 40, 93)
                Canvas.draw_text(scoreboard, "Player 2", 20, (160, 32, 240), 40, 128)
                Canvas.draw_text(scoreboard, "Player 3", 20, (64, 224, 208), 40, 165)
                Canvas.draw_text(scoreboard, str(self.data["metadata"]["scoreboard"]["0"][0]), 20, (255, 255, 255), 178,
                                 57)
                Canvas.draw_text(scoreboard, str(self.data["metadata"]["scoreboard"]["1"][0]), 20, (255, 255, 255), 178,
                                 93)
                Canvas.draw_text(scoreboard, str(self.data["metadata"]["scoreboard"]["2"][0]), 20, (255, 255, 255), 178,
                                 128)
                Canvas.draw_text(scoreboard, str(self.data["metadata"]["scoreboard"]["3"][0]), 20, (255, 255, 255), 178,
                                 165)
                Canvas.draw_text(scoreboard, str(self.data["metadata"]["scoreboard"]["0"][1]), 20, (255, 255, 255), 310,
                                 57)
                Canvas.draw_text(scoreboard, str(self.data["metadata"]["scoreboard"]["1"][1]), 20, (255, 255, 255), 310,
                                 93)
                Canvas.draw_text(scoreboard, str(self.data["metadata"]["scoreboard"]["2"][1]), 20, (255, 255, 255), 310,
                                 128)
                Canvas.draw_text(scoreboard, str(self.data["metadata"]["scoreboard"]["3"][1]), 20, (255, 255, 255), 310,
                                 165)
                # Draw the Scoreboard
                can.blit(scoreboard, (100, 100))
            # Update Canvas
            self.canvas.update()
            # print("Handling redraw:", datetime.datetime.now() - timer)
            # timer = datetime.datetime.now()

            self.send_to_background_process()

            this_time = int((datetime.datetime.now() - fps_timer).microseconds)
            delay = 0.0

            if self.counter_reset_timer > 0 and \
                    round((self.time_total + this_time) / 1000, 3) / (self.counter_reset_timer + 1) < 16:
                delay = (self.counter_reset_timer + 1) * 16 - round((self.time_total + this_time) / 1000, 3)

            elif self.counter_reset_timer == 0:
                delay = 16 - this_time / 1000

            wait_time = datetime.datetime.now()
            while datetime.datetime.now() - wait_time < datetime.timedelta(microseconds=(delay - 0.5) * 1000):
                continue
                # print((datetime.datetime.now() - wait_time).microseconds / 1000)
            # timer = datetime.datetime.now()

            # print("TOTAL TIME:", datetime.datetime.now() - fps_timer)

            this_time = int((datetime.datetime.now() - fps_timer).microseconds)
            self.counter_reset_timer += 1
            self.time_total += this_time

            if self.counter_reset_timer == 10:
                self.counter_reset_timer = 0
                self.time_total = 0
                self.new_fps_timer = datetime.datetime.now()

        self.process.kill()  # muss noch übergeben werden
        pygame.quit()

    def printLoading(self, percent):
        """
        displayes a loading screen
        :param percent: percetige to display
        """
        pygame.draw.line(surface=self.canvas.get_canvas(),
                         color=pygame.Color(255, 255, 255),
                         start_pos=(480, 430),
                         end_pos=(1100, 430),
                         width=110)
        pygame.draw.line(surface=self.canvas.get_canvas(),
                         color=pygame.Color(0, 255, 0),
                         start_pos=(480, 430),
                         end_pos=(480 + (1100 - 480) * percent, 430),
                         width=110)
        self.canvas.get_canvas().blit(pygame.image.load(wrk_dir + '\\Loadingscreen.png').convert_alpha(), (0, 0))
        self.canvas.update()

    def update_background_process(self):
        # if datetime.datetime.now() - self.timer >= datetime.timedelta(seconds=1):
        #     self.timer = datetime.datetime.now()
        #     print("count in Menu:", self.counter)
        #     self.counter = 0
        # else:
        #     self.counter += 1
        new_data = None
        # while not self.conn.poll():
        #     continue
        while self.conn.poll():
            new_data = self.conn.recv()
        if type(new_data) == str:
            self.data = json.loads(new_data)

    def send_to_background_process(self):
        temp_data = {
            "position": [int(self.playerList[int(self.data["id"])].x), int(self.playerList[int(self.data["id"])].y)],
            "player_frame": [self.playerList[int(self.data['id'])].current_frame,
                             self.playerList[int(self.data['id'])].animation_running,
                             self.playerList[int(self.data['id'])].animation_direction],
            "weapon_frame": [self.playerList[int(self.data['id'])].weapon.current_frame,
                             self.playerList[int(self.data['id'])].weapon.animation_running,
                             self.playerList[int(self.data['id'])].weapon.animation_direction,
                             self.playerList[int(self.data['id'])].weapon.weapon_type.name,
                             self.playerList[int(self.data['id'])].weapon.durability],
            "health": self.playerList[int(self.data['id'])].health,
            "killed_by": self.playerList[int(self.data['id'])].killed_by
        }
        self.conn.send(temp_data)

    @staticmethod
    def update_fps():
        fps = str(int(clock.get_fps()))
        return fps

    def parse(self):
        """
        extracts positions from server data
        :return: list of player frames [current_frame, animation_running, animation_direction],
                 list of weapon frames[current_frame, animation_running, animation_direction]
        """
        erg_player = []
        erg_weapon = []
        erg_health = []
        erg_killed_by = []
        erg_pos = []
        erg_con = []
        for key, value in self.data.items():
            # since a fifth dictionary entry named 'id' is added for the player id, ignore this key/entry
            if key != "id" and key != "metadata":
                for key2, value2 in value.items():
                    if key2 == "player_frame":
                        if key != str(self.id):
                            erg_player.append(value2)
                        else:
                            erg_player.append([self.playerList[int(self.data["id"])].current_frame,
                                               self.playerList[int(self.data["id"])].animation_running,
                                               self.playerList[int(self.data["id"])].animation_direction])
                    elif key2 == "weapon_frame":
                        if key != str(self.id):
                            erg_weapon.append(value2)
                        else:
                            erg_weapon.append([self.playerList[int(self.data["id"])].weapon.current_frame,
                                               self.playerList[int(self.data["id"])].weapon.animation_running,
                                               self.playerList[int(self.data["id"])].weapon.animation_direction,
                                               self.playerList[int(self.data["id"])].weapon.weapon_type.name,
                                               self.playerList[int(self.data["id"])].weapon.durability])
                    elif key2 == "health":
                        if key != str(self.id):
                            erg_health.append(value2)
                        else:
                            erg_health.append(self.playerList[int(self.data["id"])].health)
                    elif key2 == "killed_by":
                        if key != str(self.id):
                            erg_killed_by.append(value2)
                        else:
                            erg_killed_by.append(self.playerList[int(self.data["id"])].killed_by)
                    elif key2 == "position":
                        if key != str(self.id):
                            erg_pos.append(value2)
                        else:
                            erg_pos.append([int(self.playerList[int(self.data["id"])].x),
                                            int(self.playerList[int(self.data["id"])].y)])
                    elif key2 == "connected":
                        if key != str(self.id):
                            erg_con.append(value2)
                        else:
                            erg_con.append(True)
            else:
                continue
        return erg_player, erg_weapon, erg_health, erg_killed_by, erg_pos, erg_con

    def nextToSolid(self, player, dirn, distance):
        """
        calculates the distance to the nearest object in one direction in a range
        :param player: the current player
        :param dirn: the direction
        :param distance: the range in which to check
        :return: integer representing the distance to the next object within the range
        """
        # first combining all solid pixels in one dataframe
        # other_players = self.playerList[:self.id] + self.playerList[self.id + 1:]
        solid_pixels_df = copy(self.map.solid_df)
        # for op in other_players:
        #     solid_pixels_df = pd.concat([solid_pixels_df, op.solid_df])
        # getting copy of the players solid dataframe
        simulated_player = copy(player.solid_df)
        erg = 0

        Player.Player.shift_df(simulated_player, dirn, distance)
        if pd.merge(simulated_player, solid_pixels_df, how='inner', on=['x', 'y']).empty:
            erg = distance
            return erg
        Player.Player.shift_df(simulated_player, dirn, -distance)

        # checking for each pixel if a move ment would cause a collision
        for _ in range(distance):
            Player.Player.shift_df(simulated_player, dirn, 1)
            if not pd.merge(simulated_player, solid_pixels_df, how='inner', on=['x', 'y']).empty:
                return erg
            erg += 1
        return erg
