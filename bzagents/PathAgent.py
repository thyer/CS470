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
        self.O_FROB = 0.50
        self.G_FROB = 0.90

        self.path = []
        self.has_path = False
        self.has_flag = False

    def tick(self, time_diff):
        self.commands = []
        tank = self.bzrc.get_mytanks()[self.tank_index]
        
        # if the tank picks up the flag, recalculate path
        if not self.has_flag and not tank.flag =='-':
            self.has_path = False
            self.has_flag = True
            
        if not self.has_path:
            # get the path by choosing from DFS, BFS, A*, etc.
            print "initializing path"
            path_finder = PathFinder(self.bzrc, self.tank_index)
            print "calculating path"
            self.path = path_finder.get_path()
            print self.path
            self.has_path = True

        if not len(self.path) == 0:
            dist_from_next = math.sqrt((tank.x - self.path[0][0]) ** 2 + (tank.y - self.path[0][1]) **2)
            next_point = self.path[0]
            if dist_from_next < 15:
                self.path.remove(self.path[0])
            self.traverse_path(next_point, tank)
        else:
            self.has_path = False
        return

    def traverse_path(self, next_point, tank):
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
        
        output = [x_force * self.O_FROB, y_force * self.O_FROB]
        return output
        
    def get_obstacle_force(self, obstacle, tank):
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

        return [-1 * (mag * abs(mag)) * math.cos(angle)/50, -1 * (mag * abs(mag)) * math.sin(angle)/50]
        
    def calculate_goal_force(self, goal, tank):
        x_force = min(goal[0] - tank.x, 200)
        y_force = min(goal[1] - tank.y, 200)

        output = [x_force * self.G_FROB, y_force * self.G_FROB]
        return output
        
    def move(self, x_force, y_force, tank):
        magnitude = math.sqrt(x_force ** 2 + y_force ** 2)/20
        targetAngle = math.atan2(y_force, x_force)

        # randomly shoot
        should_shoot = False
        if random.random() < .05:
            should_shoot = True
            # randomly recalculate route
            self.has_path = False
            magnitude = 0
            targetAngle = tank.angle

        command = Command(self.tank_index, magnitude, self.calculate_angvel(tank, targetAngle), should_shoot)
        self.commands.append(command)

        if self.commands:
            self.bzrc.do_commands(self.commands)
            
    def calculate_angvel(self, tank, targetAngle):
        targetAngle = self.two_pi_normalize(targetAngle)
        current = self.two_pi_normalize(tank.angle)
        output = self.normalize_angle(targetAngle - current)
        return output

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
    agents = []
    index = 0
    for tank in bzrc.get_mytanks():
        agent = PathAgent(bzrc, index)
        agents.append(agent)
        index += 1

    prev_time = time.time()

    # Run the agent
    try:
        while True:
            time_diff = time.time() - prev_time
            prev_time = time.time()
            for agent in agents:
                agent.tick(time_diff)
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()
