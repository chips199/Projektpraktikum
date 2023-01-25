from __future__ import annotations

import inspect
from time import sleep
from threading import Thread

import customtkinter as tk

from typing import Optional, Callable, Union


class MyEntry(tk.CTkEntry):
    def __init__(self, *args, **kwargs):
        super(MyEntry, self).__init__(*args, **kwargs)

    def check_text(self,
                   target_text: str = "-200",
                   success_function: Optional[Union[Callable, None]] = None,    # type:ignore[type-arg]
                   failure_function: Optional[Union[Callable, None]] = None,    # type:ignore[type-arg]
                   **kwargs: Optional[Union[Callable, None]]) -> None:          # type:ignore[type-arg]

        # Check if entered text is equal to target text
        if self.get() == target_text:               # For Testing
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



def threaded_function(arg):
    for i in range(arg):
        print("running")
        sleep(0.0001)

def threaded_function2():
    print("running 2")
    sleep(0.0001)
    print("running test")
    sleep(0.0001)


if __name__ == "__main__":
    thread = Thread(target=threaded_function, args=(10,))
    thread2 = Thread(target=threaded_function2, args=())
    thread.start()
    thread2.start()
    while True:
        print("running")
        sleep(0.1)
    # thread.join()
    # thread2.join()
    # print("thread finished...exiting")