import inspect
import customtkinter as tk

from typing import Optional, Callable


class MyEntry(tk.CTkEntry):
    def __init__(self, *args, **kwargs):
        super(MyEntry, self).__init__(*args, **kwargs)

    def check_text(self,
                   target_text: str = "-200",
                   success_function: Optional[Callable] = None,
                   failure_function: Optional[Callable] = None,
                   **kwargs: Optional[Callable]) -> None:

        # Check if entered text is equal to target text
        if self.get() == target_text:
            # Execute success_function if provided
            if success_function is not None:
                success_function()
            # Iterate through kwargs, check if value is function and execute
            for key, value in kwargs.items():
                if inspect.isfunction(value):
                    value()
        else:
            # Execute failure_function if provided
            if failure_function is not None:
                failure_function()
