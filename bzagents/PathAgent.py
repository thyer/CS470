#!/usr/bin/python -tt

import sys
import time

from bzrc import BZRC, Command


class PathAgent(object):
    def __init__(self, bzrc, tank_index):
        self.bzrc = bzrc
        self.points = []
        self.edges = []
        self.tank_index = tank_index

        self.visibility_graph = None
        self.frontier = []
        self.visited = []
        self.path = []
        self.has_path = False
        print "running constructor"

    def tick(self, time_diff):
        # TODO: Make tick actually do something :)
        if not self.has_path:
            self.depth_first_search()
            print self.path
            self.has_path = True
        return

    def create_visibility_graph(self):
        print "creating visibility graph"
        tank = self.bzrc.get_mytanks()[self.tank_index]
        self.points = []

        # append tank position to points
        self.points.append((tank.x, tank.y))
        print "added self position"
        
        # append goal flag position to points
        flags = self.bzrc.get_flags()
        for flag in flags:
            if tank.flag and flag.color in tank.callsign:               # if the tank has the flag, go home
                self.points.append((flag.x, flag.y))
                break
            elif not tank.flag and flag.color not in tank.callsign:     # if the tank has no flag, go for one
                self.points.append((flag.x, flag.y))
                break
        print "added flag position" 
        
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
        print "visibility graph initialized to all -1"
        
        # figure out the visibility between each pair of points
        for col in range(length):
            print "Filling in visibility graph column: " + str(col)
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
        print "done doing visibility graph"

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

    def print_visibility_graph(self):
        for row in self.visibility_graph:
            print row

    def begin_search(self):
        # clear everything
        self.visited = []
        self.frontier = []
        self.path = []

        # some basic sanity checks, make sure our start is in the visibility graph
        self.create_visibility_graph()
        tank = self.bzrc.get_mytanks()[self.tank_index]
        start = (tank.x, tank.y)
        if start not in self.points:
            print >>sys.stderr, 'attempted search when tank was not part of graph'

        # initialize search at robot's current location
        self.frontier.append(start)

    def depth_first_search(self):
        print "Entering DFS"
        self.begin_search()
        print "Search initialized"
        if not self.r_dfs(self.frontier[0]):
            print >>sys.stderr, 'DFS failed to find goal'

    def r_dfs(self, vertex):
        print "Entering R_DFS"
        self.frontier.remove(vertex)
        self.visited.append(vertex)

        # recursive base case, found the goal
        if vertex == self.points[1]:
            self.path.append(vertex)
            print "R_DFS found the goal"
            return True

        # find out which point we're dealing with
        index = 0
        while not vertex == self.points[index] and index < len(self.points):
            index += 1
        if index == len(self.points):
            print >>sys.stderr, 'Vertex not found in points'

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
                print "R_DFS child returned true"
                return True
                
        # none of our children in this path returned true
        return False


def main():
    # Process CLI arguments.
    print "entering main function"
    try:
        execname, host, port = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    # Connect.
    # bzrc = BZRC(host, int(port), debug=True)
    bzrc = BZRC(host, int(port))
    print "preparing agent"
    agent = PathAgent(bzrc, 0)
    print "running agent"
    prev_time = time.time()

    # Run the agent
    try:
        while True:
            time_diff = time.time() - prev_time
            prev_time = time.time()
            agent.tick(time_diff)
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()