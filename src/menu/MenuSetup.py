import datetime
import inspect
import os
from tkinter import messagebox
from time import sleep
from typing import Optional, Callable, Union, Type

import customtkinter as tk
from PIL import Image

from src.game import game
from src.game.backgroundProzess import backgroundProzess

from src.menu.MyFrame import MyFrame
from src.menu.MyLabel import MyLabel
from src.menu.MyWindow import MyWindow

import multiprocessing
from multiprocessing.connection import Connection

wrk_dir = os.path.abspath(os.path.dirname(__file__))


class MenuSetup:
    def __init__(self):
        # -------------------------------------------  Parameters  -------------------------------------------
        self.process = None
        self.counter = 0
        self.timer = datetime.datetime.now()
        self.update_background_after_id = None
        self.network_started = False
        # self.id = "5"
        self.conn1 = Type[Connection]
        self.conn2 = Type[Connection]
        self.entry_session_id = None
        self.label_error = None
        self.label_game_name = None
        self.back_button = None
        # self.net = None
        self.w = 300
        self.h = 60
        self.window_width_planned = self.window_width = 1600
        self.window_height_planned = self.window_height = 900
        self.sizing = round(self.window_width_planned / 1920, 5)
        self.sizing_width = 1
        self.sizing_height = 1
        self.amount_player = 0
        self.game_started = False
        self.player = []
        self.lobby_owner = False
        self.data = {
            "id": 1,
            "s_id": 2984,
            "amount_player": 2
        }

        self.player_dict = {
            "0": [wrk_dir + r"\..\basicmap\player\basic_player_magenta.png", 0.14],
            "1": [wrk_dir + r"\..\basicmap\player\basic_player_orange.png", 0.37],
            "2": [wrk_dir + r"\..\basicmap\player\basic_player_purple.png", 0.6],
            "3": [wrk_dir + r"\..\basicmap\player\basic_player_turquoise.png", 0.83]
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

            self.w = int(300 * self.window_width / self.window_width_planned)
            self.h = int(60 * self.window_height / self.window_height_planned)

        self.root.set_size(self.window_width, self.window_height)
        self.root.set_sizing(self.sizing_width, self.sizing_height)

        # calculate x and y coordinates for the Tk root window
        self.x = int((self.ws / 2) - (self.window_width / 2))
        self.y = int((self.hs / 2) - (self.window_height / 2) - 20)
        self.root.geometry("{}x{}+{}+{}".format(self.window_width, self.window_height, self.x, self.y))
        self.root.resizable(False, False)

        # self.main_frame = MyFrame(master=self.root, width=self.window_width, height=self.window_height)
        # self.main_frame.place(anchor='center', relx=0.5, rely=0.5)
        self.main_frame = None
        self.interaction_frame = None
        self.lobby_frame = None
        self.choose_map_frame = None

    def run(self) -> None:
        """
        Start the mainloop of the window
        """
        # Load the main frame
        self.load_main_frame()
        # Load the interaction frame
        self.load_interaction_frame()
        # Start the mainloop
        self.root.mainloop()

        # __________________loading Frame Functions__________________

    def load_main_frame(self):
        # -------------------------------------------  MainFrame  -------------------------------------------
        """
               Load the main frame for the game window
        """

        self.main_frame = MyFrame(master=self.root, width=self.window_width, height=self.window_height)
        self.main_frame.place(anchor='center', relx=0.5, rely=0.5)

        # Game Name Label
        game_name_image = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\stick_wars_schriftzug.png"),
                                      size=(int(1225 * self.sizing_width * 0.9), int(164 * self.sizing_height * 0.9)))
        self.label_game_name = MyLabel(master=self.main_frame,
                                       text=None,
                                       image=game_name_image,
                                       fg_color="#212121")
        # self.label_game_name.place(x=int(self.window_width / 2),
        #                            y=int(164 * self.sizing_height),
        #                            anchor='s')
        self.label_game_name.place(relx=0.5,
                                   rely=0.02,
                                   anchor='n')

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

        self.back_button = tk.CTkButton(master=self.main_frame,
                                        text="Back",
                                        width=int(self.h),
                                        height=int(self.h),
                                        font=("None", self.h * 0.4),
                                        corner_radius=int(self.h / 3),
                                        command=self.back_to_start)

    def load_interaction_frame(self):
        self.interaction_frame = MyFrame(master=self.main_frame,
                                         width=self.root.window_width,
                                         # height=int(710 * self.sizing_height),
                                         height=self.window_height * 0.79,
                                         fg_color="#212121")
        self.interaction_frame.place(anchor='sw', x=0, y=self.window_height)

        # Hintergrundbild
        background_image = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\solid\basic_map_structures.png"),
                                       size=(self.window_width, self.window_height))
        # noinspection PyTypeChecker
        label_background = tk.CTkLabel(master=self.interaction_frame,
                                       text=None,
                                       image=background_image)
        label_background.place(x=0, y=self.root.window_height - (130 * self.sizing_height), anchor="sw")

        # Session ID Eingabefeld
        self.entry_session_id = tk.CTkEntry(master=self.interaction_frame,
                                            placeholder_text="Session ID",
                                            width=self.w,
                                            height=self.h,
                                            font=("None", self.h * 0.5),
                                            corner_radius=int(self.h / 3))
        self.entry_session_id.place(relx=0.47,
                                    rely=0.1,
                                    anchor='n')

        # Create 'Play/Start Button'
        button_play = tk.CTkButton(master=self.interaction_frame,
                                   text="Play",
                                   width=self.h,
                                   height=self.h,
                                   font=("None", self.h * 0.4),
                                   corner_radius=int(self.h / 3),
                                   command=self.join_lobby)

        # button_play.place(
        #     x=int((self.entry_session_id.winfo_x() + self.entry_session_id.winfo_width() + 10) * self.sizing_width),
        #     y=int(self.entry_session_id.winfo_y() * self.sizing_height))

        button_play.place(relx=0.597,
                          rely=0.1,
                          anchor='n')
        self.root.update()

        # Create 'New Session Button'
        button_new_session = tk.CTkButton(master=self.interaction_frame,
                                          text="Create New Session",
                                          width=int((button_play.winfo_x() + button_play.winfo_width()
                                                     - self.entry_session_id.winfo_x()) * self.sizing_width),
                                          height=int(self.h / 2),
                                          command=self.start_new_session,
                                          corner_radius=int(self.h / 3),
                                          font=("None", self.h * 0.4))
        button_new_session.place(relx=0.5,
                                 rely=0.2,
                                 anchor='n')

    def load_choose_map_frame(self):
        self.interaction_frame.destroy()  # type:ignore[union-attr]

        self.choose_map_frame = MyFrame(master=self.main_frame, width=int(self.window_width),
                                        height=int(400 * self.sizing_height),
                                        fg_color="#212121")
        self.choose_map_frame.place(anchor='n', x=self.window_width / 2, y=self.window_height * 0.3)

        self.back_button.place(relx=0.05,
                               rely=0.1)

        width = int(444 * self.sizing_width)
        height = int(250 * self.sizing_height)

        # load basic map
        basic_map_structures = tk.CTkImage(
            dark_image=Image.open(wrk_dir + r"\..\menu\maps\basic_map.png"),
            size=(width, height))
        map1 = MyLabel(master=self.choose_map_frame,
                       text=None,
                       image=basic_map_structures)
        map1.place(relx=0.21,
                   rely=0.5,
                   anchor='center')

        # load space map
        space_map_platforms = tk.CTkImage(
            dark_image=Image.open(wrk_dir + r"\..\menu\maps\space_map.png"),
            size=(width, height))
        map2 = MyLabel(master=self.choose_map_frame,
                       text=None,
                       image=space_map_platforms
                       )
        map2.place(relx=0.5,
                   rely=0.5,
                   anchor='center')

        # load snow map
        schnee_map_platforms = tk.CTkImage(
            dark_image=Image.open(wrk_dir + r"\..\menu\maps\schnee_map.png"),
            size=(width, height))
        map3 = MyLabel(master=self.choose_map_frame,
                       text=None,
                       image=schnee_map_platforms
                       )
        map3.place(relx=0.79,
                   rely=0.5,
                   anchor='center')

        self.root.update()

        # add buttons to choose a map
        button_start = tk.CTkButton(master=self.choose_map_frame,
                                    text="Basicmap",
                                    width=width,
                                    height=int(self.h * 0.3),
                                    font=("None", self.h * 0.4),
                                    corner_radius=int(self.h / 3),
                                    command=lambda: self.create_lobby(map_name='basicmap'))
        button_start.place(relx=0.21,
                           rely=0.9,
                           anchor='center')

        button_start2 = tk.CTkButton(master=self.choose_map_frame,
                                     text="Space Map",
                                     width=width,
                                     height=int(self.h * 0.3),
                                     font=("None", self.h * 0.4),
                                     corner_radius=int(self.h / 3),
                                     command=lambda: self.create_lobby(map_name='platformmap'))
        button_start2.place(relx=0.5,
                            rely=0.9,
                            anchor='center')

        button_start3 = tk.CTkButton(master=self.choose_map_frame,
                                     text="Snow Map",
                                     width=width,
                                     height=int(self.h * 0.3),
                                     font=("None", self.h * 0.4),
                                     corner_radius=int(self.h / 3),
                                     command=lambda: self.create_lobby(map_name='schneemap'))
        button_start3.place(relx=0.79,
                            rely=0.9,
                            anchor='center')

    def load_lobby_frame(self):
        self.lobby_frame = MyFrame(master=self.root,
                                   fg_color="#212121")

        self.lobby_frame.configure(width=self.window_width,
                                   height=150 * self.sizing_height)  # type:ignore[union-attr]
        self.lobby_frame.place(x=0, y=250 * self.sizing_height)  # type:ignore[union-attr]

        self.back_button.configure(text="Leave Lobby")
        self.back_button.place(relx=0.02,
                               rely=0.1)

        self.root.update()

        session_id_label = MyLabel(master=self.main_frame,
                                   width=self.w,
                                   height=self.h,
                                   text="Session ID: {}".format(self.data["s_id"]),
                                   font=("None", self.h * 0.6))
        session_id_label.place(x=50 * self.sizing_width,
                               y=int((self.label_game_name.winfo_y() +  # type:ignore[union-attr]
                                      self.label_game_name.winfo_height() +  # type:ignore[union-attr]
                                      10) * self.sizing_height))

        button_start = tk.CTkButton(master=self.lobby_frame,
                                    text="Start",
                                    width=self.w,
                                    height=self.h,
                                    command=self.start_game,
                                    font=("None", self.h * 0.6),
                                    corner_radius=int(self.h / 3))
        button_start.place(relx=0.5,
                           y=0,
                           anchor='n')

    # __________________Player Functions__________________

    def load_player(self, rel_x_pos, path):
        player_image = tk.CTkImage(dark_image=Image.open(path),
                                   size=(int(49 * self.sizing_width), int(142 * self.sizing_height)))
        label_image = MyLabel(master=self.main_frame,
                              text=None,
                              image=player_image)
        label_image.place(relx=rel_x_pos, rely=0.28)
        label_image.set_rel_positions(x=rel_x_pos, y=0.28)
        label_image.set_sizing(self.sizing_width, self.sizing_height)

        self.player.append(label_image)

        self.root.update()

        label_image.move_on_y_axis(direction=1,
                                   rely=0.6,
                                   ending_function=lambda: label_image.idle_animation_on_y_axis(upper_y=0.58,
                                                                                                lower_y=0.6,
                                                                                                stepsize=0.0008))

    def update_player(self):
        server_amount_player = int(self.data["amount_player"])  # type:ignore[union-attr]
        # print(server_amount_player)
        for i in range(abs(server_amount_player - self.amount_player)):
            if self.amount_player < server_amount_player:
                self.load_player(path=self.player_dict[str(self.amount_player)][0],
                                 rel_x_pos=self.player_dict[str(self.amount_player)][1])
                self.amount_player += 1
            else:
                player_to_remove = self.player.pop()
                player_to_remove.destroy()
                self.amount_player -= 1
        if self.root.run:  # and self.net is not None:
            self.main_frame.after(1000, lambda: self.update_player())

    # __________________command: Functions__________________

    def start_new_session(self):
        self.clear_frame_sliding(widget=self.interaction_frame,
                                 direction="down",
                                 after_time=1500,
                                 func=lambda: self.load_choose_map_frame())

    def create_lobby(self, map_name):
        self.lobby_owner = True
        self.start_network(argument=map_name,
                           update_func=lambda: self.update_background_process(),
                           success_func=lambda: self.clear_frame_sliding(
                               widget=self.choose_map_frame,
                               direction="down",
                               after_time=1200,
                               func=lambda: self.load_lobby_frame(),
                               func2=lambda: self.check_if_game_started(),
                               func3=lambda: self.main_frame.after(1700, lambda: self.update_player())))

    def join_lobby(self):
        self.start_network(argument=self.entry_session_id.get(),  # type:ignore[union-attr]
                           update_func=lambda: self.update_background_process(),
                           success_func=lambda: self.clear_frame_sliding(
                               widget=self.interaction_frame,
                               direction="down",
                               after_time=1200,
                               func=lambda: self.load_lobby_frame(),
                               fun2=lambda: self.check_if_game_started(),
                               func3=lambda: self.main_frame.after(1700, lambda: self.update_player())))

    def start_game(self):
        self.conn1.send("start")  # type:ignore[attr-defined]
        print("send start to background")
        self.root.run = False
        self.root.destroy()
        # important sleep, don't remove!!! Neccessary for the background task to realize that the game
        # has started, to send correct data to the game
        sleep(2)
        g = game.Game(w=1600, h=900, conn=self.conn1, process=self.process)
        g.run()

    def back_to_start(self):
        response = "yes"
        if self.lobby_owner:
            response = messagebox.askquestion(title="",
                                              message="Your are the owner of this lobby. Leaving will quit the whole lobby. Continue?")

        if response == "yes":
            self.lobby_owner = False
            self.main_frame.destroy()
            self.load_main_frame()
            self.load_interaction_frame()
            self.back_button.place_forget()
            if self.process is not None:
                self.process.kill()
                self.amount_player = 0
                self.lobby_frame.destroy()

    # __________________other Functions__________________

    def check_if_game_started(self):
        if self.data["game_started"]:  # type:ignore[union-attr]
            self.start_game()
        else:
            self.root.after(1500, lambda: self.check_if_game_started())

    def clear_frame_sliding(self,
                            widget: ['MyLabel|tk.CTkButton|MyFrame'],  # type:ignore[valid-type]
                            direction: str,
                            stepsize: int = 9,
                            after_time: int = 2000,
                            func: Optional[Union[Callable, None]] = None,  # type:ignore[type-arg]
                            **kwargs: Optional[Union[Callable, None]]) -> None:  # type:ignore[type-arg]
        self.root.move_out_of_window(widget=widget,
                                     direction=direction,
                                     stepsize=stepsize)
        if func is not None:
            self.main_frame.after(after_time, lambda: func())
        for key, value in kwargs.items():
            if inspect.isfunction(value):
                value()

    def start_network(self, argument: str, update_func, success_func):
        try:
            if argument != "":
                self.conn1, self.conn2 = multiprocessing.Pipe(duplex=True)
                self.process = multiprocessing.Process(target=backgroundProzess, args=(argument, self.conn2))
                self.process.start()
                self.root.set_process(self.process)
                while not self.conn1.poll():
                    # waiting for the first message of background process
                    sleep(0.1)
                self.timer = datetime.datetime.now()
                update_func()

            if argument == "" or self.data["id"] == "5":  # type:ignore[comparison-overlap]
                if argument == "":
                    msg = "Enter Session ID"
                else:
                    msg = str(self.data["s_id"])
                self.label_error.label_hide_show(  # type:ignore[union-attr]
                    x=int(self.window_width / 2),
                    y=int((self.label_game_name.winfo_y() +  # type:ignore[union-attr]
                           self.label_game_name.winfo_height() +  # type:ignore[union-attr]
                           15) * self.sizing_height),
                    time=3000,
                    message=msg)
                # kill process (network) if session_id is invalid, in future we should be able to update the network
                if self.process is not None:
                    self.process.kill()
                # stop the after call from update_background_process
                if self.update_background_after_id is not None:
                    self.main_frame.after_cancel(self.update_background_after_id)
            else:
                success_func()

        except ConnectionRefusedError:
            self.label_error.label_hide_show(  # type:ignore[union-attr]
                x=int(self.window_width / 2),
                y=int((self.label_game_name.winfo_y() +  # type:ignore[union-attr]
                       self.label_game_name.winfo_height() +  # type:ignore[union-attr]
                       15) * self.sizing_height),
                time=3000,
                message="No answer from server")

    def update_background_process(self):
        # print("GET_background")
        if datetime.datetime.now() - self.timer >= datetime.timedelta(seconds=1):
            self.timer = datetime.datetime.now()
            print("count in Menu:", self.counter)
            self.counter = 0
        else:
            self.counter += 1
        if self.conn1.poll():  # type:ignore[attr-defined]
            self.data = self.conn1.recv()  # type:ignore[attr-defined]
        self.update_background_after_id = self.main_frame.after(300, self.update_background_process)

    def send_data(self, msg):
        self.conn1.send(msg)  # type:ignore[attr-defined]


if __name__ == "__main__":
    m = MenuSetup()
    m.run()
