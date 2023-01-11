from typing import Optional, Callable
import customtkinter as tk


class MyLabel(tk.CTkLabel):
    def __init__(self, *args, **kwargs):
        super(MyLabel, self).__init__(*args, **kwargs)

        # create instance variable to store the scheduled event id
        self.after_id = None

    def label_hide_show(self,
                        x: int,
                        y: int,
                        time: int) -> None:

        # Check if there's an scheduled event
        if self.after_id is not None:
            # cancel the scheduled event
            self.after_cancel(self.after_id)

        # place the label at x, y with center anchor
        self.place(x=x, y=y, anchor=tk.CENTER)

        # schedule an event to hide label after a certain amount of time
        self.after_id = self.after(time, lambda: self.place_forget())

    def move_to(self,
                x: int = 0,
                y: int = 0,
                stepsize: int = 5,
                delay: int = 25,
                ending_function: Optional[Callable] = None) -> None:

        """
        Move self (Label) to the given x and y coordinate

        Parameters:
            - x (int): x-coordinate to move to
            - y (int): y-coordinate to move to
            - stepsize (int): Number of pixels the widget should be moved each time, default is 5
            - delay (int): Delay time in milliseconds before the next move, default is 25
            - ending_function ('function'): A function that will be called once the x and y coordinates are reached,
                                            Default is None
        """

        # get the current x and y position of the widget
        widget_x = self.winfo_x()
        widget_y = self.winfo_y()

        # calculate the difference from current and desired position
        x_diff = abs(widget_x - x)
        y_diff = abs(widget_y - y)

        # set new x-coordinate
        if x_diff > stepsize:
            if widget_x < x:
                new_x = widget_x + stepsize
            else:
                new_x = widget_x - stepsize
        else:
            new_x = x

        # set new y-coordinate
        if y_diff > stepsize:
            if widget_y < y:
                new_y = widget_y + stepsize
            else:
                new_y = widget_y - stepsize
        else:
            new_y = y

        # move the widget to new position
        self.place(x=new_x, y=new_y)

        # if there is a difference in either x or y coordinate, enter a recursion after the given delay time
        if x_diff != 0 or y_diff != 0:
            self.after(delay, lambda: self.move_to(x, y, stepsize, delay, ending_function))

        # otherwise the position is reached, so call the ending_function if it is handed over
        else:
            if ending_function is not None:
                ending_function()

    def idle_animation(self,
                       pos_one: list[int] = (0, 0),
                       pos_two: list[int] = (0, 0),
                       next_pos: str = "two",
                       delay: int = 30,
                       stepsize: int = 1) -> None:

        """
        Move the label between two positions in a loop with a certain delay and stepsize

        Parameters:
        - pos_one (list[int]): x and y coordinate of position one
        - pos_two (list[int]): x and y coordinate of position two
        - next_pos (str): position in which the label should be moved, should be either 'one' or 'two'
        - delay (int): Delay time in milliseconds before the next move, default is 30
        - stepsize (int): Number of pixels the label should be moved each time, default is 1
        """

        # move the label to position one
        if next_pos == "one":
            self.move_to(x=pos_one[0],
                         y=pos_one[1],
                         stepsize=stepsize,
                         delay=delay,
                         ending_function=lambda: self.idle_animation(pos_one,
                                                                     pos_two,
                                                                     next_pos="two"))
        # move the label to position two
        elif next_pos == "two":
            self.move_to(x=pos_two[0],
                         y=pos_two[1],
                         stepsize=stepsize,
                         delay=delay,
                         ending_function=lambda: self.idle_animation(pos_one,
                                                                     pos_two,
                                                                     next_pos="one"))
