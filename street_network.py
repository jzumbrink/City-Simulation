from queue import PriorityQueue
from utils import SimulatedSprite
import pygame
from collections import deque
from colors import *

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

class StreetNode():

    def __init__(self, x, y):

        self.neighbors = []
        self.position = [x, y]

    def add_neighbor(self, street_node):
        self.neighbors.append(street_node)


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
    #normalize streets
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
        for street2 in streets[i+1:]:
            # find intersection if possible
            if is_street_vertical(street1) != is_street_vertical(street2):
                comp_street1, comp_street2 = street1, street2
                if is_street_vertical(street2):
                    comp_street1, comp_street2 = street2, street1
                    # street1 is always the vertical one
                if comp_street2[0][0] <= comp_street1[0][0] <= comp_street2[1][0] and comp_street1[0][1] <= comp_street2[0][1] <= comp_street1[1][1]:
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
            if (is_street_vertical(street) and street[0][0] == intersection[0] and street[0][1] < intersection[1] < street[1][1]
                    or street[0][1] == intersection[1] and street[0][0] < intersection[0] < street[1][0]):
                # intersection splits street
                old_streets.append([street[0], intersection])
                old_streets.append([intersection, street[1]])
                break
        else:
            streets.append(street)

    connection_sprites = []

    # create street nodes
    street_nodes = {}
    for street in streets:
        street_node1, street_node2, street_node3, street_node4 = None, None, None, None
        if is_street_vertical(street):
            street_node1 = StreetNode(street[0][0] + 3, street[0][1] + 29)
            street_node2 = StreetNode(street[1][0] + 3, street[1][1])

            street_node3 = StreetNode(street[0][0] + 19, street[0][1] + 18)
            street_node4 = StreetNode(street[1][0] + 19, street[1][1])

            street_node1.add_neighbor(street_node2)
            street_node4.add_neighbor(street_node3)

            connection_sprites.append(
                StreetNodeConnectionSprite(street_node1.position[0], street_node1.position[1], street_node2.position[0],
                                           street_node2.position[1]))
            connection_sprites.append(
                StreetNodeConnectionSprite(street_node3.position[0], street_node3.position[1], street_node4.position[0],
                                           street_node4.position[1]))
        else:
            street_node1 = StreetNode(street[0][0] + 29, street[0][1] + 19)
            street_node2 = StreetNode(street[1][0], street[1][1] + 19)

            street_node3 = StreetNode(street[0][0] + 29, street[0][1] + 3)
            street_node4 = StreetNode(street[1][0], street[1][1] + 3)

            street_node1.add_neighbor(street_node2)
            street_node4.add_neighbor(street_node3)
            connection_sprites.append(
                StreetNodeConnectionSprite(street_node1.position[0], street_node1.position[1], street_node2.position[0],
                                           street_node2.position[1]))
            connection_sprites.append(
                StreetNodeConnectionSprite(street_node3.position[0], street_node3.position[1], street_node4.position[0],
                                           street_node4.position[1]))
        for street_node in [street_node1, street_node2, street_node3, street_node4]:
            street_nodes[pos_to_str(street_node.position)] = street_node

    return street_nodes, connection_sprites


create_streets([
    [[380, 105], [140, 105]],
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