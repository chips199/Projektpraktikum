import os
import customtkinter as tk

from src.menu.MyEntry import MyEntry
from src.menu.MyFrame import MyFrame
from src.menu.MyLabel import MyLabel
from src.menu.MyWindow import MyWindow
from PIL import Image

wrk_dir = os.path.abspath(os.path.dirname(__file__))


def load_lobby_frame(root_window):
    print("frame change")
    interaction_frame.configure(width=window_width, height=150 * sizing_height)
    interaction_frame.place(x=0, y=250 * sizing_height)

    session_id_label = MyLabel(master=main_frame,
                               text="Session ID: {}".format(s_id),
                               font=("None", 30))
    session_id_label.place(x=50 * sizing_width, y=30 * sizing_height)

    player_image = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\player\basic_player_orange.png"),
                               size=(int(49 * sizing_width), int(142 * sizing_height)))
    label_image = MyLabel(master=main_frame,
                          text=None,
                          image=player_image)
    label_image.place(x=int(175 * sizing_width), y=int(250 * sizing_height))
    label_image.set_sizing(sizing_width, sizing_height)

    player_image2 = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\player\basic_player_purple.png"),
                                size=(int(49 * sizing_width), int(142 * sizing_height)))
    label_image2 = MyLabel(master=main_frame, text=None, image=player_image2)
    label_image2.place(x=int(575 * sizing_width), y=int(250 * sizing_height))
    label_image2.set_sizing(sizing_width, sizing_height)

    player_image3 = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\player\basic_player_turquoise.png"),
                                size=(int(49 * sizing_width), int(142 * sizing_height)))
    label_image3 = MyLabel(master=main_frame, text=None, image=player_image3)
    label_image3.place(x=int(975 * sizing_width), y=int(250 * sizing_height))
    label_image3.set_sizing(sizing_width, sizing_height)

    player_image4 = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\player\basic_player_magenta.png"),
                                size=(int(49 * sizing_width), int(142 * sizing_height)))
    label_image4 = MyLabel(master=main_frame, text=None, image=player_image4)
    label_image4.place(x=int(1375 * sizing_width), y=int(250 * sizing_height))
    label_image4.set_sizing(sizing_width, sizing_height)

    root_window.update()

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
w = 300
h = 60
sizing = 0.83333
window_width_planned = window_width = 1600
window_height_planned = window_height = 900
sizing_width = 1
sizing_height = 1
s_id = "1"

# -------------------------------------------  Window  -------------------------------------------
# configure root window
root = MyWindow()
root.title('TestName')

# get screen width and height
ws = root.winfo_screenwidth()  # width of the screen
hs = root.winfo_screenheight()  # height of the screen

# change size of window and other widgets, if the actual screen size is smaller than the planned screen size
if ws < window_width_planned or hs < window_height_planned:
    window_width = int(ws * sizing)
    window_height = int(hs * sizing)

    sizing_width = round(window_width / window_width_planned, 2)        # type: ignore[assignment]
    sizing_height = round(window_height / window_height_planned, 2)     # type: ignore[assignment]
    print(window_width / window_width_planned)

    w = int(300 * window_width / window_width_planned)
    h = int(60 * window_height / window_height_planned)

root.set_size(window_width, window_height)
root.set_sizing(sizing_width, sizing_height)

# calculate x and y coordinates for the Tk root window
x = int((ws / 2) - (window_width / 2))
y = int((hs / 2) - (window_height / 2) - 20)
root.geometry("{}x{}+{}+{}".format(window_width, window_height, x, y))
root.resizable(False, False)

# -------------------------------------------  MainFrame  -------------------------------------------
main_frame = MyFrame(master=root, width=window_width, height=window_height)
main_frame.place(anchor='center', relx=0.5, rely=0.5)

# Hintergrundbild
background_image = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\solid\basic_map_structures.png"),
                               size=(window_width, window_height))
# noinspection PyTypeChecker
label_background = tk.CTkLabel(master=main_frame,
                               text=None,
                               image=background_image)
label_background.place(x=0, y=0)

# -------------------------------------------  InteractionFrame  -------------------------------------------
# "#212121"
interaction_frame = MyFrame(master=root, width=int(600 * sizing_width), height=int(300 * sizing_height),
                            fg_color="#212121")
interaction_frame.place(anchor='center', x=window_width / 2, y=window_height * 0.3)

# Session ID Eingabefeld
entry_session_id = MyEntry(master=interaction_frame,
                           placeholder_text="Session ID",
                           width=w,
                           height=h,
                           font=("None", h * 0.5),
                           corner_radius=h / 3)
entry_session_id.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
root.update()

# Session ID not found Fehlermeldung
label_error = MyLabel(master=interaction_frame,
                      text="Session ID not found",
                      text_color="red",
                      bg_color="transparent",
                      width=0,
                      height=10 * sizing_height,
                      font=("None", 12 * sizing_height),
                      anchor="w",
                      justify='left')

# Create 'Play/Start Button'
success_function = lambda: root.move_out_of_window(widget_list=[interaction_frame,
                                                                main_frame.winfo_children()[0]],
                                                   direction_list=["up",
                                                                   "down"],
                                                   stepsize=5)

success_function2 = lambda: main_frame.after(1800, lambda: load_lobby_frame(root))

failure_function = lambda: label_error.label_hide_show(
    x=int((entry_session_id.winfo_x() + entry_session_id.winfo_width() / 2) * sizing_width),
    y=int((entry_session_id.winfo_y() - 20) * sizing_height),
    time=3000)

button_play = tk.CTkButton(master=interaction_frame,
                           text="Play",
                           command=lambda: entry_session_id.check_text(target_text=s_id,
                                                                       success_function=success_function,
                                                                       failure_function=failure_function,
                                                                       success_function2=success_function2),
                           width=h,
                           height=h,
                           font=("None", h * 0.4),
                           corner_radius=int(h / 3), )
button_play.place(x=int((entry_session_id.winfo_x() + entry_session_id.winfo_width() + 10) * sizing_width),
                  y=int(entry_session_id.winfo_y() * sizing_height))
root.update()

# Create 'New Session Button'
button_new_session = tk.CTkButton(master=interaction_frame,
                                  text="Create New Session",
                                  width=int((button_play.winfo_x() - entry_session_id.winfo_x() +
                                             button_play.winfo_width()) * sizing_width),
                                  height=int(h / 2 * sizing_height),
                                  #                                 command=lambda: printing(),
                                  font=("None", h * 0.4),
                                  corner_radius=int(h / 3))
button_new_session.place(x=int(entry_session_id.winfo_x() * sizing_width),
                         y=int((entry_session_id.winfo_y() + entry_session_id.winfo_height() + 15) * sizing_height))

root.update()

while root.run:
    root.update()
