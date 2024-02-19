from car import Car
from street_network import *
from utils import SimulatedSprite

show_street_nodes = False

def update_camera_location(x_diff, y_diff):
    global game_sprites
    for game_sprite in game_sprites:
        game_sprite.scene_position[0] += x_diff
        game_sprite.scene_position[1] += y_diff


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

street_nodes, connection_sprites, street_sprites, intersection_connections, no_turn_intersection_connections = create_streets([
    [[410, 105], [140, 105]],
    [[410, 105], [410, 75]],
    [[440, 75], [440, 45]],
    [[470, 75], [410, 75]],
    [[470, 75], [470, 225]],
    [[470, 195], [530, 195]],
    [[530, 105], [530, 225]],
    [[320, 45], [350, 45]],
    [[350, 135], [350, 45]],
    [[290, 105], [290, 225]]
])

car1.round_trip.append(list(street_nodes.values())[0])
car2.round_trip.append(list(street_nodes.values())[0])
car3.round_trip.append(list(street_nodes.values())[0])


for s in street_sprites + [House(330, 5)]:
    sprites_list.add(s)
    game_sprites.append(s)

if show_street_nodes:
    for s in connection_sprites + [StreetNodeSprite(s.position[0], s.position[1]) for s in list(street_nodes.values())]:
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
    if show_street_nodes:
        for intersection_connection in intersection_connections:
            pygame.draw.line(screen, YELLOW, intersection_connection[0], intersection_connection[1])
        for intersection_connection in no_turn_intersection_connections:
            pygame.draw.line(screen, BROWN, intersection_connection[0], intersection_connection[1])

    # update window
    pygame.display.flip()

    # set refresh times
    clock.tick(60)