from multiprocessing import Process

import customtkinter as tk

from src.game.menu.MyFrame import MyFrame
from src.game.menu.MyLabel import MyLabel


class MyWindow(tk.CTk):
    def __init__(self,
                 window_height: int = 100,
                 window_width: int = 100,
                 *args: object,
                 **kwargs: object) -> None:
        """
        Initializes a new instance of the MyWindow class

        :param window_height: Height of the window, default is 100
        :param window_width: Width of the window, default is 100
        :param args: Additional arguments for the super class
        :param kwargs: Additional keyword arguments for the super class
        """
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

    def set_size(self,
                 width: int,
                 height: int) -> None:
        """
        This method sets the width and height

        :param width: int
        :param height: int
        :return: None
        """
        self.window_width = width
        self.window_height = height

    def set_sizing(self,
                   sizing_width: int,
                   sizing_height: int) -> None:
        """
        This method sets the sizing width and height

        :param sizing_width: int
        :param sizing_height: int
        :return: None
        """
        self.sizing_width = sizing_width
        self.sizing_height = sizing_height

    def on_closing(self) -> None:
        """
        This method is called when the window is closed
        :return: None
        """
        if self.process is not None:
            # If the process is not None, then it kills the process
            self.process.kill()  # type:ignore[unreachable]
        # Set the run attribute to False
        self.run = False
        # Destroys the window
        self.destroy()

    def set_process(self,
                    process: Process) -> None:
        """
        This method sets the process attribute

        :param process: object(Process)
        :return: None
        """
        self.process = process  # type:ignore[assignment]

    def move_out_of_window(self,
                           widget: ['MyFrame|MyLabel'],  # type:ignore[valid-type]
                           direction: str,
                           delay: int = 17,
                           stepsize: int = 1,
                           anchor: str = tk.NW) -> None:
        """
        Move widget out of the window via a given direction

        :param widget: A widget beeing an MyFrame or MyLabel objects that needs to be moved
        :param direction: directions inwhich the widgets should leave the window.
                          The direction should be one of 'down', 'up', 'left', 'right'
        :param delay: Delay time in milliseconds before the next move, default is 17
        :param stepsize: Number of pixels the widget should be moved each time, default is 1
        :param anchor: Anchor position for the widget, default is tk.NW ('nw'), can be n, ne, e, se, s, sw, w, nw,
                       or center
        :return: None
        """

        recursion = False

        widget_x = round(widget.winfo_x() * self.sizing_width)
        widget_y = round(widget.winfo_y() * self.sizing_height)

        # move the widget down if direction is 'down' and the y-coordinate of the widget is less than the window
        # height
        if direction == 'down' and widget_y < self.window_height:
            widget.place(x=widget_x, y=widget_y + stepsize, anchor=anchor)
            recursion = True

        # move the widget up if direction is 'up' and the y-coordinate of the widget + widget height is greater 0
        elif direction == 'up' and widget_y + widget.winfo_height() > 0:
            widget.place(x=widget_x, y=widget_y - stepsize, anchor=anchor)
            recursion = True

        # move the widget left if direction is 'left' and the x-coordinate of the widget + widget width is greater 0
        elif direction == 'left' and widget_x + widget.winfo_width() > 0:
            widget.place(x=widget_x - stepsize, y=widget_y, anchor=anchor)
            recursion = True

        # move the widget right if direction is 'right' and the x-coordinate of the widget is less than the
        # window width
        elif direction == 'right' and widget_x < self.window_width:
            widget.place(x=widget_x + stepsize, y=widget_y, anchor=anchor)
            recursion = True

        # enters else, when the widget has reached the desired destination
        else:
            # if the widget is a MyFrame instance, clear the frame and forget its placement
            if isinstance(widget, MyFrame):
                widget.clear_frame()
                widget.place_forget()

            # if the widget is not a MyFrame instance, destroy the widget
            else:
                widget.destroy()

        # enter a recursion after the given delay time, if the widget_list is not empty
        if recursion:
            widget.after(delay, lambda: self.move_out_of_window(widget,
                                                                direction,
                                                                delay,
                                                                stepsize,
                                                                anchor))
        self.update()
