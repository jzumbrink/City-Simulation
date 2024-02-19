from street_network import pos_to_str, str_to_pos, StreetNode
from queue import PriorityQueue


# only give the start node and then a criteria for a node that is a good target  (lambda function)
def dijkstra(start_node: StreetNode, target_criteria):
    visited = set()
    cost = {pos_to_str(start_node.position): 0}
    parent = {pos_to_str(start_node.position): None}
    pq = PriorityQueue()

    pq.put((0, start_node))

    target_vertex_str = None

    while pq:
        while not pq.empty():
            _, vertex = pq.get()
            vertex_str = pos_to_str(vertex.position)
            if vertex_str not in visited:
                break
        else:
            break

        visited.add(vertex_str)
        if target_criteria(vertex):
            target_vertex_str = pos_to_str(vertex.position)
            break

        for neighbor, _, distance in vertex.neighbors:
            neighbor_str = pos_to_str(neighbor.position)
            if neighbor_str not in visited:
                old_cost = cost.get(neighbor_str, float('inf'))
                new_cost = cost[vertex_str] + distance
                if new_cost < old_cost:
                    pq.put((new_cost, neighbor))
                    cost[neighbor_str] = new_cost
                    parent[neighbor_str] = vertex_str

    return parent, target_vertex_str


def make_path(parent, target_vertex_str):
    if target_vertex_str not in parent:
        return None
    v = target_vertex_str
    path = []
    while v is not None:
        path.append(v)
        v = parent[v]
    return path[::-1]


def shortest_path(start_node: StreetNode, target_criteria):
    parents, target_vertex_str = dijkstra(start_node, target_criteria)
    return make_path(parents, target_vertex_str)