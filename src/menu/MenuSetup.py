import os
from tkinter import Canvas

import customtkinter as tk

from src.menu.MyEntry import MyEntry
from src.menu.MyFrame import MyFrame
from src.menu.MyLabel import MyLabel
from src.menu.MyWindow import MyWindow
from PIL import Image, ImageTk

wrk_dir = os.path.abspath(os.path.dirname(__file__))


class MenuSetup:
    def __init__(self, *args, **kwargs):
        # -------------------------------------------  Parameters  -------------------------------------------
        self.interaction_frame = None
        self.main_frame = None
        self.w = 300
        self.h = 60
        self.window_width_planned = self.window_width = 1600
        self.window_height_planned = self.window_height = 900
        self.sizing = round(self.window_width_planned / 1920, 5)
        self.sizing_width = 1
        self.sizing_height = 1
        self.s_id = "1"

        # -------------------------------------------  Window  -------------------------------------------
        # configure root window
        self.root = MyWindow()
        self.root.title('TestName')

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

    def run(self):
        self.load_main_frame()
        self.load_interaction_frame()

        while self.root.run:
            self.root.update()

    def load_main_frame(self):
        # -------------------------------------------  MainFrame  -------------------------------------------
        self.main_frame = MyFrame(master=self.root, width=self.window_width, height=self.window_height)
        self.main_frame.place(anchor='center', relx=0.5, rely=0.5)

        # Hintergrundbild
        background_image = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\solid\basic_map_structures.png"),
                                       size=(self.window_width, self.window_height))
        # noinspection PyTypeChecker
        label_background = tk.CTkLabel(master=self.main_frame,
                                       text=None,
                                       image=background_image)
        label_background.place(x=0, y=0)

    def load_interaction_frame(self):
        self.interaction_frame = MyFrame(master=self.root, width=int(600 * self.sizing_width),
                                         height=int(300 * self.sizing_height),
                                         fg_color="#212121")
        self.interaction_frame.place(anchor='center', x=self.window_width / 2, y=self.window_height * 0.3)

        # Session ID Eingabefeld
        entry_session_id = MyEntry(master=self.interaction_frame,
                                   placeholder_text="Session ID",
                                   width=self.w,
                                   height=self.h,
                                   font=("None", self.h * 0.5),
                                   corner_radius=self.h / 3)
        entry_session_id.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.root.update()

        # Session ID not found Fehlermeldung
        label_error = MyLabel(master=self.interaction_frame,
                              text="Session ID not found",
                              text_color="red",
                              bg_color="transparent",
                              width=0,
                              height=10 * self.sizing_height,
                              font=("None", 12 * self.sizing_height),
                              anchor="w",
                              justify='left')

        # Create 'Play/Start Button'
        success_function = lambda: self.root.move_out_of_window(widget_list=[self.interaction_frame,
                                                                             self.main_frame.winfo_children()[0]],  # type:ignore[union-attr]
                                                                direction_list=["up",
                                                                                "down"],
                                                                stepsize=5)

        success_function2 = lambda: self.main_frame.after(1800,
                                                          lambda: self.load_lobby_frame())  # type:ignore[union-attr]

        failure_function = lambda: label_error.label_hide_show(
            x=int((entry_session_id.winfo_x() + entry_session_id.winfo_width() / 2) * self.sizing_width),
            y=int((entry_session_id.winfo_y() - 20) * self.sizing_height),
            time=3000)

        button_play = tk.CTkButton(master=self.interaction_frame,
                                   text="Play",
                                   command=lambda: entry_session_id.check_text(target_text=self.s_id,
                                                                               success_function=success_function,
                                                                               failure_function=failure_function,
                                                                               success_function2=success_function2),
                                   width=self.h,
                                   height=self.h,
                                   font=("None", self.h * 0.4),
                                   corner_radius=int(self.h / 3), )
        button_play.place(x=int((entry_session_id.winfo_x() + entry_session_id.winfo_width() + 10) * self.sizing_width),
                          y=int(entry_session_id.winfo_y() * self.sizing_height))
        self.root.update()

        # Create 'New Session Button'
        button_new_session = tk.CTkButton(master=self.interaction_frame,
                                          text="Create New Session",
                                          width=int((button_play.winfo_x() - entry_session_id.winfo_x() +
                                                     button_play.winfo_width()) * self.sizing_width),
                                          height=int(self.h / 2 * self.sizing_height),
                                          # command=lambda: printing(),
                                          font=("None", self.h * 0.4),
                                          corner_radius=int(self.h / 3))
        button_new_session.place(x=int(entry_session_id.winfo_x() * self.sizing_width),
                                 y=int((entry_session_id.winfo_y() + entry_session_id.winfo_height() + 15) *
                                       self.sizing_height))

    def load_lobby_frame(self):
        print("frame change")
        self.interaction_frame.configure(width=self.window_width,
                                         height=150 * self.sizing_height)  # type:ignore[union-attr]
        self.interaction_frame.place(x=0, y=250 * self.sizing_height)  # type:ignore[union-attr]

        session_id_label = MyLabel(master=self.main_frame,
                                   text="Session ID: {}".format(self.s_id),
                                   font=("None", 30))
        session_id_label.place(x=50 * self.sizing_width, y=30 * self.sizing_height)

        player_image = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\player\basic_player_orange.png"),
                                   size=(int(49 * self.sizing_width), int(142 * self.sizing_height)))
        label_image = MyLabel(master=self.main_frame,
                              text=None,
                              image=player_image)
        label_image.place(x=int(175 * self.sizing_width), y=int(250 * self.sizing_height))
        label_image.set_sizing(self.sizing_width, self.sizing_height)

        player_image2 = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\player\basic_player_purple.png"),
                                    size=(int(49 * self.sizing_width), int(142 * self.sizing_height)))
        label_image2 = MyLabel(master=self.main_frame, text=None, image=player_image2)
        label_image2.place(x=int(575 * self.sizing_width), y=int(250 * self.sizing_height))
        label_image2.set_sizing(self.sizing_width, self.sizing_height)

        player_image3 = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\player\basic_player_turquoise.png"),
                                    size=(int(49 * self.sizing_width), int(142 * self.sizing_height)))
        label_image3 = MyLabel(master=self.main_frame, text=None, image=player_image3)
        label_image3.place(x=int(975 * self.sizing_width), y=int(250 * self.sizing_height))
        label_image3.set_sizing(self.sizing_width, self.sizing_height)

        player_image4 = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\player\basic_player_magenta.png"),
                                    size=(int(49 * self.sizing_width), int(142 * self.sizing_height)))
        label_image4 = MyLabel(master=self.main_frame, text=None, image=player_image4)
        label_image4.place(x=int(1375 * self.sizing_width), y=int(250 * self.sizing_height))
        label_image4.set_sizing(self.sizing_width, self.sizing_height)

        self.root.update()

        label_image.move_to(175,
                            500,
                            ending_function=lambda: label_image.idle_animation(pos_one=(175, 500),
                                                                               pos_two=(175, 485),
                                                                               next_pos="two"))

        label_image2.after(920, lambda: label_image2.move_to(575,
                                                             500,
                                                             ending_function=lambda: label_image2.idle_animation(
                                                                 pos_one=(575, 500),
                                                                 pos_two=(575, 485),
                                                                 next_pos="two")))

        label_image3.after(1840, lambda: label_image3.move_to(975,
                                                              500,
                                                              ending_function=lambda: label_image3.idle_animation(
                                                                  pos_one=(975, 500),
                                                                  pos_two=(975, 485),
                                                                  next_pos="two")))

        label_image4.after(2760, lambda: label_image4.move_to(1375,
                                                              500,
                                                              ending_function=lambda: label_image4.idle_animation(
                                                                  pos_one=(1375, 500),
                                                                  pos_two=(1375, 485),
                                                                  next_pos="two")))

