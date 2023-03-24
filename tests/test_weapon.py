import datetime
from unittest import mock

import pandas as pd
import src.game.gamelogic.canvas as canvas
import src.game.gamelogic.weapon as weapon
from src.game.gamelogic.weapon import WeaponType as type
import pytest
from unittest.mock import MagicMock, Mock, patch
import os
import pygame

from freezegun import freeze_time


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


def test_getObj():
    """
    checks if the method getObj returns the correct enums for the names
    """
    assert type.getObj("Fist") == type.Fist
    assert type.getObj("Sword") == type.Sword
    assert type.getObj("Laser") == type.Laser


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


def test_get_position_weapon_shot(setup):
    """
    Tests the method get_position_weapon_shot
    """
    for weapon_test in setup:
        if not weapon_test.is_short_range_weapon():
            # define variables
            weapon_test.animation_direction = 1
            weapon_test.frame_width = 10
            weapon_test.frame_height = 10

            # Test for direction left
            result = weapon_test.get_position_weapon_shot(width=10, height=10, x=10, y=0)
            assert result == (5, 46)

            # Test for direction right
            weapon_test.animation_direction = -1
            result = weapon_test.get_position_weapon_shot(width=10, height=10, x=10, y=0)
            assert result == (15, 46)


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


@freeze_time("2023-01-01")
def test_hit(setup):
    """
    Tests the method hit
    Checks that the weapon get the status destroyed when he hits someone
    """
    for i in setup:
        # Check Weapon not destroyed after
        i.destroyed = False
        i.durability = i.weapon_type.value["damage_to_weapon_per_hit"] + 1
        assert i.hit() is None
        assert i.destroyed is False
        assert i.hit() is None
        if i.weapon_type.value["damage_to_weapon_per_hit"] > 0:
            assert i.destroyed is True
        else:
            assert i.destroyed is False

        # Check weapon destroyed
        assert i.hit() is None
        if i.weapon_type.value["damage_to_weapon_per_hit"] > 0:
            assert i.destroyed is True

        # Check if status of weapon is destroyed, when durability is under 0
        i.durability = -1
        assert i.hit() is None
        assert i.destroyed is True

        # Check that the timestamp for last_hit
        assert i.hit() is None
        assert i.last_hit == 1672531200


def test_is_short_range_weapon(setup):
    """
    Tests the Getter Method is_short_range_weapon
    """
    for weapon_test in setup:
        weapon_test.weapon_type.value["IsShortRange"] = True
        assert weapon_test.is_short_range_weapon() is True

        weapon_test.weapon_type.value["IsShortRange"] = False
        assert weapon_test.is_short_range_weapon() is False


def test_get_shot_speed(setup):
    """
    Tests the Getter Method get_shot_speed
    """
    for weapon_test in setup:
        if not weapon_test.is_short_range_weapon():
            weapon_test.weapon_type.value["shot_speed"] = 10
            assert weapon_test.get_shot_speed() == 10


def test_get_shot_speed(setup):
    """
    Tests the Getter Method get_shot_speed
    """
    for weapon_test in setup:
        weapon_test.weapon_type.value["Damage"] = 10
        assert weapon_test.get_weapon_damage() == 10


def test_check_hit(setup):
    """
    Tests the method check hit
    Checks if a player can be hit by another player
    Checks if a player can be hit by a shot from another player
    checks if a player dies when he has no life points left
    """
    # Mock Players

    player1 = MagicMock()
    player2 = MagicMock()
    player3 = MagicMock()
    player4 = MagicMock()

    # Set Player1 up

    player1.solid_df = pd.DataFrame([(2, 2)], columns=["x", "y"])
    player1.health = 15
    player1.is_blocking = True

    player_list = [player4, player3, player2, player1]
    player1.killed_by = [0, 0, 0, 1, 0]
    canvas = MagicMock()
    player1.weapon.animation_running = False
    for i in player_list:
        i.weapon = MagicMock()
        i.weapon.get_dataframe = Mock(return_value=pd.DataFrame([(2, 2)], columns=["x", "y"]))

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

    # Test for Damage, static method
    weapon.Weapon.check_hit(player1, player_list, MagicMock(), canvas)
    assert player1.health == 10
    player1.is_blocking = False
    player4.weapon.hitted_me = False

    player1.is_alive.return_value = False
    weapon.Weapon.check_hit(player1, player_list, MagicMock(), canvas)
    assert player1.health == 0
    assert player1.killed_by[1] == 1

    # Test weapon shots
    # Preparation for tests
    player4.weapon_shots = []
    player4.weapon_shots.append(MagicMock())
    player4.weapon_shots[0].damage = 10
    player4.weapon_shots[0].get_dataframe = Mock(return_value=pd.DataFrame([(2, 2)], columns=["x", "y"]))
    player4.weapon_shots[0].active = True
    for i in player_list:
        i.weapon.animation_running = False
    player1.health = 20

    # Check if player gets Damage when shot is active
    weapon.Weapon.check_hit(player1, player_list, MagicMock(), canvas)
    assert player1.health == 10

    # Check if player gets Damage when shot is inactive
    player4.weapon_shots[0].active = False
    weapon.Weapon.check_hit(player1, player_list, MagicMock(), canvas)
    assert player1.health == 10
