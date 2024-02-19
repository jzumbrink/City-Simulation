from utils import SimulatedSprite
from colors import *
from collections import deque
from math import isclose
import random
import pygame

class Car(SimulatedSprite):

    def __init__(self, starting_x, starting_y, color=RED):
        super().__init__(starting_x, starting_y)

        self.image = pygame.Surface((15, 8))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.image = pygame.transform.rotate(self.image, 0)
        self.target = None
        self.round_trip = deque()
        self.horizontal = True

    def update(self):
        if self.target is None:
            if len(self.round_trip) > 0:
                self.target = self.round_trip.popleft()
        else:
            if self.at_target():
                if len(self.round_trip) > 0:
                    self.target = self.round_trip.popleft()
                else:
                    count_neighbors = len(self.target.neighbors)
                    neighbor_index = random.randrange(count_neighbors)
                    self.target = self.target.neighbors[neighbor_index][0]

            speed = 1.34

            direction_x = self.target.position[0] - self.position[0]
            direction_y = self.target.position[1] - self.position[1]
            x_update = 0 if direction_x == 0 else speed * direction_x/abs(direction_x)
            y_update = 0 if direction_y == 0 else speed * direction_y/abs(direction_y)
            if 0 < x_update > direction_x or 0 > x_update < direction_x:
                x_update = direction_x
            if 0 < y_update > direction_y or 0 > y_update < direction_y:
                y_update = direction_y
            self.update_position(diff_x=x_update,
                                 diff_y=y_update)

            if abs(direction_x) > abs(direction_y) and not self.horizontal:
                self.image = pygame.transform.rotate(self.image, 90)
                self.horizontal = True
            if abs(direction_y) > abs(direction_x) and self.horizontal:
                self.image = pygame.transform.rotate(self.image, 90)
                self.horizontal = False


        self.rect = pygame.Rect(int(self.scene_position[0]), int(self.scene_position[1]), 15, 8)

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self.image.get_rect(center=(self.position[0], self.position[1])).center)

    def at_target(self):
        return self.target is not None and isclose(self.target.position[0], self.position[0]) and isclose(self.target.position[1], self.position[1])
