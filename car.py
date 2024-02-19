from collections import deque
from math import isclose

import pygame

from colors import *
from turn_type import *
from utils import SimulatedSprite
from street_network import str_to_pos
from pathfinding import shortest_path

CAR_WIDTH = 6
CAR_HEIGHT = 14

EXIT_SPEED = 0.35
ACCELERATION = 0.03
MAX_SPEED = 1

MAX_LOAD = 10000


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
        self.load = 0
        self.parked = True
        self.house = None

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

        if not self.parked:
            if self.at_target():
                self.speed = EXIT_SPEED
                self.target = None
                if len(self.round_trip) > 0:
                    self.target = self.round_trip.popleft()

            if self.target is None:
                if len(self.round_trip) > 0:
                    self.target = self.round_trip.popleft()
                else:
                    if (self.position[0] == self.house.parking_space_position[0]
                            and self.position[1] == self.house.parking_space_position[1]):
                        # car is home
                        self.house.rotate_car_in_parking_space()
                        self.unload_supplies()
                        self.house.car_parked = True
                        self.parked = True

            else:
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

    def nearest_street_node(self, street_nodes_str: list):
        min_street_node_str = None
        min_dist = None
        for street_node_str in street_nodes_str:
            street_node_position = str_to_pos(street_node_str)
            if min_dist is None or abs(street_node_position[0] - self.position[0]) + abs(street_node_position[1] - self.position[1]) < min_dist:
                min_dist = abs(street_node_position[0] - self.position[0]) + abs(
                    street_node_position[1] - self.position[1])
                min_street_node_str = street_node_str

        return min_street_node_str

    def load_supplies(self):
        self.load = MAX_LOAD

    def unload_supplies(self):
        self.house.supplies += self.load
        self.load = 0

    def drive_to(self, street_nodes, target_criteria):
        path_there = shortest_path(street_nodes[self.nearest_street_node(street_nodes)], target_criteria)
        last_vertex_str = None
        last_position = None
        for vertex_str in path_there:
            turn = NO_TURN
            if last_vertex_str is None:
                turn = NO_TURN
            else:
                for neighbor, neighbor_turn, _ in street_nodes[last_vertex_str].neighbors:
                    if str(neighbor) == vertex_str:
                        turn = neighbor_turn
                        break

            self.add_target(str_to_pos(vertex_str), turn, last_position)
            last_vertex_str = vertex_str
            last_position = str_to_pos(vertex_str)

    def drive_home(self, street_nodes):
        self.drive_to(street_nodes, lambda node: node == self.house.nearest_street_node)
        self.round_trip.append((self.house.parking_space_position[0], self.house.parking_space_position[1]))
