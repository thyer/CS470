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
        self.G_FROB = 0.90
        self.R_FROB = 0.1

        self.path = []
        self.has_path = False
        self.has_flag = False

        self.path_finder = PathFinder(self.bzrc, self.tank_index)

    def tick(self, time_diff):
        self.commands = []
        tank = self.bzrc.get_mytanks()[self.tank_index]

        # if our tank is dead, invalidate its path and we're done
        if tank.status == "dead":
            self.has_path = False
            return

        # if the tank picks up the flag, recalculate path
        if not self.has_flag and not tank.flag =='-':
            self.has_path = False
            self.has_flag = True
            
        if not self.has_path:
            # get the path by choosing from DFS, BFS, A*, etc.
            print "updating visibility graph for tank", self.tank_index
            self.path_finder.update_visibility_graph(self.tank_index)
            print "calculating path for tank", self.tank_index
            self.path = self.path_finder.get_path()
            self.has_path = True

        if not len(self.path) == 0:
            dist_from_next = math.sqrt((tank.x - self.path[0][0]) ** 2 + (tank.y - self.path[0][1]) **2)
            next_point = self.path[0]
            if dist_from_next < 25:
                self.path.remove(self.path[0])
            self.traverse_path(next_point, tank)
        else:
            self.has_path = False
        return

    def traverse_path(self, next_point, tank):
        forces = []
        x_force = 0
        y_force = 0

        forces.append(self.calculate_goal_force(next_point, tank))
        forces.append(self.calculate_random_force(tank))

        for force in forces:
            x_force += force[0]
            y_force += force[1]

        self.move(x_force, y_force, tank)
        
    def calculate_goal_force(self, goal, tank):
        x_force = min(goal[0] - tank.x, 200)
        y_force = min(goal[1] - tank.y, 200)

        output = [x_force * self.G_FROB, y_force * self.G_FROB]
        return output

    def calculate_random_force(self, tank):
        return [random.randint(-10, 10) * self.R_FROB, random.randint(-10, 10) * self.R_FROB]

    def move(self, x_force, y_force, tank):
        magnitude = math.sqrt(x_force ** 2 + y_force ** 2)/20
        targetAngle = math.atan2(y_force, x_force)

        # randomly shoot
        should_shoot = False
        if random.random() < .05:
            should_shoot = True

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
