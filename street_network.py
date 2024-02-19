from queue import PriorityQueue
from utils import SimulatedSprite
import pygame
from collections import deque
from colors import *
from turn_type import *

STREET = "street"
CORNER = "street90"
JUNCTION = "street_junction"
SMALL_JUNCTION = "streetT"
DEAD_END = "street_end"


class StreetNodeSprite(SimulatedSprite):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.position = [x, y]

        self.image = pygame.Surface((3, 3))
        self.image.fill(RED)
        self.rect = self.image.get_rect()

    def update(self):
        self.rect = pygame.Rect(self.scene_position[0], self.scene_position[1], 1, 1)


class StreetNodeConnectionSprite(SimulatedSprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1)

        self.position = [x1, y1]
        self.width = x2 - x1
        self.height = y2 - y1

        self.image = pygame.Surface((self.width + 1, self.height + 1))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()

    def update(self):
        self.rect = pygame.Rect(self.scene_position[0], self.scene_position[1], self.width + 1, self.height + 1)





class StreetNode:

    def __init__(self, x, y):
        self.neighbors = []
        self.position = [x, y]

    def add_neighbor(self, street_node, direction):
        self.neighbors.append([street_node, direction, abs(self.position[0] - street_node.position[0]) + abs(
            self.position[1] - street_node.position[1])])


class Street(SimulatedSprite):

    def __init__(self, x, y, type=STREET, angle=0):
        super().__init__(x, y)

        self.image = pygame.image.load("res/{}.png".format(type))
        self.rect = self.image.get_rect()
        self.image = pygame.transform.rotate(self.image, angle)

    def update(self):
        self.rect = pygame.Rect(self.scene_position[0], self.scene_position[1], 30, 30)

    def rot90(self):
        self.image = pygame.transform.rotate(self.image, 90)


def pos_to_str(pos):
    return "{}-{}".format(pos[0], pos[1])


def str_to_pos(s):
    return list(map(int, s.split("-")))


def is_street_vertical(street):
    return street[0][0] == street[1][0]


