from __future__ import annotations

import inspect

import customtkinter as tk

from typing import Optional, Callable, Union


class MyEntry(tk.CTkEntry):
    def __init__(self, *args, **kwargs):
        super(MyEntry, self).__init__(*args, **kwargs)

    def check_text(self,
                   target_text: str = "-200",
                   success_function: Optional[Union[Callable, None]] = None,  # type:ignore[type-arg]
                   failure_function: Optional[Union[Callable, None]] = None,  # type:ignore[type-arg]
                   **kwargs: Optional[Union[Callable, None]]) -> None:  # type:ignore[type-arg]

        # Check if entered text is equal to target text
        if self.get() == target_text:  # For Testing
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


import multiprocessing
import time


def printing(text):
    while True:
        print(text)
        time.sleep(0.014)


if __name__ == "__main__":
    process = multiprocessing.Process(target=printing, args=("Process", ))
    process.start()
    while True:
        print("Main")
        # time.sleep(0.014)
