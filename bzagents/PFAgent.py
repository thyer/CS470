#!/usr/bin/python -tt

import sys
import random
import time
import math

from bzrc import BZRC, Command


class DumbAgent(object):
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.current_tank = self.mytanks[0]
        self.commands = []
        self.obstacles = bzrc.get_obstacles
        self.angles_are_initialized = False

        self.targetAngle = 0
        self.lastAngle = 0

    def tick(self, time_diff):
        self.commands = []
		# calculate x, y force from obstacles
		# calculate x, y force from goal
		# calculate x, y force from tangential field
		# calculate x, y force from random field


    def init_angles(self, tank):
        self.lastAngle = tank.angle
        self.targetAngle = self.normalize_angle(0.5) # change this to reflect goal
        self.angles_are_initialized = True

    def calculate_angvel(self):
        target = self.two_pi_normalize(self.targetAngle)
        current = self.two_pi_normalize(self.current_tank.angle)
        last = self.two_pi_normalize(self.lastAngle)
        return (target - current) - (current - last)

    def normalize_angle(self, angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle

    def two_pi_normalize(self, angle):
        """Make any angle between 0 to 2pi."""
        angle += 2 * math.pi
        return angle % (2 * math.pi)

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

    agent = DumbAgent(bzrc)

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
