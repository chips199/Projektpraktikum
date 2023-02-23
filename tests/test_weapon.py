import src.game.gamelogic.weapon as weapon
from src.game.gamelogic.weapon import WeaponType as type
import pytest
from unittest.mock import MagicMock
import os


@pytest.fixture()
def setup():
    wrk_dir = os.path.abspath(os.path.dirname(__file__))
    basicmap = str(wrk_dir) + r"/basicmap"

    # test_weapon1 = weapon.Weapon(type.Fist, basicmap + r"/waffen/feuste/sound_effects/sound_destroy.mp3", 0, [0, 0],
    #                              basicmap + r"/waffen/faeuste/animation/fists_magenta_animation")
    #
    # test_weapon2 = weapon.Weapon(type.Sword, basicmap + r"/waffen/schwert/sound_effects/sound_destroy.mp3", 1, [1, 1],
    #                              basicmap + r"/waffen/schwert/animation/sword_hold_animation_magenta")

    test_weapon1 = weapon.Weapon(type.Fist, "/home/runner/work/Projektpraktikum/Projektpraktikum/basicmap/waffen/feuste/sound_effects/sound_destroy.mp3", 0, [0, 0],
                                 basicmap + "/home/runner/work/Projektpraktikum/Projektpraktikum/basicmap/waffen/faeuste/animation/fists_magenta_animation")

    test_weapon2 = weapon.Weapon(type.Sword, basicmap + "/home/runner/work/Projektpraktikum/Projektpraktikum/basicmap/waffen/schwert/sound_effects/sound_destroy.mp3", 1, [1, 1],
                                 basicmap + "/home/runner/work/Projektpraktikum/Projektpraktikum/basicmap/waffen/schwert/animation/sword_hold_animation_magenta")
    return test_weapon1, test_weapon2


def test_get_dataframe(setup):
    setup[0].animation_direction = 0
    setup[1].animation_direction = 0
    assert setup[0].get_dataframe() is None
    assert setup[1].get_dataframe() is None
    setup[0].animation_direction = 1
    setup[1].animation_direction = 1
    assert setup[0].get_dataframe() is None
    assert setup[1].get_dataframe() is None


def test_draw(setup):
    setup[0].animation_direction = 0
    setup[1].animation_direction = 0
    assert setup[0].draw() is None
    assert setup[1].draw() is None
    setup[0].animation_direction = 1
    setup[1].animation_direction = 1
    assert setup[0].draw() is None
    assert setup[1].draw() is None


def test_can_hit(setup):
    setup[0].durability = 10
    setup[0].last_hit = 100000
    setup[1].durability = 10
    setup[1].last_hit = 100000
    assert setup[0].can_hit is False
    assert setup[1].can_hit is False
    setup[0].durability = 0
    setup[0].last_hit = 100000
    setup[1].durability = 0
    setup[1].last_hit = 100000
    assert setup[0].can_hit is False
    assert setup[1].can_hit is False
    setup[0].durability = 1
    setup[0].last_hit = 0
    setup[1].durability = 1
    setup[1].last_hit = 0
    assert setup[0].can_hit is False
    assert setup[1].can_hit is False
    setup[0].durability = 0
    setup[0].last_hit = 0
    setup[1].durability = 0
    setup[1].last_hit = 0
    assert setup[0].can_hit is True
    assert setup[1].can_hit is True


def test_hit(setup):
    assert setup[0].hit() is None
    assert setup[1].hit() is None
    setup[0].durability = 0
    setup[1].durability = 0
    assert setup[0].hit() is None
    assert setup[1].hit() is None
    setup[0].durability = -1
    setup[1].durability = -1
    assert setup[0].hit() is None
    assert setup[1].hit() is None


def test_check_hit(setup):
    player1 = MagicMock()
    player2 = MagicMock()
    player3 = MagicMock()
    player4 = MagicMock()
    pd = MagicMock()
    player1.health = 50
    player1.is_blocking = True
    player4.weapon.animation_running = True
    player3.weapon.animation_running = False
    player2.weapon.animation_running = True
    player1.weapon.animation_running = False
    player2.weapon.hitted_me = True
    player4.weapon.hitted_me = True
    player3.weapon.hitted_me = False
    player1.weapon.hitted_me = False
    player1.weapon.weapon_type.value = 50
    player2.weapon.weapon_type.value = 50
    player3.weapon.weapon_type.value = 50
    player4.weapon.weapon_type.value = 50
    pd.merge = [1, 2, 4]
    player_list = [player4, player3, player2, player1]
    player1.blood_animation.set_pos = True
    player1.blood_animation.draw_animation_once = True
    player1.is_alive = True
    player1.killed_by = [0, 0, 0, 1]
    canvas = MagicMock()
    player1.weapon.animation_running = False
    setup.check_hit(player1, player_list, MagicMock(), canvas)
    assert player1.health == 25
    player1.is_blocking = False
    setup.check_hit(player1, player_list, MagicMock(), canvas)
    assert player1.health == 0
    player1.is_alive = False
    setup.check_hit(player1, player_list, MagicMock(), canvas)
    assert player1.killed_by[4] == 2