# -------------------------------------------  Parameters  -------------------------------------------
# w = 300
# h = 60
# window_width_planned = window_width = 1600
# window_height_planned = window_height = 900
# sizing = round(window_width_planned/1920, 5)
# self.sizing_width = 1
# self.sizing_height = 1
# s_id = "1"

# # -------------------------------------------  Window  -------------------------------------------
# # configure root window
# root = MyWindow()
# root.title('TestName')
#
# # get screen width and height
# ws = root.winfo_screenwidth()  # width of the screen
# hs = root.winfo_screenheight()  # height of the screen
#
# # change size of window and other widgets, if the actual screen size is smaller than the planned screen size
# if ws < window_width_planned or hs < window_height_planned:
#     window_width = int(ws * sizing)
#     window_height = int(hs * sizing)
#
#     self.sizing_width = round(window_width / window_width_planned, 2)  # type: ignore[assignment]
#     self.sizing_height = round(window_height / window_height_planned, 2)  # type: ignore[assignment]
#     print(window_width / window_width_planned)
#
#     w = int(300 * window_width / window_width_planned)
#     h = int(60 * window_height / window_height_planned)
#
# root.set_size(window_width, window_height)
# root.set_sizing(self.sizing_width, self.sizing_height)
#
# # calculate x and y coordinates for the Tk root window
# x = int((ws / 2) - (window_width / 2))
# y = int((hs / 2) - (window_height / 2) - 20)
# root.geometry("{}x{}+{}+{}".format(window_width, window_height, x, y))
# root.resizable(False, False)
#
# # -------------------------------------------  MainFrame  -------------------------------------------
# main_frame = MyFrame(master=root, width=window_width, height=window_height)
# main_frame.place(anchor='center', relx=0.5, rely=0.5)
#
# # Hintergrundbild
# background_image = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\solid\basic_map_structures.png"),
#                                size=(window_width, window_height))
# # noinspection PyTypeChecker
# label_background = tk.CTkLabel(master=main_frame,
#                                text=None,
#                                image=background_image)
# label_background.place(x=0, y=0)

