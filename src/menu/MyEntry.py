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


import glob
import os
import sys

from PIL import Image


def split(gif):
    print('%s will be split...' % gif)

    frame = Image.open(gif)
    name = gif.split(".")[0]
    dir = os.getcwd() + r"\animation\%s" % (name)
    try:
        os.makedirs(dir)
    except FileExistsError:
        # directory already exists
        pass
    frameIdx = 0

    try:
        while 1:
            print('\tseek frame %d' % frameIdx)
            frame.seek(frameIdx)
            print('\tsave frame %d' % frameIdx)
            # print(os.getcwd() + r"\tmp\%s" % (name))
            frame.save('%s/%s.png' % (dir, frameIdx))
            frameIdx += 1
    except EOFError:
        print('done.')
        return name



def to_sprite(p):
    # get your images using glob
    iconMap = glob.glob(f"animation/{p}/*.png")
    # just take the even ones
    # iconMap = iconMap[::2]

    print(len(iconMap))

    images = [Image.open(filename) for filename in iconMap]

    print("%d images will be combined." % len(images))

    image_width, image_height = images[0].size

    print("all images assumed to be %d by %d." % (image_width, image_height))

    master_width = (image_width * len(images))
    # seperate each image with lots of whitespace
    master_height = image_height
    print("the master image will by %d by %d" % (master_width, master_height))
    print("creating image...")
    master = Image.new(
        mode='RGBA',
        size=(master_width, master_height),
        color=(0, 0, 0, 0))  # fully transparent

    print("created.")

    for count, image in enumerate(images):
        location = image_width * count
        print("adding %s at %d..." % (iconMap[count][1], location))
        master.paste(image, (location, 0))
        print("added.")
    print("done adding icons.")

    print("saving master.png...")
    master.save(f'animation/{p}.png')
    print("saved!")


def main():
    os.chdir(r"C:\Users\range\Desktop\gif")
    for file in glob.glob("*.gif"):
        print(file)
        to_sprite(split(file))


if __name__ == '__main__':
    main()


