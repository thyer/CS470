#!/usr/bin/python -tt

import sys
import random
import time
import math

from bzrc import BZRC, Command


class PathAgent(object):
    def __init__(self, bzrc, index):
        self.bzrc = bzrc
        self.commands = []
        self.points = []
        self.edges = []
        self.visibilityGraph = None
        self.index = index
        self.counter = 0
        

    def tick(self, time_diff):
        if self.counter == 0:
            self.create_visibility_graph()
        self.counter += 1

    def create_visibility_graph(self):
        tank = self.bzrc.get_mytanks()[self.index]
        # append tank position to points
        self.points.append((tank.x, tank.y))
        
        # append goal flag position to points
        flags = self.bzrc.get_flags()
        for flag in flags:
            if not flag.color in tank.callsign:
                self.points.append((flag.x, flag.y))
                break
                
        # append obstacle points, edges
        for obstacle in self.bzrc.get_obstacles():
            i = 0
            for point in obstacle:
                self.points.append(point)
                self.edges.append([point, obstacle[(i+1)%len(obstacle)]])
                i += 1

        length = len(self.points)
        self.visibilityGraph = [[-1 for x in range(length)] for x in range(length)]

        for col in range(length):
            for row in range(length):
                if self.visibilityGraph[row][col] == -1:
                    if row == col:
                        self.visibilityGraph[row][col] = 0
                    elif self.is_visible(self.points[col], self.points[row]):
                        self.visibilityGraph[row][col] = 1
                    else:
                        self.visibilityGraph[row][col] = 0

        self.print_visibility_graph();

    def is_visible(self, point1, point2):
        # check if they share an edge
        for edge in self.edges:
            if point1 in edge:
                if point2 in edge:
                    return True
        
        # if there are no intersecting line segments
        for edge in self.edges:
            if line_segments_intersect([point1, point2], edge):
                return False
        
        # no edges intersected
        return True
        
    def line_segments_intersect(edge1, edge2):
        x = 0
        y = 1
        
        # crossproduct 1, 2: check points in edge 1 are on opposite sides of edge 2
        e = edge2[0]
        f = edge2[1]
        p1 = edge1[0]
        p2 = edge1[1]
        
        cp1 = (f[x]-e[x])(p1[y]-f[y]) - (f[y] - e[y])(p1[x] - f[x])
        cp2 = (f[x]-e[x])(p2[y]-f[y]) - (f[y] - e[y])(p2[x] - f[x])
        if (cp1 > 0 and cp2 > 0) or (cp1 < 0 and cp2 < 0):
            return False
        
        # crossproduct 3, 4: check points in edge 2 are on opposite sides of edge 1
        e = edge1[0]
        f = edge1[1]
        p1 = edge2[0]
        p2 = edge2[1]
        
        cp1 = (f[x]-e[x])(p1[y]-f[y]) - (f[y] - e[y])(p1[x] - f[x])
        cp2 = (f[x]-e[x])(p2[y]-f[y]) - (f[y] - e[y])(p2[x] - f[x])
        if (cp1 > 0 and cp2 > 0) or (cp1 < 0 and cp2 < 0):
            return False        
        return True
        
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
