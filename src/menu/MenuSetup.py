import os
import time
from _thread import start_new_thread
from time import sleep

import customtkinter as tk

from src.menu.MyEntry import MyEntry
from src.menu.MyFrame import MyFrame
from src.menu.MyLabel import MyLabel
from src.menu.MyWindow import MyWindow
from src.game.network import Network
from src.game import game
from typing import Optional, Callable, Union

from PIL import Image

wrk_dir = os.path.abspath(os.path.dirname(__file__))


class MenuSetup:
    def __init__(self):
        # -------------------------------------------  Parameters  -------------------------------------------
        self.label_error = None
        self.label_game_name = None
        self.net = None
        self.w = 300
        self.h = 60
        self.window_width_planned = self.window_width = 1600
        self.window_height_planned = self.window_height = 900
        self.sizing = round(self.window_width_planned / 1920, 5)
        self.sizing_width = 1
        self.sizing_height = 1
        self.s_id = "1"
        self.amount_player = 0

        self.player_dict = {
            "0": [wrk_dir + r"\..\basicmap\player\basic_player_magenta.png", 175],
            "1": [wrk_dir + r"\..\basicmap\player\basic_player_orange.png", 575],
            "2": [wrk_dir + r"\..\basicmap\player\basic_player_purple.png", 975],
            "3": [wrk_dir + r"\..\basicmap\player\basic_player_turquoise.png", 1375]
        }

        # -------------------------------------------  Window  -------------------------------------------
        # configure root window
        self.root = MyWindow()
        self.root.title('Stick Wars')

        # get screen width and height
        self.ws = self.root.winfo_screenwidth()  # width of the screen
        self.hs = self.root.winfo_screenheight()  # height of the screen

        # change size of window and other widgets, if the actual screen size is smaller than the planned screen size
        if self.ws < self.window_width_planned or self.hs < self.window_height_planned:
            self.window_width = int(self.ws * self.sizing)
            self.window_height = int(self.hs * self.sizing)

            self.sizing_width = round(self.window_width /
                                      self.window_width_planned, 2)  # type: ignore[assignment]
            self.sizing_height = round(self.window_height /
                                       self.window_height_planned, 2)  # type: ignore[assignment]
            print(self.window_width / self.window_width_planned)

            self.w = int(300 * self.window_width / self.window_width_planned)
            self.h = int(60 * self.window_height / self.window_height_planned)

        self.root.set_size(self.window_width, self.window_height)
        self.root.set_sizing(self.sizing_width, self.sizing_height)

        # calculate x and y coordinates for the Tk root window
        self.x = int((self.ws / 2) - (self.window_width / 2))
        self.y = int((self.hs / 2) - (self.window_height / 2) - 20)
        self.root.geometry("{}x{}+{}+{}".format(self.window_width, self.window_height, self.x, self.y))
        self.root.resizable(False, False)

        self.main_frame = MyFrame(master=self.root, width=self.window_width, height=self.window_height)
        self.main_frame.place(anchor='center', relx=0.5, rely=0.5)
        self.interaction_frame = None
        self.lobby_frame = None
        self.choose_map_frame = None

    def update_player(self):
        time.sleep(1.5)
        # task to get amount of player from server, needs to be performed in asynchronus thread
        while self.root.run and self.net is not None:
            if not self.net.game_started():
                # Start game here
                self.start_game()
                return
            server_amount_player = int(self.net.check_lobby())
            for i in range(server_amount_player - self.amount_player):
                if self.amount_player < server_amount_player:
                    time.sleep(1)
                    print("amount player saved", self.amount_player)
                    # print("i", i)
                    print("amount player from server", server_amount_player)
                    # self.amount_player = int(self.net.check_lobby())
                    self.load_player(path=self.player_dict[str(self.amount_player)][0],
                                     x_pos=self.player_dict[str(self.amount_player)][1])
                    self.amount_player += 1
                print()

    def run(self):
        self.load_main_frame()
        self.load_interaction_frame()
        self.root.mainloop()

        while self.root.run:
            self.root.update()

            # if self.net is not None:
            #     self.amount_player = int(self.net.check_lobby())

    def load_main_frame(self):
        # -------------------------------------------  MainFrame  -------------------------------------------

        # Hintergrundbild
        background_image = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\solid\basic_map_structures.png"),
                                       size=(self.window_width, self.window_height))
        # noinspection PyTypeChecker
        label_background = tk.CTkLabel(master=self.main_frame,
                                       text=None,
                                       image=background_image)
        label_background.place(x=0, y=0)

        # Game Name Label
        game_name_image = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\stick_wars_schriftzug.png"),
                                      size=(int(1225 * self.sizing_width * 0.9), int(164 * self.sizing_height * 0.9)))
        self.label_game_name = MyLabel(master=self.main_frame,
                                       text=None,
                                       image=game_name_image,
                                       fg_color="#212121")
        self.label_game_name.place(x=int(self.window_width / 2),
                                   y=int(164 * self.sizing_height),
                                   anchor='s')

        # Session ID not found Fehlermeldung
        self.label_error = MyLabel(master=self.main_frame,
                                   text="Session ID not found",
                                   text_color="red",
                                   bg_color="transparent",
                                   width=0,
                                   height=10 * self.sizing_height,
                                   font=("None", 12 * self.sizing_height),
                                   anchor="w",
                                   justify='left')

    def load_interaction_frame(self):
        self.interaction_frame = MyFrame(master=self.root, width=int(self.window_width),
                                         height=int(280 * self.sizing_height),
                                         fg_color="#212121")
        self.interaction_frame.place(anchor='center', x=self.window_width / 2, y=self.window_height * 0.45)

        # Session ID Eingabefeld
        entry_session_id = MyEntry(master=self.interaction_frame,
                                   placeholder_text="Session ID",
                                   width=self.w,
                                   height=self.h,
                                   font=("None", self.h * 0.5),
                                   corner_radius=self.h / 3)
        entry_session_id.place(relx=0.5, rely=0.0, anchor='n')
        self.root.update()

        # # Game Name Label
        # game_name_image = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\stick_wars_schriftzug.png"),
        #                            size=(int(1225 * self.sizing_width * 0.9), int(164 * self.sizing_height * 0.9)))
        # label_image = MyLabel(master=self.interaction_frame,
        #                       text=None,
        #                       image=game_name_image)
        # label_image.place(x=int((entry_session_id.winfo_x() + entry_session_id.winfo_width()/2) * self.sizing_width),
        #                   y=int((entry_session_id.winfo_y() - entry_session_id.winfo_height()/2 - 30) * self.sizing_height),
        #                   anchor='s')

        # label_image.place(x=0,
        #                   y=0,
        #                   anchor='center')

        # Create 'Play/Start Button'
        button_play = tk.CTkButton(master=self.interaction_frame,
                                   text="Play",
                                   width=self.h,
                                   height=self.h,
                                   font=("None", self.h * 0.4),
                                   corner_radius=int(self.h / 3), )
        button_play.configure(command=lambda: self.start_network(argument=entry_session_id.get(),
                                                                 func=lambda: self.clear_frame_sliding(
                                                                     widget_list=[self.interaction_frame,
                                                                                  self.main_frame.winfo_children()[
                                                                                      0]],
                                                                     direction_list=["up",
                                                                                     "down"],
                                                                     after_time=2400,
                                                                     func=lambda: self.load_lobby_frame())))

        button_play.place(x=int((entry_session_id.winfo_x() + entry_session_id.winfo_width() + 10) * self.sizing_width),
                          y=int(entry_session_id.winfo_y() * self.sizing_height))
        self.root.update()

        # Create 'New Session Button'
        button_new_session = tk.CTkButton(master=self.interaction_frame,
                                          text="Create New Session",
                                          width=int((button_play.winfo_x() - entry_session_id.winfo_x() +
                                                     button_play.winfo_width()) * self.sizing_width),
                                          height=int(self.h / 2 * self.sizing_height),
                                          command=lambda: self.clear_frame_sliding(widget_list=[self.interaction_frame,
                                                                                                self.main_frame.winfo_children()[
                                                                                                    0]],
                                                                                   direction_list=["up",
                                                                                                   "down"],
                                                                                   after_time=2400,
                                                                                   func=lambda: self.load_choose_map_frame()),
                                          corner_radius=int(self.h / 3),
                                          font=("None", self.h * 0.4))
        button_new_session.place(x=int(entry_session_id.winfo_x() * self.sizing_width),
                                 y=int((entry_session_id.winfo_y() + entry_session_id.winfo_height() + 15) *
                                       self.sizing_height))

    def load_lobby_frame(self):
        # for widget in self.main_frame.winfo_children():
        #     widget.destroy()

        self.lobby_frame = MyFrame(master=self.root,
                                   fg_color="#212121")

        self.lobby_frame.configure(width=self.window_width,
                                   height=150 * self.sizing_height)  # type:ignore[union-attr]
        self.lobby_frame.place(x=0, y=250 * self.sizing_height)  # type:ignore[union-attr]

        self.root.update()

        session_id_label = MyLabel(master=self.main_frame,
                                   width=self.w,
                                   height=self.h,
                                   text="Session ID: {}".format(self.s_id),
                                   font=("None", self.h * 0.6))
        session_id_label.place(x=50 * self.sizing_width,
                               y=int(self.label_game_name.winfo_y() +  # type:ignore[union-attr]
                                     self.label_game_name.winfo_height() +  # type:ignore[union-attr]
                                     10 * self.sizing_height))

        button_start = tk.CTkButton(master=self.lobby_frame,
                                    text="Start",
                                    width=self.w,
                                    height=self.h,
                                    command=self.start_game,
                                    font=("None", self.h * 0.6),
                                    corner_radius=int(self.h / 3))
        button_start.place(x=int(self.lobby_frame.winfo_width() / 2),
                           y=0,
                           anchor='n')

        # self.amount_player = int(self.net.check_lobby())
        # for i in range(self.amount_player):
        #     print("yes")
        #     self.load_player(path=self.player_dict[str(i)][0], x_pos=self.player_dict[str(i)][1])

    def load_player(self, x_pos, path):
        player_image = tk.CTkImage(dark_image=Image.open(path),
                                   size=(int(49 * self.sizing_width), int(142 * self.sizing_height)))
        label_image = MyLabel(master=self.main_frame,
                              text=None,
                              image=player_image)
        label_image.place(x=int(x_pos * self.sizing_width), y=int(250 * self.sizing_height))
        label_image.set_sizing(self.sizing_width, self.sizing_height)

        self.root.update()

        label_image.move_to(x_pos,
                            500,
                            ending_function=lambda: label_image.idle_animation(pos_one=(x_pos, 500),
                                                                               pos_two=(x_pos, 485),
                                                                               next_pos="two"))

    def load_choose_map_frame(self):
        # for widget in self.main_frame.winfo_children():
        #     widget.place_forget()
        #     widget.destroy()
        self.interaction_frame.destroy()

        self.choose_map_frame = MyFrame(master=self.root, width=int(self.window_width),
                                        height=int(400 * self.sizing_height),
                                        fg_color="#212121")
        self.choose_map_frame.place(anchor='n', x=self.window_width / 2, y=self.window_height * 0.3)

        # load basic map
        basic_map_structures = tk.CTkImage(
            dark_image=Image.open(wrk_dir + r"\..\menu\maps\basic_map.png"),
            size=(int(444 * self.sizing_width),
                  int(250 * self.sizing_height)))
        map1 = MyLabel(master=self.choose_map_frame,
                       text=None,
                       image=basic_map_structures)
        map1.place(x=int(175 * self.sizing_width),
                   y=int(20 * self.sizing_height))

        self.root.update()

        # load space map
        space_map_platforms = tk.CTkImage(
            dark_image=Image.open(wrk_dir + r"\..\menu\maps\space_map.png"),
            size=(map1.winfo_width(),
                  map1.winfo_height()))
        map2 = MyLabel(master=self.choose_map_frame,
                       text=None,
                       image=space_map_platforms,
                       fg_color='#252525'
                       )
        map2.place(x=int(map1.winfo_x() + map1.winfo_width() + 20 * self.sizing_width),
                   y=map1.winfo_y())

        self.root.update()

        # add buttons to choose a map
        button_start = tk.CTkButton(master=self.choose_map_frame,
                                    text="Basicmap",
                                    width=map1.winfo_width(),
                                    height=int(self.h * 0.3),
                                    font=("None", self.h * 0.4),
                                    corner_radius=int(self.h / 3))
        button_start.place(x=int(map1.winfo_x()),
                           y=int(map1.winfo_y() + map1.winfo_height() + 20 * self.sizing_height))
        button_start.configure(
            command=lambda: self.start_network(argument='basicmap',
                                               func=lambda: self.clear_frame_sliding(
                                                   widget_list=[self.choose_map_frame],
                                                   direction_list=["down"],
                                                   stepsize=7,
                                                   after_time=2500,
                                                   func=lambda: self.load_lobby_frame())))

        button_start2 = tk.CTkButton(master=self.choose_map_frame,
                                     text="Space Map",
                                     width=map2.winfo_width(),
                                     height=int(self.h * 0.3),
                                     font=("None", self.h * 0.4),
                                     corner_radius=int(self.h / 3))
        button_start2.place(x=int(map2.winfo_x()),
                            y=int(map2.winfo_y() + map2.winfo_height() + 20 * self.sizing_height))
        button_start2.configure(
            command=lambda: self.start_network(argument='platformmap',
                                               func=lambda: self.clear_frame_sliding(
                                                   widget_list=[self.choose_map_frame],
                                                   direction_list=["down"],
                                                   stepsize=7,
                                                   after_time=2500,
                                                   func=lambda: self.load_lobby_frame())))

    def clear_frame_sliding(self,
                            widget_list: list['MyLabel|tk.CTkButton|MyFrame'],
                            direction_list: list[str],
                            stepsize: int = 5,
                            after_time: int = 2000,
                            func: Optional[Union[Callable, None]] = None) -> None:  # type:ignore[type-arg]
        self.root.move_out_of_window(widget_list=widget_list,
                                     direction_list=direction_list,
                                     stepsize=stepsize)
        if func is not None:
            self.main_frame.after(after_time, lambda: func())

    def start_game(self):

        self.root.run = False
        sleep(1)
        self.net.start_game()  # type:ignore[union-attr]
        # sleep(1)
        self.root.destroy()
        g = game.Game(w=1600, h=900, net=self.net)
        g.run()

    def start_network(self, argument, func):
        try:
            self.net = Network(argument)

            if self.net.id == "5":
                self.label_error.label_hide_show(  # type:ignore[union-attr]
                    x=int(self.window_width / 2),
                    y=int(self.label_game_name.winfo_y() +  # type:ignore[union-attr]
                          self.label_game_name.winfo_height() +  # type:ignore[union-attr]
                          30 * self.sizing_height),
                    time=3000,
                    message=self.net.session_id)
            else:
                self.s_id = self.net.session_id
                start_new_thread(self.update_player, tuple())
                func()

        except ConnectionRefusedError:
            self.label_error.label_hide_show(  # type:ignore[union-attr]
                x=int(self.window_width / 2),
                y=int(self.label_game_name.winfo_y() +  # type:ignore[union-attr]
                      self.label_game_name.winfo_height() +  # type:ignore[union-attr]
                      30 * self.sizing_height),
                time=3000,
                message="No answer from server")


if __name__ == "__main__":
    m = MenuSetup()
    m.run()
