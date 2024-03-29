import pygame
from car import Car
from residential_house import ResidentialHouse
from supermarket import Supermarket
from colors import *
from utils import SimulatedSprite, ParkingSpace
from pathfinding import shortest_path
from street_network import str_to_pos, StreetNodeSprite
from settings import *
from turn_type import *


class World:

    def __init__(self):
        self.game_sprites = []
        self.sprites_list = pygame.sprite.Group()

        self.cars = []
        self.houses = []
        self.supermarkets = []

        self.street_sprites = []
        self.connection_sprites = []
        self.street_node_sprites = []

        self.street_nodes = []

        self.camera_diff = [0, 0]

    def position_to_camera_position(self, position):
        return [position[0] + self.camera_diff[0], position[1] + self.camera_diff[1]]

    def add_sprite(self, sprite: SimulatedSprite, sprite_type: list):
        sprite_type.append(sprite)
        self.game_sprites.append(sprite)
        self.sprites_list.add(sprite)

    def add_sprite_list(self, sprites: list, sprite_type: list):
        sprite_type += sprites
        self.game_sprites += sprites
        for sprite in sprites:
            self.sprites_list.add(sprite)

    def update_camera_location(self, x_diff, y_diff):
        for game_sprite in self.game_sprites:
            game_sprite.scene_position[0] += x_diff
            game_sprite.scene_position[1] += y_diff
        self.camera_diff[0] += x_diff
        self.camera_diff[1] += y_diff

    def handle_key_event(self, event):
        if event.key == pygame.K_w:
            self.update_camera_location(x_diff=0, y_diff=10)
        if event.key == pygame.K_a:
            self.update_camera_location(x_diff=10, y_diff=0)
        if event.key == pygame.K_s:
            self.update_camera_location(x_diff=0, y_diff=-10)
        if event.key == pygame.K_d:
            self.update_camera_location(x_diff=-10, y_diff=0)

    def handle_pressed_keys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.update_camera_location(x_diff=0, y_diff=3)
        if keys[pygame.K_a]:
            self.update_camera_location(x_diff=3, y_diff=0)
        if keys[pygame.K_s]:
            self.update_camera_location(x_diff=0, y_diff=-3)
        if keys[pygame.K_d]:
            self.update_camera_location(x_diff=-3, y_diff=0)

    def align_houses_to_street_nodes(self):
        for building in self.houses + self.supermarkets:
            min_street_node_str = None
            min_dist = None
            for street_node_str in self.street_nodes.keys():
                street_node_position = str_to_pos(street_node_str)
                if min_dist is None or abs(street_node_position[0] - building.parking_space_position[0]) + abs(street_node_position[1] - building.parking_space_position[1]) < min_dist:
                    min_dist = abs(street_node_position[0] - building.parking_space_position[0]) + abs(street_node_position[1] - building.parking_space_position[1])
                    min_street_node_str = street_node_str
            if min_street_node_str is not None:
                building.nearest_street_node = self.street_nodes[min_street_node_str]

        for supermarket in self.supermarkets:
            if supermarket.nearest_street_node is not None:
                supermarket.nearest_street_node.has_supermarket_connection = True

    def simulate_houses(self):
        for house in self.houses:
            if house.car_parked and house.low_on_supplies():
                house.car_parked = False
                house.car.parked = False
                # get new supplies
                house.car.drive_to(self.street_nodes, lambda node: node.has_supermarket_connection)

    def simulate_cars(self):
        for car in self.cars:
            if car.target is None and not car.parked:
                car_street_node = car
                if self.street_nodes[car.nearest_street_node(self.street_nodes)].has_supermarket_connection:
                    car.load_supplies()
                    car.drive_home(self.street_nodes)

    def simulate_turn(self):
        self.simulate_houses()
        self.simulate_cars()

    def add_parking_space(self, parking_space: ParkingSpace):
        sx, sy = parking_space.street_access_position



def create_example_world(street_nodes: list, connection_sprites: list, street_sprites: list) -> World:
    city = World()

    city.street_nodes = street_nodes
    city.add_sprite_list(street_sprites, city.street_sprites)
    if SHOW_STREET_NODES:
        city.add_sprite_list(connection_sprites, city.connection_sprites)
        for street_node in street_nodes.values():
            city.add_sprite(StreetNodeSprite(street_node.position[0], street_node.position[1]), city.street_node_sprites)
    city.align_houses_to_street_nodes()

    cars = [
        Car(30, 30),
        Car(300, 70, BLUE),
        Car(100, 240, GREEN),
        Car(100, 240, ORANGE),
        Car(100, 240, YELLOW),
        Car(100, 240, BROWN),
    ]

    houses = [
        ResidentialHouse(90, 65),
        ResidentialHouse(320, 210, angle=270),
        ResidentialHouse(150, 135, angle=180),
        ResidentialHouse(430, 210, angle=90),
        ResidentialHouse(330, 5),
        ResidentialHouse(310, 285, angle=180)
    ]

    for car, house in zip(cars, houses):
        house.add_car_to_house(car)
        city.add_sprite(house, city.houses)
        city.add_sprite(car, city.cars)

    supermarket1 = Supermarket(560, 125, angle=270)
    city.add_sprite(supermarket1, city.supermarkets)


    supermarket2 = Supermarket(170, 25)
    city.add_sprite(supermarket2, city.supermarkets)

    for parking_space in supermarket1.parking_spaces + supermarket2.parking_spaces:
        city.add_sprite(StreetNodeSprite(parking_space.street_access_position[0], parking_space.street_access_position[1]), city.street_node_sprites)

    city.align_houses_to_street_nodes()

    return city
