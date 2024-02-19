from utils import Building
import pygame

SUPERMARKET_WIDTH = 80
SUPERMARKET_HEIGHT = 80

PARKING_BLUEPRINT = [
    [7, 64, False, 7, 84],
    [18, 64, False, 18, 84],
    [29, 64, False, 29, 84],
    [40, 64, False, 40, 84],
    [51, 64, False, 51, 84],
]


class Supermarket(Building):

    def __init__(self, x, y, angle=0):
        super().__init__(x, y, SUPERMARKET_WIDTH, SUPERMARKET_HEIGHT, angle)

        self.image = pygame.image.load("res/supermarket.png")
        self.rect = self.image.get_rect()
        self.image = pygame.transform.rotate(self.image, angle)
        self.create_parking_spaces(PARKING_BLUEPRINT)

    def update(self):
        self.rect = pygame.Rect(self.scene_position[0], self.scene_position[1], SUPERMARKET_WIDTH, SUPERMARKET_HEIGHT)
