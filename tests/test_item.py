import src.game.gamelogic.item as item
import src.game.gamelogic.weapon as weapon
import src.game.gamelogic.canvas as canvas
import pytest
import os
import pandas as pd
import pygame


@pytest.fixture(scope="session")
def setup():
    pygame.init()
    pygame.display.set_mode((50, 50))
    waffe = os.path.join(os.path.dirname(__file__), "mock_resources", "basicmap", "waffen")
    item1 = item.Item(weapon.WeaponType.Sword, (10, 10), os.path.join(waffe, "schwert", "sword.png"))
    item2 = item.Item(weapon.WeaponType.Fist, (0, 0), os.path.join(waffe, "faeuste", "fists_magenta.png"))
    item3 = item.Item(weapon.WeaponType.Laser, (20, 20), os.path.join(waffe, "laser", "laser.png"))
    return item1, item2, item3


def test_get_item(setup):
    dt = pd.DataFrame([(1, 2), (3, 4)], columns=['x', 'y'])
    for i in setup:
        assert i.getItem(dt, weapon.WeaponType.Fist) == i.type or i.getItem(dt, weapon.WeaponType.Fist) is None
        assert i.getItem(dt, weapon.WeaponType.Sword) == i.type or i.getItem(dt, weapon.WeaponType.Sword) is None
        assert i.getItem(dt, weapon.WeaponType.Laser) == i.type or i.getItem(dt, weapon.WeaponType.Laser) is None


def test_draw(setup):
    test_canvas = canvas.Canvas(50, 50)
    for i in setup:
        assert i.draw(test_canvas.get_canvas()) is None
