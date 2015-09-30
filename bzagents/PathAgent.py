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
        self.create_visibility_graph()
        self.print_visibility_graph()  # TODO: eventually we'll want to remove this

    def tick(self, time_diff):
        # TODO: Make tick actually do something :)
        return

    def create_visibility_graph(self):
        tank = self.bzrc.get_mytanks()[self.tank_index]

        # append tank position to points
        self.points.append((tank.x, tank.y))
        
        # append goal flag position to points
        flags = self.bzrc.get_flags()
        for flag in flags:
            if not flag.color in tank.callsign:
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


def main():
    # Process CLI arguments.
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

    agent = PathAgent(bzrc, 0)

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
