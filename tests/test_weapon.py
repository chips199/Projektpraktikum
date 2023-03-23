import pandas as pd
import src.game.gamelogic.canvas as canvas
import src.game.gamelogic.weapon as weapon
from src.game.gamelogic.weapon import WeaponType as type
import pytest
from unittest.mock import MagicMock, Mock
import os
import pygame


@pytest.fixture()
def setup():
    pygame.init()
    pygame.display.set_mode((50, 50))
    wrk_dir = os.path.abspath(os.path.dirname(__file__))
    basicmap = os.path.join(wrk_dir, "mock_resources", "basicmap")
    pygame.display.set_mode((50, 50))
    test_weapon1 = weapon.Weapon(type.Fist, os.path.join(basicmap, "waffen", "faeuste"), [0, 0],
                                 os.path.join(basicmap, "waffen", "faeuste", "animation", "fists_magenta_animation"))
    test_weapon2 = weapon.Weapon(type.Sword, os.path.join(basicmap, "waffen", "schwert"), [1, 1],
                                 os.path.join(basicmap, "waffen", "schwert", "animation",
                                              "sword_hold_animation_magenta"))
    test_weapon3 = weapon.Weapon(type.Laser, os.path.join(basicmap, "waffen", "laser"), [2, 2],
                                 os.path.join(basicmap, "waffen", "laser", "animation", "laser_hold_magenta"))

    return test_weapon1, test_weapon2, test_weapon3


def test_get_dataframe(setup):
    for i in setup:
        i.animation_direction = 0
        assert isinstance(i.get_dataframe(), pd.DataFrame)
        i.animation_direction = 1
        assert isinstance(i.get_dataframe(), pd.DataFrame)


def test_draw(setup):
    test_canvas = canvas.Canvas(100, 100)
    for i in setup:
        i.x = 100
        i.y = 100
        i.animation_direction = 0
        assert i.draw(y=10, height=100, width=100, x=10, g=test_canvas.get_canvas()) is None
        i.animation_direction = 1
        assert i.draw(y=10, height=100, x=10, width=100, g=test_canvas.get_canvas()) is None


def test_can_hit(setup):
    for i in setup:
        i.durability = 10
        i.last_hit = 100000
        assert i.can_hit() is True
        i.durability = 0
        i.last_hit = 100000
        assert i.can_hit() is False
        i.durability = 1
        i.last_hit = 0
        assert i.can_hit() is True
        i.durability = 0
        i.last_hit = 0
        assert i.can_hit() is False


def test_hit(setup):
    for i in setup:
        i.destroyed = False
        i.durability = 5
        assert i.hit() is None
        assert i.destroyed is False
        i.durability = 1
        assert i.hit() is None
        assert i.destroyed is False
        assert i.hit() is None
        assert i.destroyed is True
        i.durability = -1
        assert i.hit() is None
        assert i.destroyed is True


def test_check_hit(setup):
    # Mock Players

    player1 = MagicMock()
    player2 = MagicMock()
    player3 = MagicMock()
    player4 = MagicMock()

    # Set Player1 up

    player1.solid_df = pd.DataFrame([(2, 2)], columns=["x", "y"])
    player1.health = 50
    player1.is_blocking = True

    # Set Player list up

    player4.weapon.animation_running = True
    player3.weapon.animation_running = False
    player2.weapon.animation_running = True
    player1.weapon.animation_running = False
    player1.weapon.hitted_me = True
    player2.weapon.hitted_me = True
    player3.weapon.hitted_me = False
    player4.weapon.hitted_me = False
    player1.weapon.weapon_type = weapon.WeaponType.Fist
    player2.weapon.weapon_type = weapon.WeaponType.Fist
    player3.weapon.weapon_type = weapon.WeaponType.Fist
    player4.weapon.weapon_type = weapon.WeaponType.Fist
    player_list = [player4, player3, player2, player1]
    player1.killed_by = [0, 0, 0, 1, 0]
    canvas = MagicMock()
    player1.weapon.animation_running = False
    for i in player_list:
        i.weapon = MagicMock()
        i.weapon.get_dataframe = Mock(return_value=pd.DataFrame([(2, 2)], columns=["x", "y"]))

    # Test for Damage, static method

    weapon.Weapon.check_hit(player1, player_list, MagicMock(), canvas)
    assert player1.health == 25
    player1.is_blocking = False
    weapon.Weapon.check_hit(player1, player_list, MagicMock(), canvas)
    assert player1.health == 0
    player1.is_alive = False
    weapon.Weapon.check_hit(player1, player_list, MagicMock(), canvas)
    assert player1.killed_by[4] == 2

    # Test for shot
    player1.add
