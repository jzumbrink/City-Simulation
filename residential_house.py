import random

import pygame

from utils import Building

PARKING_SPACE_LOCATION = {
    0: [9, 24],
    90: [24, 25],
    180: [25, 2],
    270: [2, 9]
}

START_SUPPLIES = 5500
MIN_SUPPLY_DECREASE = 0.2
MAX_SUPPLY_DECREASE = 5
MIN_SUPPLY_AMOUNT = 5000


class ResidentialHouse(Building):

    def __init__(self, x, y, angle=0):
        super().__init__(x, y)

        self.image = pygame.image.load("res/house.png")
        self.rect = self.image.get_rect()
        self.image = pygame.transform.rotate(self.image, angle)
        self.angle = angle
        self.car = None
        self.car_parked = False
        self.supplies = START_SUPPLIES
        self.supply_decrease_rate = MIN_SUPPLY_DECREASE + random.random() * (MAX_SUPPLY_DECREASE - MIN_SUPPLY_DECREASE)
        self.parking_space_position = [self.position[0] + PARKING_SPACE_LOCATION[self.angle][0],
                                       self.position[1] + PARKING_SPACE_LOCATION[self.angle][1]]

    def add_car_to_house(self, car):
        self.car = car
        self.car_parked = True
        car.house = self
        car.set_position(self.parking_space_position[0], self.parking_space_position[1])
        self.rotate_car_in_parking_space()

    def rotate_car_in_parking_space(self):
        if self.angle == 90 or self.angle == 270:
            self.car.set_horizontal()
        else:
            self.car.set_vertical()

    def update(self):
        self.rect = pygame.Rect(self.scene_position[0], self.scene_position[1], 40, 40)
        self.update_supplies()

    def update_supplies(self):
        self.supplies -= self.supply_decrease_rate

    def low_on_supplies(self) -> bool:
        return self.supplies < MIN_SUPPLY_AMOUNT
