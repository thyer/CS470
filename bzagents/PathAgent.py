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
                
        # append obstacle points
        for obstacle in self.bzrc.get_obstacles():
            for point in obstacle:
                self.points.append(point)

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

        print self.visibilityGraph

    def is_visible(self, point1, point2):
        return True

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
