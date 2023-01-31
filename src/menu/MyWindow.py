import customtkinter as tk
from tkinter import messagebox

from src.menu.MyFrame import MyFrame
from src.menu.MyLabel import MyLabel


class MyWindow(tk.CTk):
    def __init__(self,
                 window_height: int = 100,
                 window_width: int = 100,
                 *args: object,
                 **kwargs: object) -> None:
        super(MyWindow, self).__init__(*args, **kwargs)
        self.sizing_height = 1
        self.sizing_width = 1
        self.window_height = window_height
        self.window_width = window_width
        self.run = True
        self.process = None
        # Set the appearance mode of the window to 'dark'
        tk.set_appearance_mode("dark")
        # Set the default color theme of the window to 'dark-blue'
        tk.set_default_color_theme("dark-blue")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def set_size(self, width, height):
        self.window_width = width
        self.window_height = height

    def set_sizing(self, sizing_width, sizing_height):
        self.sizing_width = sizing_width
        self.sizing_height = sizing_height

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.run = False
            self.destroy()
            if self.process is not None:
                self.process.kill()

    def set_process(self, process):
        self.process = process

    def move_out_of_window(self,
                           widget_list: list['MyFrame|MyLabel'],
                           direction_list: list[str],
                           delay: int = 20,
                           stepsize: int = 1,
                           anchor: str = tk.NW) -> None:
        """
        Move widgets out of the window via a given direction

        Parameters:
        - widget_list (list('MyFrame|MyLabel')): List containing MyFrame or MyLabel objects that needs to be moved
        - direction_list (list[str]): List of directions that corresponding to the widgets in widget_list.
                                      The direction should be one of 'down', 'up', 'left', 'right'
        - delay (int): Delay time in milliseconds before the next move, default is 20
        - stepsize (int): Number of pixels the widget should be moved each time, default is 1
        - anchor (str): Anchor position for the widget, default is tk.NW ('nw'), can be n, ne, e, se, s, sw, w, nw,
                        or center
        """

        for widget, direction in zip(widget_list, direction_list):
            widget_x = round(widget.winfo_x() * self.sizing_width)
            widget_y = round(widget.winfo_y() * self.sizing_height)

            # move the widget down if direction is 'down' and the y-coordinate of the widget is less than the window
            # height
            if direction == 'down' and widget_y < self.window_height:
                widget.place(x=widget_x, y=widget_y + stepsize, anchor=anchor)

            # move the widget up if direction is 'up' and the y-coordinate of the widget + widget height is greater 0
            elif direction == 'up' and widget_y + widget.winfo_height() > 0:
                widget.place(x=widget_x, y=widget_y - stepsize, anchor=anchor)

            # move the widget left if direction is 'left' and the x-coordinate of the widget + widget width is greater 0
            elif direction == 'left' and widget_x + widget.winfo_width() > 0:
                widget.place(x=widget_x - stepsize, y=widget_y, anchor=anchor)

            # move the widget right if direction is 'right' and the x-coordinate of the widget is less than the
            # window width
            elif direction == 'right' and widget_x < self.window_width:
                widget.place(x=widget_x + stepsize, y=widget_y, anchor=anchor)

            # enters else, when the widget has reached the desired destination
            else:
                # if the widget is a MyFrame instance, clear the frame and forget its placement
                if isinstance(widget, MyFrame):
                    widget.clear_frame()
                    widget.place_forget()

                # if the widget is not a MyFrame instance, destroy the widget
                else:
                    widget.destroy()

                # remove the widget from widget_list and direction from direction_list, since no moving can be done
                # anymore
                widget_list.remove(widget)
                direction_list.remove(direction)

        # enter a recursion after the given delay time, if the widget_list is not empty
        if len(widget_list) > 0:
            widget_list[0].after(delay, lambda: self.move_out_of_window(widget_list,
                                                                        direction_list,
                                                                        delay,
                                                                        stepsize,
                                                                        anchor))
        # self.update()
