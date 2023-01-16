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
    interaction_frame.configure(width=window_width, height=150)
    interaction_frame.place(x=0, y=250)

    session_id_label = MyLabel(master=main_frame,
                               text="Session ID: {}".format(s_id),
                               font=("None", 30))
    session_id_label.place(x=50, y=30)

    player_image = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\player\basic_player_orange.png"),
                               size=(49, 142))
    label_image = MyLabel(master=main_frame,
                          text=None,
                          image=player_image)
    label_image.place(x=175, y=250)
    root_window.update()

    player_image2 = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\player\basic_player_purple.png"),
                                size=(49, 142))
    label_image2 = MyLabel(master=main_frame, text=None, image=player_image2)
    label_image2.place(x=575, y=250)

    player_image3 = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\player\basic_player_turquoise.png"),
                                size=(49, 142))
    label_image3 = MyLabel(master=main_frame, text=None, image=player_image3)
    label_image3.place(x=975, y=250)

    player_image4 = tk.CTkImage(dark_image=Image.open(wrk_dir + r"\..\basicmap\player\basic_player_magenta.png"),
                                size=(49, 142))
    label_image4 = MyLabel(master=main_frame, text=None, image=player_image4)
    label_image4.place(x=1375, y=250)
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
window_width = 1600
window_height = 900
s_id = "1"

# -------------------------------------------  Window  -------------------------------------------
# configure root window
root = MyWindow(window_width=1600,
                window_height=900)
root.title('TestName')

# get screen width and height
ws = root.winfo_screenwidth()  # width of the screen
hs = root.winfo_screenheight()  # height of the screen

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
                               size=(1600, 900))
# noinspection PyTypeChecker
label_background = tk.CTkLabel(master=main_frame,
                               text=None,
                               image=background_image)
label_background.place(x=0, y=0)

# -------------------------------------------  InteractionFrame  -------------------------------------------
interaction_frame = MyFrame(master=root, width=600, height=300, fg_color="#212121")
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
                      height=10,
                      font=("None", 12),
                      anchor="w",
                      justify='left')
label_error.place(x=entry_session_id.winfo_x() + entry_session_id.winfo_width() / 2,
                  y=entry_session_id.winfo_y() - 20,
                  anchor=tk.CENTER)
label_error.place_forget()
root.update()

# Create 'Play/Start Button'
success_function = lambda: root.move_out_of_window(widget_list=[interaction_frame,
                                                                main_frame.winfo_children()[0]],
                                                   direction_list=["up",
                                                                   "down"],
                                                   stepsize=5)

success_function2 = lambda: main_frame.after(1800, lambda: load_lobby_frame(root))

failure_function = lambda: label_error.label_hide_show(x=int(entry_session_id.winfo_x() + entry_session_id.winfo_width()
                                                             / 2),
                                                       y=entry_session_id.winfo_y() - 20,
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
button_play.place(x=entry_session_id.winfo_x() + entry_session_id.winfo_width() + 10,
                  y=entry_session_id.winfo_y())
root.update()

# Create 'New Session Button'
button_new_session = tk.CTkButton(master=interaction_frame,
                                  text="Create New Session",
                                  width=button_play.winfo_x() - entry_session_id.winfo_x() + button_play.winfo_width(),
                                  height=int(h / 2),
                                  #                                 command=lambda: printing(),
                                  font=("None", h * 0.4),
                                  corner_radius=int(h / 3))
button_new_session.place(x=entry_session_id.winfo_x(),
                         y=entry_session_id.winfo_y() + entry_session_id.winfo_height() + 15)

root.update()

while root.run:
    root.update()
