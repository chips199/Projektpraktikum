import customtkinter as tk


class MyFrame(tk.CTkFrame):
    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the MyFrame class.

        :param args: Arguments for the super class
        :param kwargs: Keyword arguments for the super class
        """
        # calling super class constructor
        super(MyFrame, self).__init__(*args, **kwargs)

    def clear_frame(self) -> None:
        """
        Remove all widgets from the frame

        :return: None
        """
        # Iterate through each child widget of the frame
        for widget in self.winfo_children():
            # Removing the widget from the frame
            widget.place_forget()
            # Destroying the widget, removing it from memory
            widget.destroy()
