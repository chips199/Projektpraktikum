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

    def set_rel_positions(self,
                          x: float,
                          y: float) -> None:
        """
        Set the relative positions for the widget

        :param x: The x position of the widget, as a float between 0 and 1
        :param y: The y position of the widget, as a float between 0 and 1
        :return: None
        """
        self.current_relx = x
        self.current_rely = y

    def set_sizing(self,
                   sizing_width: float,
                   sizing_height: float) -> None:
        """
        Set the scaling factor for the width and height of the window.

        :param sizing_width: Scaling factor for width
        :param sizing_height: Scaling factor for height

        :return: None
        """
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

        """
        Move self (Label) to the given relativ y pos

        :param direction: direction in which to move, either 0 for right or 1 for left
        :param rely: relative y-coordinate to move to. 1.0 is 100% 0.0 is 0% of screensize
        :param stepsize: stepsize per frame in percent, 1.0 means 100% of screen, default is 0.0028, so 0.28% per frame
        :param delay: Delay time in milliseconds before the next move, default is 15
        :param ending_function: A function that will be called once the rely coordinate is reached, default is None
        :return: None
        """

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

    def idle_animation_on_y_axis(self,
                                 upper_y: float = 0.0,
                                 lower_y: float = 0.0,
                                 next_pos: str = "one",
                                 delay: int = 25,
                                 stepsize: float = 0.004) -> None:

        """
        Perform an idle animation by alternating between two positions.

        :param upper_y: The upper rely position to move to
        :param lower_y: The lower rely position to move to
        :param next_pos: The next position to move to. Either "one" or "two". Default is "one".
        :param delay: Delay time in milliseconds before the next move. Default is 25.
        :param stepsize: stepsize per frame in percent, 1.0 means 100% of screen, default is 0.004, so 0.4% per frame
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
