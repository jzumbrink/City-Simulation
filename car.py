from utils import SimulatedSprite
from colors import *
from collections import deque
from math import isclose
import random
import pygame
from turn_type import *

CAR_WIDTH = 8
CAR_HEIGHT = 14

EXIT_SPEED = 0.35
ACCELERATION = 0.03
MAX_SPEED = 1.2

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
        self.current_turn = None
        self.position_round_trip = deque()
        self.position_target = None
        self.speed = 1

    def update(self):
        if self.target is None:
            if len(self.round_trip) > 0:
                self.target = self.round_trip.popleft()
        else:
            if self.at_position_target():
                self.speed = EXIT_SPEED
                if len(self.position_round_trip) > 0:
                    self.position_target = self.position_round_trip.popleft()
                else:
                    self.position_target = None

            if self.at_target():
                self.speed = EXIT_SPEED
                if len(self.round_trip) > 0:
                    self.target = self.round_trip.popleft()
                else:
                    count_neighbors = len(self.target.neighbors)
                    neighbor_index = random.randrange(count_neighbors)
                    self.current_turn = self.target.neighbors[neighbor_index][1]
                    target_position = self.target.neighbors[neighbor_index][0].position

                    if self.current_turn == SOUTH_EAST:
                        self.position_round_trip.append((self.position[0], target_position[1]))
                    if self.current_turn == EAST_NORTH:
                        self.position_round_trip.append((target_position[0], self.position[1]))

                    if self.current_turn == SOUTH_WEST or self.current_turn == NORTH_EAST:
                        self.position_round_trip.append((self.position[0], target_position[1]))
                    if self.current_turn == EAST_SOUTH or self.current_turn == WEST_NORTH:
                        self.position_round_trip.append((target_position[0], self.position[1]))

                    if self.current_turn == WEST_TURN:
                        self.position_round_trip.append((target_position[0] - 20, self.position[1]))
                        self.position_round_trip.append((target_position[0] - 20, target_position[1]))
                    if self.current_turn == NORTH_TURN:
                        self.position_round_trip.append((self.position[0], self.position[1] - 20))
                        self.position_round_trip.append((target_position[0], target_position[1] - 20))
                    if self.current_turn == EAST_TURN:
                        self.position_round_trip.append((self.position[0] + 14, self.position[1]))
                        self.position_round_trip.append((target_position[0] + 14, target_position[1]))
                    if self.current_turn == SOUTH_TURN:
                        self.position_round_trip.append((self.position[0], self.position[1] + 14))
                        self.position_round_trip.append((target_position[0], target_position[1] + 14))

                    self.target = self.target.neighbors[neighbor_index][0]

            target = self.target.position
            self.speed += ACCELERATION
            self.speed = min(self.speed, MAX_SPEED)

            if self.position_target is None:
                if len(self.position_round_trip) > 0:
                    self.position_target = self.position_round_trip.popleft()

            if self.position_target is not None:
                target = self.position_target


            direction_x = target[0] - self.position[0]
            direction_y = target[1] - self.position[1]
            x_update = 0 if direction_x == 0 else self.speed * direction_x/abs(direction_x)
            y_update = 0 if direction_y == 0 else self.speed * direction_y/abs(direction_y)
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


        self.rect = pygame.Rect(int(self.scene_position[0]), int(self.scene_position[1]), CAR_HEIGHT, CAR_WIDTH)

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self.image.get_rect(center=(self.position[0], self.position[1])).center)

    def at_target(self):
        return self.target is not None and isclose(self.target.position[0], self.position[0]) and isclose(self.target.position[1], self.position[1])

    def at_position_target(self):
        return self.position_target is not None and isclose(self.position_target[0], self.position[0]) and isclose(self.position_target[1], self.position[1])
