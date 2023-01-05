import pygame
import os
import game.map
import pytest
from unittest.mock import MagicMock, Mock


@pytest.fixture
def test_map():
    wrk_dir = os.path.os.path.dirname(__file__)
    basic_map = wrk_dir + "/../src/basicmap"
    test_game = Mock()
    test_game.height = 50
    test_game.width = 50
    test_map = game.map.Map(test_game, basic_map)

    test_map.solid = [(1, 2), (3, 4), (5, 6), (-8, -9)]
    test_map.background = pygame.Surface((20, 10))

    return test_map


def test_collide(test_map):
    assert test_map.collides([(8, 9), (11, 24)]) is False
    assert test_map.collides([(1, 2), (3, 4), (5, 6)]) is True
    assert test_map.collides([(5, 6), (3, 4), (9, 11)]) is True
    assert test_map.collides([(3, 4)]) is True
    assert test_map.collides([]) is False
    assert test_map.collides([(-1, 2)]) is False
    assert test_map.collides(([(-1, -2)])) is False
    assert test_map.collides([(12, 13), (-8, -9)]) is True


def test_draw(test_map):
    rect = pygame.Rect(0, 0, test_map.game.width, test_map.game.height)
    screen = MagicMock()
    test_map.draw(screen)
    screen.blit.assert_called_with(test_map.background, rect)
    test_map.staticimages = [1]
    test_map.static_objects_img = None
    test_map.draw(screen)
    # screen.blit.assert_called_with(test_map.background, rect)
    screen.blit.assert_called_with(test_map.static_objects_img, rect)

    test_map.background = "no Surface"
    test_map.draw(screen)
    screen.fill.assert_called_with((41, 41, 41))