def create_streets(streets):
    # normalize streets
    # first comes the most western and most northern point
    for street in streets:
        if street[0][0] > street[1][0] or street[0][1] > street[1][1]:
            street[1], street[0] = street[0], street[1]

    # merge streets together is possible TODO
    """for street1 in streets:
        for street2 in streets:
            if is_street_vertical(street1) and is_street_vertical(street2):
                if street2[0][1] <= street1[1][1] <= street2[1][1] and street1[0][1] <= street2[1][1] <= street1[1][1]:
    """

    positions = {}

    for street in streets:
        for position1, position2 in zip(street, street[::-1]):
            pos_str = pos_to_str(position1)
            if pos_str not in positions:
                positions[pos_str] = []
            positions[pos_str].append(position2)

    intersections_set = set()
    for i, street1 in enumerate(streets):
        for street2 in streets[i + 1:]:
            # find intersection if possible
            if is_street_vertical(street1) != is_street_vertical(street2):
                comp_street1, comp_street2 = street1, street2
                if is_street_vertical(street2):
                    comp_street1, comp_street2 = street2, street1
                    # street1 is always the vertical one
                if comp_street2[0][0] <= comp_street1[0][0] <= comp_street2[1][0] and comp_street1[0][1] <= \
                        comp_street2[0][1] <= comp_street1[1][1]:
                    # there is an intersection
                    intersections_set.add(pos_to_str([comp_street1[0][0], comp_street2[0][1]]))

    intersections = []
    for intersection in intersections_set:
        intersections.append(str_to_pos(intersection))

    # split streets into more streets at intersections
    old_streets = deque()
    for street in streets:
        old_streets.append(street)
    streets = []
    while len(old_streets) > 0:
        street = old_streets.popleft()
        for intersection in intersections:
            if (is_street_vertical(street) and street[0][0] == intersection[0] and street[0][1] < intersection[1] <
                    street[1][1]
                    or street[0][1] == intersection[1] and street[0][0] < intersection[0] < street[1][0]):
                # intersection splits street
                old_streets.append([street[0], intersection])
                old_streets.append([intersection, street[1]])
                break
        else:
            streets.append(street)

    connection_sprites = []
    streets_sprites = []

    # create street nodes
    street_nodes = {}
    intersection_nodes = {intersection_str: [None for _ in range(8)] for intersection_str in intersections_set}
    for street in streets:
        street_node1, street_node2, street_node3, street_node4 = None, None, None, None
        if is_street_vertical(street):
            street_node1 = StreetNode(street[0][0] + 4, street[0][1] + 29)
            street_node2 = StreetNode(street[1][0] + 4, street[1][1])

            street_node3 = StreetNode(street[0][0] + 18, street[0][1] + 29)
            street_node4 = StreetNode(street[1][0] + 18, street[1][1])

            street_node1.add_neighbor(street_node2, NO_TURN)
            street_node4.add_neighbor(street_node3, NO_TURN)

            connection_sprites.append(
                StreetNodeConnectionSprite(street_node1.position[0], street_node1.position[1], street_node2.position[0],
                                           street_node2.position[1]))
            connection_sprites.append(
                StreetNodeConnectionSprite(street_node3.position[0], street_node3.position[1], street_node4.position[0],
                                           street_node4.position[1]))

            # find first intersection
            for intersection in intersections:
                if street[0][0] == intersection[0] and street[0][1] == intersection[1]:
                    intersection_nodes[pos_to_str(intersection)][0] = street_node1
                    intersection_nodes[pos_to_str(intersection)][1] = street_node3
                    break
            else:
                # dead end
                street_node3.add_neighbor(street_node1, NORTH_TURN)
                connection_sprites.append(
                    StreetNodeConnectionSprite(street_node1.position[0], street_node1.position[1],
                                               street_node3.position[0],
                                               street_node3.position[1]))
                streets_sprites.append(Street(street[0][0], street[0][1], type=DEAD_END, angle=90))

            # find second intersection
            for intersection in intersections:
                if street[1][0] == intersection[0] and street[1][1] == intersection[1]:
                    intersection_nodes[pos_to_str(intersection)][5] = street_node2
                    intersection_nodes[pos_to_str(intersection)][4] = street_node4
                    break
            else:
                # dead end
                street_node2.add_neighbor(street_node4, SOUTH_TURN)
                connection_sprites.append(
                    StreetNodeConnectionSprite(street_node2.position[0], street_node2.position[1],
                                               street_node4.position[0],
                                               street_node4.position[1]))
                streets_sprites.append(Street(street[1][0], street[1][1], type=DEAD_END, angle=270))
        else:
            street_node1 = StreetNode(street[0][0] + 29, street[0][1] + 18)
            street_node2 = StreetNode(street[1][0], street[1][1] + 18)

            street_node3 = StreetNode(street[0][0] + 29, street[0][1] + 4)
            street_node4 = StreetNode(street[1][0], street[1][1] + 4)

            street_node1.add_neighbor(street_node2, NO_TURN)
            street_node4.add_neighbor(street_node3, NO_TURN)
            connection_sprites.append(
                StreetNodeConnectionSprite(street_node1.position[0], street_node1.position[1], street_node2.position[0],
                                           street_node2.position[1]))
            connection_sprites.append(
                StreetNodeConnectionSprite(street_node3.position[0], street_node3.position[1], street_node4.position[0],
                                           street_node4.position[1]))

            # find first intersection
            for intersection in intersections:
                if street[0][0] == intersection[0] and street[0][1] == intersection[1]:
                    intersection_nodes[pos_to_str(intersection)][2] = street_node1
                    intersection_nodes[pos_to_str(intersection)][3] = street_node3
                    break
            else:
                # dead end
                street_node3.add_neighbor(street_node1, WEST_TURN)
                connection_sprites.append(
                    StreetNodeConnectionSprite(street_node3.position[0], street_node3.position[1],
                                               street_node1.position[0],
                                               street_node1.position[1]))
                streets_sprites.append(Street(street[0][0], street[0][1], type=DEAD_END, angle=180))

            # find second intersection
            for intersection in intersections:
                if street[1][0] == intersection[0] and street[1][1] == intersection[1]:
                    intersection_nodes[pos_to_str(intersection)][7] = street_node2
                    intersection_nodes[pos_to_str(intersection)][6] = street_node4
                    break
            else:
                # dead end
                street_node2.add_neighbor(street_node4, EAST_TURN)
                connection_sprites.append(
                    StreetNodeConnectionSprite(street_node4.position[0], street_node4.position[1],
                                               street_node2.position[0],
                                               street_node2.position[1]))
                streets_sprites.append(Street(street[1][0], street[1][1], type=DEAD_END, angle=0))
        for street_node in [street_node1, street_node2, street_node3, street_node4]:
            street_nodes[pos_to_str(street_node.position)] = street_node

    # make the sprites for all normal streets
    for street in streets:
        if is_street_vertical(street):
            street_length = street[1][1] - street[0][1]
            for i in range((street_length - 30) // 30):
                streets_sprites.append(Street(street[0][0], street[0][1] + 30 * (i + 1), angle=90))
        else:
            street_length = street[1][0] - street[0][0]
            for i in range((street_length - 30) // 30):
                streets_sprites.append(Street(street[0][0] + 30 * (i + 1), street[0][1]))

    intersection_connections = []
    no_turn_intersection_connections = []

    # make the sprites for the intersections and connect all the street nodes in the intersection
    for intersection_str in intersections_set:
        intersection_node = intersection_nodes[intersection_str]
        intersection = str_to_pos(intersection_str)
        count_none = 0
        first_missing = None
        last_missing = None
        for i, street_intersection_node in enumerate(intersection_node):
            if street_intersection_node is None:
                count_none += 1
                if first_missing is None:
                    first_missing = i
                last_missing = i

        if count_none == 0:
            streets_sprites.append(Street(intersection[0], intersection[1], type=JUNCTION))

        if count_none == 2:
            rotation = 0
            if first_missing == 0:
                rotation = 180
            elif first_missing == 2:
                rotation = 270
            elif first_missing == 4:
                rotation = 0
            elif first_missing == 6:
                rotation = 90
            streets_sprites.append(Street(intersection[0], intersection[1], type=SMALL_JUNCTION, angle=rotation))

        if count_none == 4:
            rotation = 0
            if first_missing == 0 and last_missing == 3:
                rotation = 270
            if first_missing == 0 and last_missing == 7:
                rotation = 180
            if first_missing == 2:
                rotation = 0
            if first_missing == 4:
                rotation = 90
            streets_sprites.append(Street(intersection[0], intersection[1], type=CORNER, angle=rotation))

        for i, (start, end) in enumerate([(7, 0), (1, 2), (3, 4), (5, 6), (7, 4), (1, 6), (3, 0), (5, 2)]):
            if intersection_node[start] is not None and intersection_node[end] is not None:
                intersection_node[start].add_neighbor(intersection_node[end], i + 1)
                intersection_connections.append((intersection_node[start].position, intersection_node[end].position))

        for start, end in [(7, 2), (1, 4), (3, 6), (5, 0)]:
            if intersection_node[start] is not None and intersection_node[end] is not None:
                intersection_node[start].add_neighbor(intersection_node[end], NO_TURN)
                no_turn_intersection_connections.append((intersection_node[start].position, intersection_node[end].position))

    return street_nodes, connection_sprites, streets_sprites, intersection_connections, no_turn_intersection_connections


create_streets([
    [[410, 105], [140, 105]],
    [[140, 105], [140, 135]],
    [[320, 45], [350, 45]],
    [[350, 135], [350, 45]],
    [[290, 105], [290, 225]]
])


def dijkstra(g, start, target):
    visited = set()
    cost = {start: 0}
    parent = {start: None}
    pq = PriorityQueue()

    pq.put((0, start))

    while pq:
        while not pq.empty():
            _, vertex = pq.get()
            if vertex not in visited: break
        else:
            break
        visited.add(vertex)
        if vertex == target:
            break
        for neighbor, distance in g[vertex]:
            if neighbor not in visited:
                old_cost = cost.get(neighbor, float('inf'))
                new_cost = cost[vertex] + distance
                if new_cost < old_cost:
                    pq.put((new_cost, neighbor))
                    cost[neighbor] = new_cost
                    parent[neighbor] = vertex

    return parent


def make_path(parent, goal):
    if goal not in parent:
        return None
    v = goal
    path = []
    while v is not None:
        path.append(v)
        v = parent[v]
    return path[::-1]
