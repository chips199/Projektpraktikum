import datetime
import inspect
import os
from tkinter import messagebox
from time import sleep
from typing import Optional, Callable, Union, Type
import copy

import customtkinter as tk
from PIL import Image

from src.game.gamelogic import game
from src.game.gamelogic.backgroundProcess import backgroundProzess
from src.game.gamelogic.background_music import Music

from src.game.menu.MyFrame import MyFrame
from src.game.menu.MyLabel import MyLabel
from src.game.menu.MyWindow import MyWindow

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
        self.conn1 = Type[Connection]
        self.conn2 = Type[Connection]
        self.entry_session_id = None
        self.label_error = None
        self.label_game_name = None
        self.back_button = None
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
            "amount_player": 2,
            "map": "unknown"
        }

        # -------------------------------------------  Music  -------------------------------------------
        self.music = Music(r"music", 1.0)
        self.music.play(-1)

        self.player_dict = {
            "0": [wrk_dir + r"\..\unknown1\player\unknown2_player_magenta.png", 0.14],
            "1": [wrk_dir + r"\..\unknown1\player\unknown2_player_orange.png", 0.37],
            "2": [wrk_dir + r"\..\unknown1\player\unknown2_player_purple.png", 0.6],
            "3": [wrk_dir + r"\..\unknown1\player\unknown2_player_turquoise.png", 0.83]
        }

        self.copy_player_dict = copy.deepcopy(self.player_dict)

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

    def load_interaction_frame(self) -> None:
        """
        Load the interaction frame, holding the buttons to start and create a session and an entry field to enter an
        existing session id
        """
        self.interaction_frame = MyFrame(master=self.main_frame,
                                         width=self.root.window_width,
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

    def load_choose_map_frame(self) -> None:
        """
        Load the 'Choose Map' frame.

        This function destroys the current interaction frame and creates a new frame
        where players can choose a map to play on. The chosen map is passed to
        create_lobby().

        Returns:
            None
        """
        # Destroy the current interaction frame
        self.interaction_frame.destroy()  # type:ignore[union-attr]

        # Create a new frame for the map selection
        self.choose_map_frame = MyFrame(master=self.main_frame,
                                        width=int(self.window_width),
                                        height=int(400 * self.sizing_height),
                                        fg_color="#212121")
        self.choose_map_frame.place(anchor='n', x=self.window_width / 2, y=self.window_height * 0.3)

        # Create the 'back' button
        self.back_button.place(relx=0.05,
                               rely=0.1)

        width = int(444 * self.sizing_width)
        height = int(250 * self.sizing_height)

        # Load and place the basic map
        basic_map_structures = tk.CTkImage(
            dark_image=Image.open(wrk_dir + r"\..\menu\maps\basic_map.png"),
            size=(width, height))
        map1 = MyLabel(master=self.choose_map_frame,
                       text=None,
                       image=basic_map_structures)
        map1.place(relx=0.21,
                   rely=0.5,
                   anchor='center')

        # Load and place the space map
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

        # Load and place the snow map
        schnee_map_platforms = tk.CTkImage(
            dark_image=Image.open(wrk_dir + r"\..\menu\maps\snow_map.png"),
            size=(width, height))
        map3 = MyLabel(master=self.choose_map_frame,
                       text=None,
                       image=schnee_map_platforms
                       )
        map3.place(relx=0.79,
                   rely=0.5,
                   anchor='center')

        # Create buttons to select each map
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

    def load_lobby_frame(self) -> None:
        """
        Load the lobby frame.

        The lobby frame consists of a MyFrame widget and various child widgets,
        including a back button, a session ID label, and a start button.
        """
        # Create a MyFrame widget as the lobby frame
        self.lobby_frame = MyFrame(master=self.root,
                                   fg_color="#212121")

        # Configure the dimensions of the lobby frame
        self.lobby_frame.configure(width=self.window_width,  # type:ignore[union-attr]
                                   height=150 * self.sizing_height)  # type:ignore[union-attr]
        # Place the lobby frame at the appropriate position
        self.lobby_frame.place(x=0, y=250 * self.sizing_height)

        # Configure and place the back button widget
        self.back_button.configure(text="Leave Lobby")
        self.back_button.place(relx=0.02, rely=0.1)

        # Update the main window to render any newly-added widgets
        self.root.update()

        # Create a session ID label widget and place it in the lobby frame
        session_id_label = MyLabel(master=self.main_frame,
                                   width=self.w,
                                   height=self.h,
                                   text="Session ID: {}".format(self.data["s_id"]),
                                   font=("None", self.h * 0.6))
        session_id_label.place(x=50 * self.sizing_width,
                               y=int((self.label_game_name.winfo_y() +  # type:ignore[union-attr]
                                      self.label_game_name.winfo_height() +  # type:ignore[union-attr]
                                      10) * self.sizing_height))

        # Create a start button widget and place it in the lobby frame
        button_start = tk.CTkButton(master=self.lobby_frame,
                                    text="Start",
                                    width=self.w,
                                    height=self.h,
                                    command=self.start_game,
                                    font=("None", self.h * 0.6),
                                    corner_radius=int(self.h / 3))
        button_start.place(relx=0.5, y=0, anchor='n')

    # __________________Player Functions__________________

    def load_player(self,
                    rel_x_pos: float,
                    path: str) -> None:
        """
        Loads a player into the main frame at the specified position.

        :param rel_x_pos: The x-position of the player in the main frame, specified as a relative value (0.0-1.0)
        :param path: The file path to the player image
        :return: None
        """
        # Load the player image from the specified file path
        player_image = tk.CTkImage(dark_image=Image.open(path),
                                   size=(int(49 * self.sizing_width), int(142 * self.sizing_height)))

        # Create a label to display the player image
        label_image = MyLabel(master=self.main_frame,
                              text=None,
                              image=player_image)

        # Place the label at the specified relative position
        label_image.place(relx=rel_x_pos, rely=0.28)

        # Set the relative position of the label
        label_image.set_rel_positions(x=rel_x_pos, y=0.28)

        # Set the sizing of the label
        label_image.set_sizing(self.sizing_width, self.sizing_height)

        # Add the player label to the list of players
        self.player.append(label_image)

        # Update the GUI
        self.root.update()

        # Animate the player
        label_image.move_on_y_axis(direction=1,
                                   rely=0.6,
                                   ending_function=lambda: label_image.idle_animation_on_y_axis(upper_y=0.58,
                                                                                                lower_y=0.6,
                                                                                                stepsize=0.0008))

    def update_player(self) -> None:
        """
        Update the players in the game by extracting the amount of players from server handed over in the self.data
        In Addition change the directory path to the correct map path
        """
        server_amount_player = int(self.data["amount_player"])  # type: ignore[call-overload]

        if self.data["map"] not in self.player_dict['0'][0]:  # type:ignore[operator]
            player = "unknown2"
            if self.data["map"] == "basicmap":
                player = "basic"
            elif self.data["map"] == "platformmap":
                player = "space"
            elif self.data["map"] == "schneemap":
                player = "snow"
            for key, val in self.player_dict.items():
                val[0] = val[0].replace("unknown1", self.data["map"])  # type:ignore[attr-defined]
                val[0] = val[0].replace("unknown2", player)  # type:ignore[attr-defined]

        # Loop over the absolute difference between the number of players in the game and the number of players on the server
        else:
            for i in range(abs(server_amount_player - self.amount_player)):
                # If the number of players in the game is less than the number of players on the server
                if self.amount_player < server_amount_player:
                    # Load the new player
                    self.load_player(path=self.player_dict[str(self.amount_player)][0],  # type: ignore[arg-type]
                                     rel_x_pos=self.player_dict[str(self.amount_player)][1])  # type: ignore[arg-type]
                    self.amount_player += 1

                # If the number of players in the game is greater than the number of players on the server
                else:
                    # Remove the last player in the game
                    player_to_remove = self.player.pop()
                    player_to_remove.destroy()
                    self.amount_player -= 1

        # If the game is running
        if self.root.run:
            # Call the update player method again after 1000ms
            self.main_frame.after(1000, lambda: self.update_player())

    # __________________command: Functions__________________

    def start_new_session(self):
        """
        Clears the interaction frame and loads the choose map frame.
        """
        # Clear the interaction frame
        self.clear_frame_sliding(widget=self.interaction_frame,
                                 direction="down",
                                 after_time=1500,
                                 func=lambda: self.load_choose_map_frame())

    def create_lobby(self, map_name: str) -> None:
        """
        Creates a lobby with the given map_name.

        :param map_name: The name of the map to be used in the lobby.
        """
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

    def join_lobby(self) -> None:
        """
        Start the network and try to join the lobby with the session ID from the entry field
        When successful, slide out the interaction frame and load the lobby frame.
        """
        self.start_network(argument=self.entry_session_id.get(),  # type:ignore[union-attr]
                           update_func=lambda: self.update_background_process(),
                           success_func=lambda: self.clear_frame_sliding(
                               widget=self.interaction_frame,
                               direction="down",
                               after_time=1200,
                               func=lambda: self.load_lobby_frame(),
                               fun2=lambda: self.check_if_game_started(),
                               func3=lambda: self.main_frame.after(1700, lambda: self.update_player())))

    def start_game(self) -> None:
        """
        Start the game and close the main window
        """
        # Send start signal to the game
        self.conn1.send("start")  # type:ignore[attr-defined]
        # Stop the main loop
        self.root.run = False
        # Destroy the main window
        self.root.destroy()
        # Stop the music
        self.music.fadeout(2000)
        # Create and run the game instance
        g = game.Game(w=1600, h=900, conn=self.conn1, process=self.process)
        g.run()

    def back_to_start(self) -> None:
        """
        Return to the main frame of the game, destroying any current frames and resetting attributes
        """
        response = "yes"
        if self.lobby_owner:
            response = messagebox.askquestion(title="",
                                              message="Your are the owner of this lobby. Leaving will quit the whole lobby. Continue?")

        if response == "yes":
            self.lobby_owner = False
            # Destroy current frames
            self.main_frame.destroy()
            # Load the main frame
            self.load_main_frame()
            # Load the interaction frame
            self.load_interaction_frame()
            # Remove the back button
            self.back_button.place_forget()
            # Reset player dictionary
            self.player_dict = copy.deepcopy(self.copy_player_dict)
            if self.process is not None:
                # Terminate the process
                self.process.kill()
                # Reset attributes
                self.amount_player = 0
                self.lobby_frame.destroy()

    # __________________other Functions__________________
    def check_if_game_started(self) -> None:
        """
        Check if the game has started and call the start_game method if it has, otherwise wait 1500 ms and
        call itself recursively.
        """
        if self.data["game_started"]:  # type:ignore[union-attr]
            self.start_game()
        else:
            self.root.after(1500, lambda: self.check_if_game_started())

    def clear_frame_sliding(self,
                            widget: Union['MyLabel', 'tk.CTkButton', 'MyFrame'],
                            direction: str,
                            stepsize: int = 9,
                            after_time: int = 2000,
                            func: Optional[Callable] = None,  # type: ignore[type-arg]
                            **kwargs: Optional[Callable]) -> None:  # type: ignore[type-arg]
        """
        Clear the widget out of the window in a sliding animation.
        :param widget: widget to be cleared
        :param direction: direction in which the widget is cleared
        :param stepsize: stepsize of the animation
        :param after_time: time after which the func() function is performed
        :param func: function that is called with delay given in after_time
        :param kwargs: functions that are called without delay
        :return: None
        """
        # Perform the sliding animation
        self.root.move_out_of_window(widget=widget,
                                     direction=direction,
                                     stepsize=stepsize)

        # If a function was provided, call it after the sliding animation
        if func is not None:
            self.main_frame.after(after_time, lambda: func())

        # Loop over the provided functions and call them after the sliding animation
        for key, value in kwargs.items():
            if inspect.isfunction(value):
                value()

    def start_network(self,
                      argument: str,
                      update_func: Callable,  # type: ignore[type-arg]
                      success_func: Callable) -> None:  # type: ignore[type-arg]
        """
        Start the network by passing the `argument` to the `backgroundProzess` function.
        :param argument: the argument passed to the `backgroundProzess` function.
        :param update_func: the function to call after updating the network.
        :param success_func: the function to call after successfully starting the network.
        """
        try:
            if argument != "":
                # self.update_directory(map_name = argument)
                # Set up connection between main process and background process
                self.conn1, self.conn2 = multiprocessing.Pipe(duplex=True)
                # Start the background process
                self.process = multiprocessing.Process(target=backgroundProzess, args=(argument, self.conn2))
                self.process.start()
                self.root.set_process(self.process)
                # Wait for the first message from the background process
                while not self.conn1.poll():
                    sleep(0.1)
                # Store the current time
                self.timer = datetime.datetime.now()
                # Call update function
                update_func()

            # When session id is empty or 5 (means invalid)
            if argument == "" or self.data["id"] == "5":  # type:ignore[comparison-overlap]
                if argument == "":
                    msg = "Enter Session ID"
                else:
                    msg = str(self.data["s_id"])

                # Show error message
                self.label_error.label_hide_show(  # type:ignore[union-attr]
                    x=int(self.window_width / 2),
                    y=int((self.label_game_name.winfo_y() +  # type:ignore[union-attr]
                           self.label_game_name.winfo_height() +  # type:ignore[union-attr]
                           15) * self.sizing_height),
                    time=3000,
                    message=msg)

                # Also kill the background process
                if self.process is not None:
                    self.process.kill()

                # Cancel the after call from update_background_process
                if self.update_background_after_id is not None:
                    self.main_frame.after_cancel(self.update_background_after_id)

            else:
                # Call the success function if the session ID is valid
                success_func()

        except ConnectionRefusedError:
            self.label_error.label_hide_show(  # type:ignore[union-attr]
                x=int(self.window_width / 2),
                y=int((self.label_game_name.winfo_y() +  # type:ignore[union-attr]
                       self.label_game_name.winfo_height() +  # type:ignore[union-attr]
                       15) * self.sizing_height),
                time=3000,
                message="No answer from server")

    def update_background_process(self) -> None:
        """
        Updates the background process by checking if there is data available through a connection
        """
        if self.conn1.poll():  # type:ignore[attr-defined]
            self.data = self.conn1.recv()  # type:ignore[attr-defined]
        # Set up the next update by calling itself through after method
        self.update_background_after_id = self.main_frame.after(100, self.update_background_process)


if __name__ == "__main__":
    m = MenuSetup()
    m.run()

    print(int(round(datetime.datetime.now().timestamp())))
    print(datetime.datetime.now().timestamp())
