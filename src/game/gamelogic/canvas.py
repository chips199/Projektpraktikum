import pygame


class Canvas:

    def __init__(self, w, h, name="None"):
        self.width = w
        self.height = h
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption(name)

    @staticmethod
    def update():
        """
        update the canvas
        """
        pygame.display.update()

    def get_canvas(self):
        """
        returns the screen for drawing on it
        param:
        :return: Pygame.display
        """
        return self.screen

    @staticmethod
    def draw_text(g, text, size, color, x, y):
        """
        draws text
        @param g: canvas
        @param text: text that should be displayed
        @param size: size of the text
        @param color: color of the text
        @param x: x position
        @param y: y position
        """
        pygame.font.init()
        font = pygame.font.SysFont("Sans-serif", size)
        render = font.render(text, False, color)
        g.blit(render, (x, y))

    def draw_background(self, c):
        """
        fills the canvas with one color
        @param c: the color
        """
        self.screen.fill(c)
