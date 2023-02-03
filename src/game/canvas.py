import pygame


class Canvas:

    def __init__(self, w, h, name="None"):
        self.width = w
        self.height = h
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption(name)

    @staticmethod
    def update():
        pygame.display.update()

    def get_canvas(self):
        return self.screen

    @staticmethod
    def draw_text(g, text, size, color, x, y):
        pygame.font.init()
        font = pygame.font.SysFont("Sans-serif", size)
        render = font.render(text, False, color)
        g.blit(render, (x, y))

    def draw_background(self, c):
        self.screen.fill(c)
