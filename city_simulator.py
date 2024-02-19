from street_network import *
from world import create_example_world
from settings import *

pygame.init()

screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)
clock = pygame.time.Clock()


street_nodes, connection_sprites, street_sprites, intersection_connections, no_turn_intersection_connections = create_streets([
    [[410, 105], [80, 105]],
    [[140, 105], [140, 75]],
    [[410, 105], [410, 75]],
    [[440, 75], [440, 45]],
    [[470, 75], [410, 75]],
    [[470, 75], [470, 255]],
    [[470, 195], [530, 195]],
    [[530, 105], [530, 225]],
    [[320, 45], [350, 45]],
    [[350, 135], [350, 45]],
    [[290, 105], [290, 255]],
    [[290, 255], [470, 255]]
])

city = create_example_world(street_nodes, connection_sprites, street_sprites)


while True:
    # check for user actions
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            city.handle_key_event(event)
    city.handle_pressed_keys()

    # game logic
    city.simulate_turn()

    # draw game
    screen.fill(WHITE)
    city.sprites_list.update()
    city.sprites_list.draw(screen)
    if SHOW_STREET_NODES:
        for intersection_connection in intersection_connections:
            pygame.draw.line(screen, YELLOW, city.position_to_camera_position(intersection_connection[0]),
                             city.position_to_camera_position(intersection_connection[1]))
        for intersection_connection in no_turn_intersection_connections:
            pygame.draw.line(screen, BROWN, city.position_to_camera_position(intersection_connection[0]),
                             city.position_to_camera_position(intersection_connection[1]))

    # update window
    pygame.display.flip()

    # set refresh times
    clock.tick(60)