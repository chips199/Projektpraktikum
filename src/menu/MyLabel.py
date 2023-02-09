from typing import Optional, Callable, Union
import customtkinter as tk


class MyLabel(tk.CTkLabel):
    def __init__(self, *args, **kwargs):
        """
        Initialize the MyLabel class

        :param args: Arguments for superclass
        :param kwargs: Keyword Arguments for superclass
        """
        super(MyLabel, self).__init__(*args, **kwargs)

        # create instance variable to store the scheduled event id
        self.sizing_height = 1
        self.sizing_width = 1
        self.after_id = None
        self.current_rely = 0.0
        self.current_relx = 0.0

    def set_rel_positions(self, x, y):
        self.current_relx = x
        self.current_rely = y

    def set_sizing(self, sizing_width, sizing_height):
        self.sizing_width = sizing_width
        self.sizing_height = sizing_height

    def label_hide_show(self,
                        x: int,
                        y: int,
                        time: int,
                        message: str = "No message given") -> None:
        """
        Show the label at the given x and y position for a given amount of time

        :param x: X-coordinate of the label on the window
        :param y: Y-coordinate of the label on the window
        :param time: Amount of time in milliseconds for which the label should be visible
        :param message: Message to be displayed in the label
        """
        # Check if there's an scheduled event
        if self.after_id is not None:
            # cancel the scheduled event
            self.after_cancel(self.after_id)

        self.configure(text=message)

        # place the label at x, y with center anchor
        self.place(x=x, y=y, anchor=tk.CENTER)

        # schedule an event to hide label after a certain amount of time
        self.after_id = self.after(time, lambda: self.place_forget())

    def move_on_y_axis(self,
                       direction: int = 0,
                       rely: float = 0.0,
                       stepsize: float = 0.0028,
                       delay: int = 15,
                       ending_function: Optional[Union[Callable, None]] = None) -> None:  # type:ignore[type-arg]

        if rely == round(self.current_rely, 2):
            if ending_function is not None:
                ending_function()
            return
        elif direction == 0:
            self.current_rely -= stepsize
        elif direction == 1:
            self.current_rely += stepsize

        self.place(relx=self.current_relx, rely=self.current_rely)

        self.after(delay, lambda: self.move_on_y_axis(direction, rely, stepsize, delay, ending_function))

    def move_to(self,
                x: int = 0,
                y: int = 0,
                stepsize: int = 5,
                delay: int = 25,
                ending_function: Optional[Union[Callable, None]] = None) -> None:  # type:ignore[type-arg]

        """
        Move self (Label) to the given x and y coordinate

        :param x: x-coordinate to move to
        :param y: y-coordinate to move to
        :param stepsize: Number of pixels the widget should be moved each time, default is 5
        :param delay: Delay time in milliseconds before the next move, default is 25
        :param ending_function: A function that will be called once the x and y coordinates are reached, default is None
        :return: None
        """
        x_sized = round(x * self.sizing_width)
        y_sized = round(y * self.sizing_height)
        stepsize_sized = round(stepsize * self.sizing_height)

        # get the current x and y position of the widget
        widget_x = round(self.winfo_x() * self.sizing_width)
        widget_y = round(self.winfo_y() * self.sizing_height)

        # calculate the difference from current and desired position
        x_diff = abs(widget_x - x_sized)
        y_diff = abs(widget_y - y_sized)

        # set new x-coordinate
        if x_diff > stepsize_sized:
            if widget_x < x_sized:
                new_x = widget_x + stepsize_sized
            else:
                new_x = widget_x - stepsize_sized
        else:
            new_x = x_sized

        # set new y-coordinate
        if y_diff > stepsize_sized:
            if widget_y < y_sized:
                new_y = widget_y + stepsize_sized
            else:
                new_y = widget_y - stepsize_sized
        else:
            new_y = y_sized

        # move the widget to new position
        self.place(x=new_x, y=new_y)

        # if there is a difference in either x or y coordinate, enter a recursion after the given delay time
        if x_diff > stepsize_sized or y_diff > stepsize_sized:
            self.after(delay, lambda: self.move_to(x, y, stepsize, delay, ending_function))

        # otherwise the position is reached, so call the ending_function if it is handed over
        else:
            if ending_function is not None:
                ending_function()

    def idle_animation_on_y_axis(self,
                                 upper_y: float = 0.0,
                                 lower_y: float = 0.0,
                                 next_pos: str = "one",
                                 delay: int = 25,
                                 stepsize: float = 0.004) -> None:

        """
        Perform an idle animation by alternating between two positions.

        :param pos_one: The first position to move to (x, y). Default is (0, 0).
        :param pos_two: The second position to move to (x, y). Default is (0, 0).
        :param next_pos: The next position to move to. Either "one" or "two". Default is "two".
        :param delay: Delay time in milliseconds before the next move. Default is 35.
        :param stepsize: Number of pixels the widget should be moved each time. Default is 1.
        :return: None
        """

        # move the label to position one
        if next_pos == "one":
            self.move_on_y_axis(direction=0,
                                rely=upper_y,
                                stepsize=stepsize,
                                delay=delay,
                                ending_function=lambda: self.idle_animation_on_y_axis(upper_y,
                                                                                      lower_y,
                                                                                      next_pos="two",
                                                                                      stepsize=stepsize))
        # move the label to position two
        elif next_pos == "two":
            self.move_on_y_axis(direction=1,
                                rely=lower_y,
                                stepsize=stepsize,
                                delay=delay,
                                ending_function=lambda: self.idle_animation_on_y_axis(upper_y,
                                                                                      lower_y,
                                                                                      next_pos="one",
                                                                                      stepsize=stepsize))
