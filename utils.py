import pygame


class SimulatedSprite(pygame.sprite.Sprite):

    def __init__(self, starting_x, starting_y):
        super().__init__()
        self.position = [starting_x, starting_y]
        self.scene_position = [starting_x, starting_y]

    def update_position(self, diff_x, diff_y):
        self.position[0] += diff_x
        self.position[1] += diff_y
        self.scene_position[0] += diff_x
        self.scene_position[1] += diff_y

    def set_position(self, x, y):
        diff_x = x - self.position[0]
        diff_y = y - self.position[1]
        self.update_position(diff_x, diff_y)


class Building(SimulatedSprite):

    def __init__(self, starting_x, starting_y):
        super().__init__(starting_x, starting_y)
        self.nearest_street_node = None
