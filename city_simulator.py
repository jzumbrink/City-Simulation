from math import isclose

from colors import *
from street_network import *
from utils import SimulatedSprite


def update_camera_location(x_diff, y_diff):
    global game_sprites
    for game_sprite in game_sprites:
        game_sprite.scene_position[0] += x_diff
        game_sprite.scene_position[1] += y_diff

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
            if self.at_target() and len(self.round_trip) > 0:
                self.target = self.round_trip.popleft()

            direction_x = self.target[0] - self.position[0]
            direction_y = self.target[1] - self.position[1]
            self.update_position(diff_x=0 if direction_x == 0 else 0.5 * direction_x/abs(direction_x),
                                 diff_y=0 if direction_y == 0 else 0.5 * direction_y / abs(direction_y))

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
        return self.target is not None and isclose(self.target[0], self.position[0]) and isclose(self.target[1], self.position[1])


class House(SimulatedSprite):

    def __init__(self, x, y, angle=0):
        super().__init__(x, y)

        self.image = pygame.image.load("res/house.png")
        self.rect = self.image.get_rect()
        self.image = pygame.transform.rotate(self.image, angle)

    def update(self):
        self.rect = pygame.Rect(self.scene_position[0], self.scene_position[1], 40, 40)
def handle_key_event(event):
    if event.key == pygame.K_w:
        update_camera_location(x_diff=0, y_diff=10)
    if event.key == pygame.K_a:
        update_camera_location(x_diff=10, y_diff=0)
    if event.key == pygame.K_s:
        update_camera_location(x_diff=0, y_diff=-10)
    if event.key == pygame.K_d:
        update_camera_location(x_diff=-10, y_diff=0)

def handle_pressed_keys():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        update_camera_location(x_diff=0, y_diff=3)
    if keys[pygame.K_a]:
        update_camera_location(x_diff=3, y_diff=0)
    if keys[pygame.K_s]:
        update_camera_location(x_diff=0, y_diff=-3)
    if keys[pygame.K_d]:
        update_camera_location(x_diff=-3, y_diff=0)


pygame.init()

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("City Simulation")
clock = pygame.time.Clock()

sprites_list = pygame.sprite.Group()

# init sprites etc.
car1 = Car(30, 30)


car2 = Car(300, 70, BLUE)
car3 = Car(100, 240, GREEN)
house1 = House(150, 65)
house2 = House(320, 210, angle=270)

game_sprites = [car1, car2, car3, house1, house2]

s1 = StreetNode(140, 123)
s2 = StreetNode(290, 123)
s3 = StreetNode(293, 225)

car1.round_trip.append(s1.position)
car1.round_trip.append(s2.position)
car1.round_trip.append(s3.position)

car2.round_trip.append([309, 255])
car2.round_trip.append([309, 123])
car2.round_trip.append([319, 124])
car2.round_trip.append([350, 124])
car2.round_trip.append([369, 105])
car2.round_trip.append([369, 63])
car2.round_trip.append([350, 48])
car2.round_trip.append([350, 64])
car2.round_trip.append([353, 74])
car2.round_trip.append([353, 105])
car2.round_trip.append([350, 108])
car2.round_trip.append([169, 108])

street_nodes, connection_sprites, street_sprites = create_streets([
    [[380, 105], [140, 105]],
    [[320, 45], [350, 45]],
    [[350, 135], [350, 45]],
    [[290, 105], [290, 225]]
])


for s in street_sprites + [House(330, 5)] + [StreetNodeSprite(s.position[0], s.position[1]) for s in list(street_nodes.values())] + connection_sprites:
    sprites_list.add(s)
    game_sprites.append(s)

sprites_list.add(house1)
sprites_list.add(house2)
sprites_list.add(car1)
sprites_list.add(car2)
sprites_list.add(car3)

while True:
    # check for user actions
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            handle_key_event(event)
    handle_pressed_keys()

    # game logic
    if car1.at_target():
        #print("Arrived at target")
        pass
        #car1.target = (random.randrange(0, 480), random.randrange(0, 400))

    # draw game
    screen.fill(WHITE)
    sprites_list.update()
    sprites_list.draw(screen)

    # update window
    pygame.display.flip()

    # set refresh times
    clock.tick(60)