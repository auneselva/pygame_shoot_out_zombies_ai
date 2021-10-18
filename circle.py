import pygame
from pygame.math import Vector2


class Circle(object):

    def __init__(self, game, r, pos_x, pos_y, color):
        self.game = game
        self.r = r
        self.pos = Vector2(pos_x, pos_y)
        self.color = color

    def draw(self):
        pygame.draw.circle(self.game.screen, self.color, (int(self.pos.x), int(self.pos.y)), self.r, 3)
