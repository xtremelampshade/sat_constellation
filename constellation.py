import math
from numpy import pi, cos, sin, arccos, arange

# Parameters
radius_of_earth = 4000 # miles
altitude_of_satellites = 300 # miles
valid_satellite_distance = 100000000 # max distance (in miles) that satellites can communicate via VLOS

# Boilerplate Functions
def dist(x,y):
    distance = math.sqrt(
        ((x[0] - y[0]) * (x[0] - y[0])) +
        ((x[1] - y[1]) * (x[1] - y[1])) +
        ((x[2] - y[2]) * (x[2] - y[2]))
    )
    return distance

# This function receives the first and last point to compute the connecting between and check if the earth interferes with
# the line of sight. It does this by computing the midpoint of the segment connecting them and then calculating the
# distance between that point and the center of the sphere, which is also the origin. If it is less than the radius of
# the earth, then it decides the line of sight would be blocked by the earth and therefore returns false. If it is
# otherwise determined to not be blocked, it returns true.
def valid_distance(first_id,first,last_id,last):
    line_of_site_barrier = radius_of_earth / (radius_of_earth + altitude_of_satellites)

    x0 = first[0]
    x1 = last[0]
    y0 = first[1]
    y1 = last[1]
    z0 = first[2]
    z1 = last[2]

    dX = x1 - x0
    dY = y1 - y0
    dZ = z1 - z0

    xM = x0 + dX/2
    yM = y0 + dY/2
    zM = z0 + dZ/2

    if math.sqrt(
        xM * xM +
        yM * yM +
        zM * zM
    ) > line_of_site_barrier:
        return [True, first_id, last_id, dist(first,last)]
    else:
        return [False, first_id, last_id, 10000000000000]

#Code for Constellation
class fibonacciConstellation():
    def __init__(self, vertices, jammed, blocked):
        self.num_verts = vertices
        self.jammed_sats = jammed
        self.blocked_links = blocked
        self.destroyed = []
        self.sphere = self.fibonacci_sphere()
        self.graph = self.get_graph_from_sats(self.get_vis_sat_sets())

    # This attribute simulated "reseeding" of the constellation. If the constellation contains any destroyed satellites,
    # it prioritizes replacing these satellites first. It then adds new satellites to the constellation by updating the
    # num_verts attribute. Remember that the graph must be re-generated after reseeding.
    def reseed(self, sats):
        while ((len(self.destroyed) > 0) or (sats > 0)):
            del self.destroyed[0]
            sats -= 1
        self.num_verts = self.num_verts + sats

    def strike_sats(self, destroyed):
        if type(destroyed) == int:
            self.destroyed.append(str(destroyed))
        elif type(destroyed) == list:
            for sat in destroyed:
                self.destroyed.append(str(sat))

    def fibonacci_sphere(self):
        points = []
        phi = math.pi * (math.sqrt(5.) - 1.)  # golden angle in radians

        for i in range(self.num_verts):
            y = (1 - (i / float(self.num_verts - 1)) * 2)  # y goes from 1 to -1
            radius = math.sqrt(1 - y * y)  # radius at y
            theta = phi * i  # golden angle increment
            x = math.cos(theta) * radius
            z = math.sin(theta) * radius
            points.append((x, y, z))
        return points

    def get_vis_sat_sets(self, ):
        sat_set_output = {}  # []
        for sat_id in range(self.num_verts):
            if sat_id in self.jammed_sats:
                continue
            if sat_id in self.destroyed:
                continue
            closest_sat = -1
            closest_sat_dist = 1000000000000000
            visible_set = []
            for count in range(self.num_verts):
                if count == sat_id:
                    continue
                if (
                    ([sat_id, count] in self.blocked_links) or
                    ([count, sat_id] in self.blocked_links)
                ):
                    continue
                valdist = valid_distance(sat_id, self.sphere[sat_id], count, self.sphere[count])
                if valdist[0]:
                    if valdist[3] < valid_satellite_distance:
                        visible_set.append(valdist)
                        if valdist[3] < closest_sat_dist:
                            closest_sat = count
            sat_set_output[str(sat_id)] = [visible_set, closest_sat]
        return sat_set_output

    def get_graph_from_sats(self, visible_satellite_sets):
        output_sat_graph = {}
        for sat in range(self.num_verts):
            satellite_graph = {}
            if str(sat) in visible_satellite_sets.keys():  ###
                visible_satellite_set = visible_satellite_sets[str(sat)][0]
                for vis_sat in visible_satellite_set:
                    satellite_graph[str(vis_sat[2])] = vis_sat[3]
                output_sat_graph[str(sat)] = satellite_graph
        return output_sat_graph


    def dist_between_2_nodes(self, start, end):
        unvisited = {node: None for node in self.graph}  # using None as +inf
        visited = {}
        predecessor = {}  # To reconstruct the path
        current = str(start)
        currentDistance = 0
        unvisited[current] = currentDistance

        while True:
            for neighbour, distance in self.graph[current].items():
                if neighbour not in unvisited:
                    continue
                if neighbour in self.destroyed:
                    continue
                newDistance = currentDistance + distance
                if unvisited[neighbour] is None or unvisited[neighbour] > newDistance:
                    unvisited[neighbour] = newDistance
                    predecessor[neighbour] = current  # Record the path
            visited[current] = currentDistance
            del unvisited[current]
            if not unvisited:
                break
            candidates = [node for node in unvisited.items() if node[1]]
            if not candidates:
                break  # No more reachable nodes
            current, currentDistance = sorted(candidates, key=lambda x: x[1])[0]
        # Reconstruct the path
        path = []
        node = str(end)
        if node not in predecessor and node != str(start):
            return None, []  # No path found
        while node != str(start):
            path.insert(0, node)
            node = predecessor[node]
        path.insert(0, str(start))
        return [visited[str(end)] * (radius_of_earth + altitude_of_satellites), path]