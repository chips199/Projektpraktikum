import json
import os
from copy import copy
import datetime
import time
import pandas as pd
import pygame
import math
from src.game.gamelogic.animated import Animated
from src.game.gamelogic.canvas import Canvas

from src.game.gamelogic import canvas, weapon_shot
from src.game.gamelogic.map import Map
from src.game.gamelogic import player as player
from src.game.gamelogic import weapon as weapon
from src.game.gamelogic.sounds import Sounds

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

    def __init__(self, w, h, conn, process, data={}):
        self.data = data  # type:ignore[var-annotated]
        self.kills_to_win = 5
        self.counter = 0
        self.conn = conn
        self.process = process
        self.timer = datetime.datetime.now()
        self.initialize_game_data()
        self.id = int(self.data['id'])

        # Status of the music
        self.music_on = True

        # pygame.init()
        # time.sleep(0.5)
        pygame.display.set_icon(pygame.image.load(wrk_dir + r"\..\stick_wars_logo.png"))
        self.width = w
        self.height = h
        self.canvas = canvas.Canvas(self.width, self.height, str(self.id) + "Stick  Wars")
        self.print_loading(0.1)
        self.map = Map(self, map_names_dict[self.data["metadata"]["map"]])
        self.print_loading(0.2)
        print("MAP:", self.data["metadata"]["map"])
        print("SPAWNPOINTS:", self.data["metadata"]["spawnpoints"])
        self.online = [False, False, False, False]
        self.this_player_pos = [700, 50]
        self.pos = [[100, 100], [200, 100], [300, 100], [400, 100]]
        self.player_frames = [[0, False, 1], [0, False, 1], [0, False, 1], [0, False, 1]]
        self.weapon_frames = [[0, False, 1], [0, False, 1], [0, False, 1], [0, False, 1]]
        self.print_loading(0.5)
        self.playerList = [
            player.Player(0, self.data["metadata"]["spawnpoints"]["0"], directory=self.map.player_uris[0]),
            player.Player(1, self.data["metadata"]["spawnpoints"]["1"], directory=self.map.player_uris[1]),
            player.Player(2, self.data["metadata"]["spawnpoints"]["2"], directory=self.map.player_uris[2]),
            player.Player(3, self.data["metadata"]["spawnpoints"]["3"], directory=self.map.player_uris[3])]
        self.playerList[self.id].set_velocity(self.data["metadata"]["spawnpoints"]["velocity"])
        self.print_loading(0.7)
        self.min_timer = 0
        self.max_timer = 0
        self.counter_reset_timer = 0
        self.time_total = 0
        self.new_fps_timer = datetime.datetime.now()
        self.show_scoreboard = False

        # Sets the start and end time of the game
        self.start_time = datetime.datetime.strptime(self.data["metadata"]["start"], "%d/%m/%Y, %H:%M:%S")
        self.end_time = datetime.datetime.strptime(self.data["metadata"]["end"], "%d/%m/%Y, %H:%M:%S")

        # Sound effects
        self.lost_sound_effect = Sounds(self.map.directory + r"\sounds\lost_sound.mp3", 1.0)
        self.win_sound_effect = Sounds(self.map.directory + r"\sounds\win_sound.mp3", 1.0)


    def run(self):
        """
        the core method of the game containing the game loop
        """
        # pygame stuff
        # clock = pygame.time.Clock()

        # Draw countdown
        while datetime.datetime.now() < self.start_time:
            self.canvas.get_canvas().fill((32, 32, 32))
            self.canvas.draw_text(self.canvas.get_canvas(), str((self.start_time - datetime.datetime.now()).seconds),
                                  300, (255, 255, 255), 700, 300)
            self.canvas.update()
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

                # Restarts the music, when all songs were played
                if event.type == self.map.music.MUSIC_END and self.music_on and not self.map.music.get_status():
                    self.map.music_load()

            if self.playerList[id].is_alive():
                # check if weapon is destroyed and give player fists if true
                if self.playerList[id].weapon.destroyed and not self.playerList[id].weapon.animation_running:
                    self.playerList[id].weapon = weapon.Weapon(weapon.WeaponType.Fist,
                                                               self.map.directory + r"\waffen\faeuste",
                                                               [self.playerList[id].x, self.playerList[id].y],
                                                               self.playerList[id].weapon_path[
                                                                   weapon.WeaponType.Fist.name])
                weapon.Weapon.check_hit(self.playerList[id], self.playerList[:self.id] + self.playerList[self.id + 1:],
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

                # pick up weapon
                if keys[pygame.K_e]:
                    for w in self.map.items:
                        new_weapon = w.getItem(self.playerList[id].solid_df, self.playerList[id].weapon.weapon_type)
                        if new_weapon is not None:
                            weapon_sound_file = "\\".join(str(self.playerList[id].weapon_path[
                                                                  new_weapon.name]).split('\\')[:-2])
                            self.playerList[id].weapon = weapon.Weapon(new_weapon, weapon_sound_file,
                                                                       [self.playerList[id].x, self.playerList[id].y],
                                                                       self.playerList[id].weapon_path[
                                                                           new_weapon.name])
                            break

                # Hit
                if keys[pygame.K_s]:
                    # Check if Player can use his weapon
                    if self.playerList[id].weapon.can_hit():
                        # hit with the weapon
                        self.playerList[id].weapon.hit()
                        # Check if Weapon is a short range weapon
                        if self.playerList[id].weapon.is_short_range_weapon():
                            # Start shot Animation
                            self.playerList[id].weapon.start_animation_in_direction(
                                self.playerList[id].animation_direction)
                        else:
                            # long distance weapon shot
                            self.playerList[id].add_shot()

                # blocking
                if keys[pygame.K_m] or keys[pygame.K_q]:
                    self.playerList[id].start_blocking()
                else:
                    self.playerList[id].stop_blocking()

                if keys[pygame.K_d] and not self.playerList[id].block_x_axis:
                    if self.playerList[id].landed:
                        self.playerList[id].start_animation_in_direction(0)
                    self.playerList[id].move(0, self.next_to_solid(self.playerList[id], 0,
                                                                   self.playerList[id].current_moving_velocity))
                    self.playerList[id].reset_sliding_counter()

                elif keys[pygame.K_a] and not self.playerList[id].block_x_axis:
                    if self.playerList[id].landed:
                        self.playerList[id].start_animation_in_direction(1)
                    self.playerList[id].move(1, self.next_to_solid(self.playerList[id], 1,
                                                                   self.playerList[id].current_moving_velocity))
                    self.playerList[id].reset_sliding_counter()

                elif self.data["metadata"]["map"] == "schneemap":
                    self.playerList[id].keep_sliding(func=self.next_to_solid)

                # Jump
                if keys[pygame.K_SPACE] or self.playerList[id].is_jumping or keys[pygame.K_w]:
                    self.playerList[id].stop_sliding()
                    self.playerList[id].stop_animation()
                    self.playerList[id].jump(func=self.next_to_solid)

                # falling
                self.playerList[id].falling(func=self.next_to_solid)

                # print("Handling Keys:", datetime.datetime.now() - timer)
                # timer = datetime.datetime.now()
            else:
                # if player is dead, respawn
                if datetime.datetime.now() - self.playerList[id].death_time > datetime.timedelta(seconds=3):
                    self.playerList[id] = player.Player(int(id), self.data["metadata"]["spawnpoints"][str(id)],
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
            self.player_frames, self.weapon_frames, health, killed, pos, con, shots, blocking = self.parse()
            for i, (data_player, data_weapon, health, killed, pos, con, shots, blocking) in enumerate(
                    zip(self.player_frames, self.weapon_frames, health, killed, pos, con, shots, blocking)):
                self.playerList[i].current_frame = data_player[0]
                self.playerList[i].animation_running = data_player[1]
                self.playerList[i].animation_direction = data_player[2]
                if self.playerList[i].weapon.weapon_type != weapon.WeaponType.getObj(data_weapon[3]):
                    self.playerList[i].weapon = weapon.Weapon(weapon.WeaponType.getObj(data_weapon[3]),
                                                              self.map.directory + r"\waffen\faeuste",
                                                              [self.playerList[i].x, self.playerList[i].y],
                                                              self.playerList[i].weapon_path[
                                                                  weapon.WeaponType.getObj(data_weapon[3]).name])
                self.playerList[i].weapon.durability = data_weapon[4]
                self.playerList[i].weapon.current_frame = data_weapon[0]
                self.playerList[i].weapon.animation_running = data_weapon[1]
                self.playerList[i].weapon.animation_direction = data_weapon[2]
                self.playerList[i].blood_frame = data_weapon[5]
                self.playerList[i].health = health
                self.playerList[i].killed_by = killed
                self.playerList[i].x, self.playerList[i].y = pos
                self.playerList[i].is_connected = con
                self.playerList[i].is_blocking = blocking

                for s in shots:
                    shot_found = False
                    for shot in self.playerList[i].weapon_shots:
                        if s[0] == shot.shot_id:
                            shot_found = True
                            shot.x = s[1]
                            shot.y = s[2]
                    if not shot_found:
                        self.playerList[i].weapon_shots.append(
                            weapon_shot.WeaponShot((s[1], s[2]), s[4], player.Player.get_color_rgb(self.playerList[i]),
                                                   s[3], s[5], shot_id=s[0]))

            for p in self.playerList:
                if p == self.playerList[id]:
                    continue
                p.refresh_solids()

            # sync items
            self.map.setitems(self.data["metadata"]["spawnpoints"]["items"])
            # print("Handling pos parsing:", datetime.datetime.now() - timer)
            # timer = datetime.datetime.now()

            # Draw Map Background
            # self.map.draw(self.canvas.get_canvas())
            self.map.draw_background(self.canvas.get_canvas())

            # Draw Players
            for p in self.playerList:
                if p.is_connected:
                    p.draw(self.canvas.get_canvas())
                    # Draw Shots
                    for shot in p.weapon_shots:
                        for ps in self.playerList:
                            if ps.id != id and not pd.merge(ps.solid_df, shot.get_dataframe(), how='inner',
                                                            on=['x', 'y']).empty:
                                shot.active = False
                        if shot.is_active():
                            shot.draw(self.canvas.get_canvas())
                            shot.move(self)
                        else:
                            p.weapon_shots.remove(shot)

            # Draw Solids on Map
            self.map.draw_solids(self.canvas.get_canvas())
            if not self.playerList[id].is_alive():
                # Draw Death-screen
                self.canvas.get_canvas().blit(pygame.image.load(wrk_dir + '\\wasted.png').convert_alpha(), (0, 0))

            # Draw Items
            self.map.draw_items(self.canvas.get_canvas())

            #  Draw Scorebpard
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

            # Draw Clock
            game_length = (self.end_time - self.start_time).total_seconds()
            remaining = (self.end_time - datetime.datetime.now()).total_seconds()
            remain_per = remaining / game_length
            if remain_per > 0.2:
                # shifted four times, because of strange artefacts when done only once
                pygame.draw.arc(self.canvas.get_canvas(), [255, 255, 255], [self.width - 60, 10, 50, 50], math.pi * 0.5,
                                (math.pi * 2 * remain_per) + math.pi * 0.5, 25)
                pygame.draw.arc(self.canvas.get_canvas(), [255, 255, 255], [self.width - 61, 10, 50, 50], math.pi * 0.5,
                                (math.pi * 2 * remain_per) + math.pi * 0.5, 25)
                pygame.draw.arc(self.canvas.get_canvas(), [255, 255, 255], [self.width - 60, 11, 50, 50], math.pi * 0.5,
                                (math.pi * 2 * remain_per) + math.pi * 0.5, 25)
                pygame.draw.arc(self.canvas.get_canvas(), [255, 255, 255], [self.width - 61, 11, 50, 50], math.pi * 0.5,
                                (math.pi * 2 * remain_per) + math.pi * 0.5, 25)
            else:
                pygame.draw.arc(self.canvas.get_canvas(), [255, 0, 0], [self.width - 60, 10, 50, 50], math.pi * 0.5,
                                (math.pi * 2 * remain_per) + math.pi * 0.5, 25)
                pygame.draw.arc(self.canvas.get_canvas(), [255, 0, 0], [self.width - 61, 10, 50, 50], math.pi * 0.5,
                                (math.pi * 2 * remain_per) + math.pi * 0.5, 25)
                pygame.draw.arc(self.canvas.get_canvas(), [255, 0, 0], [self.width - 60, 11, 50, 50], math.pi * 0.5,
                                (math.pi * 2 * remain_per) + math.pi * 0.5, 25)
                pygame.draw.arc(self.canvas.get_canvas(), [255, 0, 0], [self.width - 61, 11, 50, 50], math.pi * 0.5,
                                (math.pi * 2 * remain_per) + math.pi * 0.5, 25)

            # Draw End screen
            kills_per_player = list(
                map(lambda x: x[0], self.data["metadata"]["scoreboard"].values()))  # type:ignore[no-any-return]
            mvp = kills_per_player.index(max(kills_per_player))
            # Show the end screen when time is up or a player has enough kills
            if datetime.datetime.now() > self.end_time or max(kills_per_player) >= self.kills_to_win:
                self.canvas.get_canvas().fill((32, 32, 32))
                self.canvas.draw_text(self.canvas.get_canvas(), f"Player {mvp} has won",
                                      200, (255, 255, 255), 200, 350)
                if self.music_on:
                    # Stop Music
                    self.map.music.fadeout(1000)
                    self.music_on = False
                    if id == mvp:
                        # Play win sound
                        self.win_sound_effect.play()
                    else:
                        # Play lose sound
                        self.lost_sound_effect.play()

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

    def print_loading(self, percent):
        """
        displayes a loading screen
        :param percent: percentige to display
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
            "weapon_data": [self.playerList[int(self.data['id'])].weapon.current_frame,
                            self.playerList[int(self.data['id'])].weapon.animation_running,
                            self.playerList[int(self.data['id'])].weapon.animation_direction,
                            self.playerList[int(self.data['id'])].weapon.weapon_type.name,
                            self.playerList[int(self.data['id'])].weapon.durability,
                            self.playerList[int(self.data['id'])].blood_frame],
            "health": self.playerList[int(self.data['id'])].health,
            "killed_by": self.playerList[int(self.data['id'])].killed_by,
            "is_blocking": self.playerList[int(self.data['id'])].is_blocking,
            "shots": list(map(weapon_shot.WeaponShot.get_sync_data, self.playerList[int(self.data['id'])].weapon_shots))
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
        erg_blocking = []
        erg_shots = []
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
                    elif key2 == "weapon_data":
                        if key != str(self.id):
                            erg_weapon.append(value2)
                        else:
                            erg_weapon.append([self.playerList[int(self.data["id"])].weapon.current_frame,
                                               self.playerList[int(self.data["id"])].weapon.animation_running,
                                               self.playerList[int(self.data["id"])].weapon.animation_direction,
                                               self.playerList[int(self.data["id"])].weapon.weapon_type.name,
                                               self.playerList[int(self.data["id"])].weapon.durability,
                                               self.playerList[int(self.data["id"])].blood_frame])
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
                    elif key2 == "is_blocking":
                        if key != str(self.id):
                            erg_blocking.append(value2)
                        else:
                            erg_blocking.append(self.playerList[int(self.data["id"])].is_blocking)
                    elif key2 == "shots":
                        if key != str(self.id):
                            erg_shots.append(value2)
                        else:
                            erg_shots.append(list(map(weapon_shot.WeaponShot.get_sync_data,
                                                      self.playerList[int(self.data['id'])].weapon_shots)))
            else:
                continue
        return erg_player, erg_weapon, erg_health, erg_killed_by, erg_pos, erg_con, erg_shots, erg_blocking

    def next_to_solid(self, player, dirn, distance):
        """
        calculates the distance to the nearest object in one direction in a range
        :param player: the current player
        :param dirn: the direction
        :param distance: the range in which to check
        :return: integer representing the distance to the next object within the range
        """
        return self.next_to_solid_df(player.solid_df, dirn, distance)

    def next_to_solid_df(self, input_df, dirn, distance):
        """
        calculates the distance to the nearest object in one direction in a range
        :param input_df: the current dataframe
        :param dirn: the direction
        :param distance: the range in which to check
        :return: integer representing the distance to the next object within the range
        """
        # first combining all solid pixels in one dataframe
        solid_pixels_df = copy(self.map.solid_df)
        # getting copy of the solid dataframe
        df = copy(input_df)
        erg = 0

        Animated.shift_df(df, dirn, distance)
        if pd.merge(df, solid_pixels_df, how='inner', on=['x', 'y']).empty:
            erg = distance
            return erg
        Animated.shift_df(df, dirn, -distance)

        # checking for each pixel if a move ment would cause a collision
        for _ in range(distance):
            Animated.shift_df(df, dirn, 1)
            if not pd.merge(df, solid_pixels_df, how='inner', on=['x', 'y']).empty:
                return erg
            erg += 1
        return erg

    def initialize_game_data(self):
        timeout = time.time() + 60 * 0
        while "metadata" not in self.data:
            self.update_background_process()
            if time.time() > timeout:
                raise Exception('timeout while receiving data from background process')