# -------------------------------------------  InteractionFrame  -------------------------------------------
# "#212121"
# interaction_frame = MyFrame(master=root, width=int(600 * self.sizing_width), height=int(300 * self.sizing_height),
#                             fg_color="#212121")
# interaction_frame.place(anchor='center', x=window_width / 2, y=window_height * 0.3)
#
# # Session ID Eingabefeld
# entry_session_id = MyEntry(master=interaction_frame,
#                            placeholder_text="Session ID",
#                            width=w,
#                            height=h,
#                            font=("None", h * 0.5),
#                            corner_radius=h / 3)
# entry_session_id.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
# root.update()
#
# # Session ID not found Fehlermeldung
# label_error = MyLabel(master=interaction_frame,
#                       text="Session ID not found",
#                       text_color="red",
#                       bg_color="transparent",
#                       width=0,
#                       height=10 * self.sizing_height,
#                       font=("None", 12 * self.sizing_height),
#                       anchor="w",
#                       justify='left')
#
# # Create 'Play/Start Button'
# success_function = lambda: root.move_out_of_window(widget_list=[interaction_frame,
#                                                                 main_frame.winfo_children()[0]],
#                                                    direction_list=["up",
#                                                                    "down"],
#                                                    stepsize=5)
#
# success_function2 = lambda: main_frame.after(1800, lambda: load_lobby_frame(root))
#
# failure_function = lambda: label_error.label_hide_show(
#     x=int((entry_session_id.winfo_x() + entry_session_id.winfo_width() / 2) * self.sizing_width),
#     y=int((entry_session_id.winfo_y() - 20) * self.sizing_height),
#     time=3000)
#
# button_play = tk.CTkButton(master=interaction_frame,
#                            text="Play",
#                            command=lambda: entry_session_id.check_text(target_text=s_id,
#                                                                        success_function=success_function,
#                                                                        failure_function=failure_function,
#                                                                        success_function2=success_function2),
#                            width=h,
#                            height=h,
#                            font=("None", h * 0.4),
#                            corner_radius=int(h / 3), )
# button_play.place(x=int((entry_session_id.winfo_x() + entry_session_id.winfo_width() + 10) * self.sizing_width),
#                   y=int(entry_session_id.winfo_y() * self.sizing_height))
# root.update()
#
# # Create 'New Session Button'
# button_new_session = tk.CTkButton(master=interaction_frame,
#                                   text="Create New Session",
#                                   width=int((button_play.winfo_x() - entry_session_id.winfo_x() +
#                                              button_play.winfo_width()) * self.sizing_width),
#                                   height=int(h / 2 * self.sizing_height),
#                                   #                                 command=lambda: printing(),
#                                   font=("None", h * 0.4),
#                                   corner_radius=int(h / 3))
# button_new_session.place(x=int(entry_session_id.winfo_x() * self.sizing_width),
#                          y=int((entry_session_id.winfo_y() + entry_session_id.winfo_height() + 15) * self.sizing_height))

# root.update()
#
# # root.mainloop()
#
# while root.run:
#     root.update()
