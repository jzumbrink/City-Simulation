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

    def __init__(self, starting_x, starting_y, width, height, angle):
        super().__init__(starting_x, starting_y)
        self.nearest_street_node = None
        self.parking_space_position = [starting_x, starting_y]
        self.parking_spaces = []
        self.width = width
        self.height = height
        self.angle = angle

    def rotate_inner_parking_position(self, position):
        if self.angle == 90:
            return [position[1], self.width - position[0] - 6]
        if self.angle == 180:
            return [self.width - position[0] - 6, self.height - position[1] - 14]
        if self.angle == 270:
            return [self.height - position[1] - 14, position[0]]
        return position

    def rotate_parking_street_access_position(self, position):
        if self.angle == 90:
            return [position[1], self.width - position[0] - 8]
        if self.angle == 180:
            return [self.width - position[0] - 8, self.height - position[1] - 14]
        if self.angle == 270:
            return [self.height - position[1] - 8, position[0]]
        return position

    def rotate_parking_alignment(self, horizontal: bool) -> bool:
        return horizontal if self.angle == 0 or self.angle == 180 else not horizontal

    def create_parking_spaces(self, parking_blueprints):
        for parking_blueprint in parking_blueprints:
            x, y = self.rotate_inner_parking_position(parking_blueprint[:2])
            street_x, street_y = self.rotate_parking_street_access_position(parking_blueprint[3:])
            self.parking_spaces.append(ParkingSpace(x + self.position[0], y + self.position[1],
                                                    self.rotate_parking_alignment(parking_blueprint[2]),
                                                    street_x + self.position[0],
                                                    street_y + self.position[1]))


class ParkingSpace:

    def __init__(self, x, y, horizontal, street_x, street_y):
        self.position = [x, y]
        self.car = None
        self.horizontal = horizontal
        self.street_access_position = [street_x, street_y]
