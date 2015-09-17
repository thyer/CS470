#!/usr/bin/python -tt

import sys
import random
import time
import math

from bzrc import BZRC, Command


class PFAgent(object):
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.current_tank = self.bzrc.get_mytanks()[0]
        self.commands = []
        self.obstacles = self.bzrc.get_obstacles()
        self.angles_are_initialized = False
        self.has_flag = False
        for flag in self.bzrc.get_flags():
            if str(flag.color) in str(self.current_tank.callsign):
                self.flag_home = flag
            else:
                self.flag_goal = flag

        self.targetAngle = 0
        self.lastAngle = 0

    def tick(self, time_diff):
        self.commands = []
        x_force = 0
        y_force = 0
        # Chloe, do you know how to make these three lines less verbose? Seems like it should be a one-liner
        forces = self.calculate_obstacles_force(self.current_tank)
        x_force += forces[0]
        y_force += forces[1]
        # calculate x, y force from goal
        # calculate x, y force from tangential field
        # calculate x, y force from random field


    def init_angles(self, tank):
        self.lastAngle = tank.angle
        self.targetAngle = self.normalize_angle(0.5) # change this to reflect goal
        self.angles_are_initialized = True

    def calculate_goal_force(self, tank):
        if self.has_flag:
            goal = self.flag_home
        else:
            goal = self.flag_goal

        x_force = tank.x - goal.x
        y_force = tank.y - goal.y

        return [x_force, y_force]

    def calculate_obstacles_force(self, tank):
        d = 50  # maximum radius of influence
        x_force = 0
        y_force = 0
        for obstacle in self.obstacles:
            average_x = 0
            average_y = 0
            total_points = 0
            for point in obstacle:
                average_x += point[0]
                average_y += point[1]
                total_points += 1
            average_x /= total_points   # x coordinate of object center
            average_y /= total_points   # y coordinate of object center

            r = 0   # radius of circle
            for point in obstacle:
                temp = math.sqrt(point[0] ** 2 + point[1] ** 2)
                if temp > r:
                    r = temp

            d_x = tank.x - average_x
            d_y = tank.y - average_y
            tank_distance = math.sqrt((d_x) ** 2 + (d_y) ** 2)
            if tank_distance > d + r:
                continue

            # if we're within radius of influence
            x_force += d / d_x
            y_force += d / d_y

        return [x_force, y_force]

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

    agent = PFAgent(bzrc)

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
