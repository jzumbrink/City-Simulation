from utils import Building
import pygame

SUPERMARKET_WIDTH = 80
SUPERMARKET_HEIGHT = 80


class Supermarket(Building):

    def __init__(self, x, y):
        super().__init__(x, y)

        self.image = pygame.image.load("res/supermarket.png")
        self.rect = self.image.get_rect()

    def update(self):
        self.rect = pygame.Rect(self.scene_position[0], self.scene_position[1], SUPERMARKET_WIDTH, SUPERMARKET_HEIGHT)
