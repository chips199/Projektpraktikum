import src.game.gamelogic.item as item
import src.game.gamelogic.weapon as weapon
import src.game.gamelogic.canvas as canvas
import pytest
import os
import pandas as pd
import pygame


@pytest.fixture(scope="session")
def setup():

    # set up test subjects

    pygame.init()
    pygame.display.set_mode((50, 50))
    waffe = os.path.join(os.path.dirname(__file__), "mock_resources", "basicmap", "waffen")
    item1 = item.Item("sword", (10, 10), os.path.join(waffe, "schwert", "sword.png"))
    item2 = item.Item("fist", (0, 0), os.path.join(waffe, "faeuste", "fists_magenta.png"))
    item3 = item.Item("laser", (20, 20), os.path.join(waffe, "laser", "laser.png"))
    return item1, item2, item3


def test_get_item(setup):

    # define parameters

    dt = pd.DataFrame([(1, 2), (3, 4)], columns=['x', 'y'])
    result = []

    for i in setup:

        # iterate through test subjects and test for result

        fist = i.getItem(dt, weapon.WeaponType.Fist)
        sword = i.getItem(dt, weapon.WeaponType.Sword)
        laser = i.getItem(dt, weapon.WeaponType.Laser)
        assert fist == i.type or fist is None
        result.append(fist)
        assert sword == i.type or sword is None
        result.append(sword)
        assert laser == i.type or laser is None
        result.append(laser)
        assert result.__contains__(fist)
        assert result.__contains__(sword)
        assert result.__contains__(laser)


def test_draw(setup):

    # test draw method executing without error

    test_canvas = canvas.Canvas(50, 50)
    for i in setup:
        assert i.draw(test_canvas.get_canvas()) is None
