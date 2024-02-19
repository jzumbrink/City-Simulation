from collections import deque
from math import isclose

import pygame

from colors import *
from turn_type import *
from utils import SimulatedSprite

CAR_WIDTH = 6
CAR_HEIGHT = 14

EXIT_SPEED = 0.35
ACCELERATION = 0.03
MAX_SPEED = 1


class Car(SimulatedSprite):

    def __init__(self, starting_x, starting_y, color=RED):
        super().__init__(starting_x, starting_y)

        self.image = pygame.Surface((CAR_HEIGHT, CAR_WIDTH))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.image = pygame.transform.rotate(self.image, 0)
        self.target = None
        self.round_trip = deque()
        self.horizontal = True
        self.speed = 1

    def add_target(self, target_position, turn, last_position=None):
        if last_position is None:
            last_position = self.position

        if turn == SOUTH_EAST:
            self.round_trip.append((last_position[0], target_position[1]))
        if turn == EAST_NORTH:
            self.round_trip.append((target_position[0], last_position[1]))

        if turn == SOUTH_WEST or turn == NORTH_EAST:
            self.round_trip.append((last_position[0], target_position[1]))
        if turn == EAST_SOUTH or turn == WEST_NORTH:
            self.round_trip.append((target_position[0], last_position[1]))

        if turn == WEST_TURN:
            self.round_trip.append((target_position[0] - 20, last_position[1]))
            self.round_trip.append((target_position[0] - 20, target_position[1]))
        if turn == NORTH_TURN:
            self.round_trip.append((last_position[0], last_position[1] - 20))
            self.round_trip.append((target_position[0], target_position[1] - 20))
        if turn == EAST_TURN:
            self.round_trip.append((last_position[0] + 14, last_position[1]))
            self.round_trip.append((target_position[0] + 14, target_position[1]))
        if turn == SOUTH_TURN:
            self.round_trip.append((last_position[0], last_position[1] + 14))
            self.round_trip.append((target_position[0], target_position[1] + 14))

        self.round_trip.append((target_position[0], target_position[1]))

    def update(self):
        if self.target is None:
            if len(self.round_trip) > 0:
                self.target = self.round_trip.popleft()
        else:
            if self.at_target():
                self.speed = EXIT_SPEED
                if len(self.round_trip) > 0:
                    self.target = self.round_trip.popleft()

            self.speed += ACCELERATION
            self.speed = min(self.speed, MAX_SPEED)

            direction_x = self.target[0] - self.position[0]
            direction_y = self.target[1] - self.position[1]
            x_update = 0 if direction_x == 0 else self.speed * direction_x / abs(direction_x)
            y_update = 0 if direction_y == 0 else self.speed * direction_y / abs(direction_y)
            if 0 < x_update > direction_x or 0 > x_update < direction_x:
                x_update = direction_x
            if 0 < y_update > direction_y or 0 > y_update < direction_y:
                y_update = direction_y
            self.update_position(diff_x=x_update,
                                 diff_y=y_update)

            if abs(direction_x) > abs(direction_y) and not self.horizontal:
                self.set_horizontal()
            if abs(direction_y) > abs(direction_x) and self.horizontal:
                self.set_vertical()

        self.rect = pygame.Rect(int(self.scene_position[0]), int(self.scene_position[1]), CAR_HEIGHT, CAR_WIDTH)

    def set_vertical(self):
        if self.horizontal:
            self.image = pygame.transform.rotate(self.image, 90)
            self.horizontal = False

    def set_horizontal(self):
        if not self.horizontal:
            self.image = pygame.transform.rotate(self.image, 90)
            self.horizontal = True

    def at_target(self):
        return self.target is not None and isclose(self.target[0], self.position[0]) and isclose(self.target[1],
                                                                                                 self.position[1])
