#!/usr/bin/python -tt

import sys
import random
import time
import math

from bzrc import BZRC, Command
from PathFinder import PathFinder


class PathAgent(object):
    def __init__(self, bzrc, tank_index):
        self.bzrc = bzrc
        self.obstacles = self.bzrc.get_obstacles()
        self.tank_index = tank_index
        self.O_FROB = 0.05
        self.G_FROB = 0.50

        self.path = []
        self.has_path = False

    def tick(self, time_diff):
        self.commands = []
        if not self.has_path:
            # get the path by choosing from DFS, BFS, A*, etc.
            path_finder = PathFinder(self.bzrc, self.tank_index)
            self.path = path_finder.get_depth_first_search_path()
            print self.path
            self.has_path = True

        while not len(self.path) == 0:
            tank = self.bzrc.get_mytanks()[self.tank_index]
            if (tank.x, tank.y) == self.path[0]:
                self.path.remove(self.path[0])
            next_point = self.path[0]
            self.traverse_path(next_point, tank)
        return

    def traverse_path(self, next_point, tank):
        print "tank is at (" + str(tank.x) + ", " + str(tank.y) + ") and moving toward " + str(next_point)
        forces = []
        x_force = 0
        y_force = 0

        forces.append(self.calculate_obstacles_force(tank))
        forces.append(self.calculate_goal_force(next_point, tank))

        for force in forces:
            x_force += force[0]
            y_force += force[1]

        self.move(x_force, y_force, tank)
        
    def calculate_obstacles_force(self, tank):
        x_force = 0
        y_force = 0
        for obstacle in self.obstacles:
            forces = self.get_obstacle_force(obstacle, tank)
            x_force += forces[0]
            y_force += forces[1]

        return [x_force * self.O_FROB, y_force * self.O_FROB]
        
    def get_obstacle_force(self, obstacle, tank, use_exponential=False):
        d = 0  # maximum radius of influence
        r = 0   # radius of circle
        average_x = 0
        average_y = 0
        total_points = 0

        for point in obstacle:
            average_x += point[0]
            average_y += point[1]
            total_points += 1
        average_x /= total_points   # x coordinate of object center
        average_y /= total_points   # y coordinate of object center


        for point in obstacle:
            temp = math.sqrt((average_x - point[0]) ** 2 + (average_y - point[1]) ** 2)
            if temp > r:
                r = temp
                d = r + 20

        d_x = average_x - tank.x
        d_y = average_y - tank.y
        tank_distance = math.sqrt((d_x) ** 2 + (d_y) ** 2)
        angle = math.atan2(d_y, d_x)
        if tank_distance > d:
            return [0, 0]

        # if we're within radius of influence
        mag = d - tank_distance

        if not use_exponential:
            return [mag * math.cos(angle), mag * math.sin(angle)]

        return [-1 * (mag * abs(mag)) * math.cos(angle)/50, -1 * (mag * abs(mag)) * math.sin(angle)/50]
        
    def calculate_goal_force(self, goal, tank):
        return [0, 0]
        
    def move(self, x_force, y_force, tank):
        magnitude = math.sqrt(x_force ** 2 + y_force ** 2)
        targetAngle = math.atan2(y_force, x_force)

        # randomly shoot
        should_shoot = False
        if random.random() < .01:
            should_shoot = True

        command = Command(self.tank_index, magnitude, self.calculate_angvel(tank, targetAngle), should_shoot)
        self.commands.append(command)

        if self.commands:
            self.bzrc.do_commands(self.commands)
            
    def calculate_angvel(self, tank, targetAngle):
        targetAngle = self.two_pi_normalize(targetAngle)
        current = self.two_pi_normalize(tank.angle)
        return self.normalize_angle(targetAngle - current)

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


#####################
### MAIN FUNCTION ###
#####################


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
