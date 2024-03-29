
from bzrc import BZRC
import sys
import math
from PriorityQueue import PriorityQueue

class PathFinder(object):
    def __init__(self, bzrc, tank_index):
        self.bzrc = bzrc
        self.points = []
        self.edges = []
        self.visibility_graph = None

        self.frontier = []
        self.visited = []
        self.path = []

        self.search_snapshots = []
        self.create_visibility_graph(tank_index)

    def get_path(self):
        return self.get_a_star_path()

    ########################
    ### VISIBILITY GRAPH ###
    ########################

    def create_visibility_graph(self, tank_index):
        print "Generating Visibility Graph for Tank", tank_index

        tank = self.bzrc.get_mytanks()[tank_index]
        self.points = []

        # append tank position to points, this MUST be the first point in this list (we're relying on that for
        # our search algorithms below)
        self.points.append((tank.x, tank.y))

        # append goal flag position to points
        flags = self.bzrc.get_flags()
        for flag in flags:
            if tank.flag != '-' and flag.color in tank.callsign:        # if the tank has the flag, go home
                self.points.append((flag.x, flag.y))                    # TODO: this line only works if the other team hasn't already taken our flag and run with it. We should probably use our base instead...
                break
            elif flag.color not in tank.callsign:                       # if the tank has no flag, go for one
                self.points.append((flag.x, flag.y))
                break

        # append obstacle corners to points, and obstacle edges to our list of edges
        for obstacle in self.bzrc.get_obstacles():
            i = 0
            for point in obstacle:
                self.points.append(point)
                self.edges.append([point, obstacle[(i+1) % len(obstacle)]])
                i += 1

        # initialize the visibility graph to all -1's
        length = len(self.points)
        self.visibility_graph = [[-1 for _ in range(length)] for _ in range(length)]

        # figure out the visibility between each pair of points
        for col in range(length):
            for row in range(length):
                if self.visibility_graph[row][col] == -1:  # we haven't considered this pair of points yet
                    if self.is_visible(self.points[col], self.points[row]):
                        # "if you are visible to me, than I am visible to you" mentality
                        self.visibility_graph[row][col] = 1
                        self.visibility_graph[col][row] = 1
                    else:
                        # "if you are not visible to me, than I am not visible to you" mentality
                        self.visibility_graph[row][col] = 0
                        self.visibility_graph[col][row] = 0

        # remove any edges that are on the very edge of the map (and therefore couldn't be traversed by the tank)
        self.remove_visibility_on_world_edges()


    def update_visibility_graph(self, tank_index):
        tank = self.bzrc.get_mytanks()[tank_index]
        self.points[0] = (tank.x, tank.y)  # update the tank position

        # update goal flag position in points
        flags = self.bzrc.get_flags()
        for flag in flags:
            if tank.flag != '-' and flag.color in tank.callsign:        # if the tank has the flag, go home
                self.points[1] = (flag.x, flag.y)                    # TODO: this line only works if the other team hasn't already taken our flag and run with it. We should probably use our base instead...
                break
            elif tank.flag == '-' and flag.color not in tank.callsign:                       # if the tank has no flag, go for one
                self.points[1] = (flag.x, flag.y)
                break

        # update the first two rows and columns in our visibility graph (these are the only points that have changed)
        # initialize the visibility graph to all -1's
        length = len(self.points)

        # figure out the visibility between each pair of points
        for col in range(length):
            for row in range(length):
                if col > 1 and row > 1:
                    continue

                if self.is_visible(self.points[col], self.points[row]):
                    # "if you are visible to me, than I am visible to you" mentality
                    self.visibility_graph[row][col] = 1
                    self.visibility_graph[col][row] = 1
                else:
                    # "if you are not visible to me, than I am not visible to you" mentality
                    self.visibility_graph[row][col] = 0
                    self.visibility_graph[col][row] = 0

    def is_visible(self, point1, point2):
        # check if they are the same point...a point is not visible to itself
        if point1 == point2:
            return False

        # check if they share an edge
        p1_found = False
        for edge in self.edges:
            if point1 in edge:
                p1_found = True
                if point2 in edge:
                    return True

        # check if they are both in the same obstacle (but obviously don't share an edge because of the case above)
        if p1_found:
            for obstacle in self.bzrc.get_obstacles():
                if point1 in obstacle and point2 in obstacle:
                    return False

        # check if there are any intersecting edges between these two points
        temp_edge = [point1, point2]
        for edge in self.edges:
            if self.line_segments_intersect(temp_edge, edge):
                return False

        # No edges intersected, these two points are visible to each other
        return True

    # Determines if two line segments intersect by checking that the two ends of one segment are on different sides
    # of the other segment, AND vise-versa (both conditions must be true for the line segments to intersect).
    # See http://stackoverflow.com/questions/7069420/check-if-two-line-segments-are-colliding-only-check-if-they-are-intersecting-n
    # for further explanation & math.
    def line_segments_intersect(self, edge1, edge2):
        # if both points of edge1 are on the same side of edge2, or one of edge1's points is on edge2
        # then we already know the lines aren't crossing over each other.
        cp1 = self.cross_product(edge1[0], edge2)
        cp2 = self.cross_product(edge1[1], edge2)
        if (cp1 > 0 and cp2 > 0) or (cp1 < 0 and cp2 < 0) or cp1 == 0 or cp2 == 0:
            return False

        # if both points of edge2 are on the same side of edge1, or one of edge2's endpoints is on edge1
        # then we know the lines aren't crossing over each other
        cp1 = self.cross_product(edge2[0], edge1)
        cp2 = self.cross_product(edge2[1], edge1)
        if (cp1 > 0 and cp2 > 0) or (cp1 < 0 and cp2 < 0) or cp1 == 0 or cp2 == 0:
            return False

        return True

    # Returns the cross product between the given line segment and the vector from that line segment to the given point
    def cross_product(self, point, segment):
        seg_start = segment[0]
        seg_end = segment[1]
        x = 0
        y = 1

        return (seg_end[x]-seg_start[x]) * (point[y]-seg_end[y]) - (seg_end[y]-seg_start[y]) * (point[x]-seg_end[x])

    def remove_visibility_on_world_edges(self):
        length = len(self.points)

        for index1 in range(length):
            point1 = self.points[index1]

            # check left edge
            if point1[0] == -400:  # the x value is on the left edge of the map
                for index2 in range(length):
                    point2 = self.points[index2]
                    if self.visibility_graph[index1][index2] == 1 and point2[0] == -400:  # both of these points' x values are on the left edge of the map
                        self.visibility_graph[index1][index2] = 0  # make them invisible to each other
                        self.visibility_graph[index2][index1] = 0

            # check right edge
            elif point1[0] == 400:  # the x value is on the right edge of the map
                for index2 in range(length):
                    point2 = self.points[index2]
                    if self.visibility_graph[index1][index2] == 1 and point2[0] == 400:  # both of these points' x values are on the edge of the map
                        self.visibility_graph[index1][index2] = 0  # make them invisible to each other
                        self.visibility_graph[index2][index1] = 0

            # check top edge
            elif point1[1] == 400:  # the y value is on the top edge of the map
                for index2 in range(length):
                    point2 = self.points[index2]
                    if self.visibility_graph[index1][index2] == 1 and point2[1] == 400:  # both of these points' y values are on the top edge of the map
                        self.visibility_graph[index1][index2] = 0  # make them invisible to each other
                        self.visibility_graph[index2][index1] = 0

            # check bottom edge
            elif point1[1] == -400:  # the y value is on the bottom edge of the map
                for index2 in range(length):
                    point2 = self.points[index2]
                    if self.visibility_graph[index1][index2] == 1 and point2[1] == -400:  # both of these points' y values are on the bottom edge of the map
                        self.visibility_graph[index1][index2] = 0  # make them invisible to each other
                        self.visibility_graph[index2][index1] = 0


    def print_visibility_graph(self):
        print "Visibility Graph:"
        for row in self.visibility_graph:
            print row

    ##########################
    ### DEPTH FIRST SEARCH ###
    ##########################

    def get_depth_first_search_path(self):
        print "Running Depth First Search to Get Path"
        # clear everything and add the tank's start position to the frontier
        self.clear_history()
        self.frontier.append(self.points[0])

        if not self.r_dfs(self.frontier[0]):
            print >> sys.stderr, 'DFS failed to find the goal'

        return self.path

    def r_dfs(self, vertex):
        self.search_snapshots.append(Snapshot(list(self.visited), list(self.frontier)))
        self.frontier.remove(vertex)
        self.visited.append(vertex)

        # recursive base case, found the goal
        if self.is_goal(vertex):
            self.path.append(vertex)
            return True

        # find out which point we're dealing with
        try:
            index = self.points.index(vertex)
        except:
            print >> sys.stderr, 'Vertex not found in points'
            return False

        # prepare qualified new neighbors to be added to frontier
        row = self.visibility_graph[index]
        new_neighbors = []
        index = 0
        for item in row:
            neighbor = self.points[index]
            if item == 1 and neighbor not in self.visited:
                new_neighbors.append(neighbor)
            index += 1

        # recursive base case, no new neighbors
        if len(new_neighbors) == 0:
            return False

        # it's a beautiful day in the neighborhood
        for neighbor in new_neighbors:
            self.frontier.insert(0, neighbor)
            if self.r_dfs(neighbor):
                self.path.insert(0, vertex)
                return True

        # none of our children in this path returned true
        return False

    ############################
    ### BREADTH FIRST SEARCH ###
    ############################

    def get_breadth_first_search_path(self):
        print "Running Breadth First Search to Get Path"
         # clear everything and add the beginning node (with the tank's start position) to the frontier
        self.clear_history()
        self.frontier.append(BFSNode(self.points[0], None))

        self.breadth_first_search()
        return self.path

    def breadth_first_search(self):
        while self.frontier:
            if self.frontier[0].my_point in self.visited:
                # we've already visited this node, don't need to look at it again
                self.frontier.pop(0)
                continue

            self.search_snapshots.append(Snapshot(list(self.visited), list(self.frontier), uses_bfs_nodes=True))
            current_node = self.frontier.pop(0)
            vertex = current_node.my_point
            self.visited.append(vertex)

            # find out which (x,y) point we're dealing with
            try:
                index = self.points.index(vertex)
            except:
                print >> sys.stderr, 'Vertex not found in points'
                return

            # find the neighbors of this point
            row = self.visibility_graph[index]
            for i in range(0, len(row)):
                neighbor = self.points[i]
                if row[i] == 1 and neighbor not in self.visited:
                    if self.is_goal(neighbor):
                        # If this child is the goal node, we're done!
                        last_node = BFSNode(neighbor, current_node)
                        self.frontier.append(last_node)
                        self.search_snapshots.append(Snapshot(list(self.visited), list(self.frontier), uses_bfs_nodes=True))
                        self.reconstruct_path_from_last_node(last_node)
                        return
                    else:
                        # Add this child to the end of the queue
                        self.frontier.append(BFSNode(neighbor, current_node))

        # If we get to this point, then the frontier became empty before we found the goal
        print "BFS failed to find the goal"

    def reconstruct_path_from_last_node(self, last_node):
        self.path = []
        node = last_node
        while node:
            self.path.insert(0, node.my_point)
            node = node.parent

    ############################
    ###   A-STAR ALGORITHM   ###
    ############################
    def get_a_star_path(self):
        print "Running A* to Get Path"
        self.a_star_search()
        return self.path

    def a_star_search(self):
        self.clear_history()
        self.frontier = PriorityQueue()
        self.frontier.put(AStarNode(self.points[0], None, 0), 0)
        last_node = None

        # iterate until the frontier is empty
        while not self.frontier.empty():
            snapshot = Snapshot(list(self.visited), self.frontier.getNodes(), uses_a_star_nodes=True)
            self.search_snapshots.append(snapshot)
            current = self.frontier.get()
            if current.my_point in self.visited:
                #  Never mind, we didn't want that snapshot :)
                self.search_snapshots.remove(snapshot)
                continue
            self.visited.append(current.my_point)

            # end immediately if the goal is found
            if self.is_goal(current.my_point):
                last_node = current
                break

            # find out which point we're dealing with
            try:
                index = self.points.index(current.my_point)
            except:
                print >> sys.stderr, 'Vertex not found in points'
                return False

            # prepare qualified new neighbors to be added to frontier
            row = self.visibility_graph[index]
            index = 0
            for item in row:
                neighbor = self.points[index]
                if item == 1 and neighbor not in self.visited:
                    distance = current.cost
                    distance += self.distance(neighbor, current.my_point)   # distance so far
                    est_distance_remaining = distance + self.distance(neighbor, self.points[1])    # est. distance to go
                    self.frontier.put(AStarNode(neighbor, current, distance), est_distance_remaining)
                index += 1

        # unwind path back to start
        while not last_node == None:
            self.path.insert(0, last_node.my_point)
            last_node = last_node.parent


    ################################
    ### SEARCH ALGORITHM HELPERS ###
    ################################

    def clear_history(self):
        self.visited = []
        self.frontier = []
        self.path = []
        self.search_snapshots = []

    def is_goal(self, point):
        return point == self.points[1]  # the goal point is always the second one in our list of points

    def distance(self, point1, point2):
        return math.sqrt((point1[0]-point2[0])**2 + (point1[1] - point2[1]) ** 2)


class BFSNode(object):
    def __init__(self, my_point, parent_point):
        self.my_point = my_point
        self.parent = parent_point


class AStarNode(object):
    def __init__(self, my_point, parent_point, cost):
        self.my_point = my_point
        self.parent = parent_point
        self.cost = cost

class Snapshot(object):
    def __init__(self, visited, frontier, uses_bfs_nodes=False, uses_a_star_nodes=False):
        self.visited = visited

        # our frontier is made up of nodes or points. We only need the snapshot to contain
        # points, so pull the points out of the nodes if needed.
        if uses_bfs_nodes:
            self.frontier = []
            for node in frontier:
                self.frontier.append(node.my_point)
        elif uses_a_star_nodes:
            self.frontier = []
            for node in frontier:
                self.frontier.append(node.my_point)
        else:
            self.frontier = frontier
