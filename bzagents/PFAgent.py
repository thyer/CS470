#!/usr/bin/python -tt

import sys
import random
import time
import math

from bzrc import BZRC, Command


class PFAgent(object):
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.commands = []
        self.obstacles = self.bzrc.get_obstacles()
        self.has_flag = False

        self.ourCallsign = self.bzrc.get_mytanks()[0].callsign
        self.targetAngle = 0
        self.lastAngle = 0

        # frobbing constants
        self.O_FROB = 1.5
        self.G_FROB = 0.1
        self.T_FROB = 1
        self.R_FROB = 0.3

        bases = self.bzrc.get_bases()
        for base in bases:
            if str(base.color) in str(self.ourCallsign):
                # this is our base
                center_x = (base.corner1_x + base.corner3_x) / 2
                center_y = (base.corner1_y + base.corner3_y) / 2
                self.flag_home = HomeBase(center_x, center_y)

    def tick(self):
        self.commands = []

        flags = self.bzrc.get_flags()
        self.has_flag = False
        for flag in flags:
            if not str(flag.color) in str(self.ourCallsign):
                self.flag_goal = flag
            if str(flag.poss_color) in str(self.ourCallsign):
                self.has_flag = True

        mytanks = self.bzrc.get_mytanks()
        for tank in mytanks:
            x_force, y_force = self.get_forces_on_tank(tank)
            magnitude = math.sqrt(x_force ** 2 + y_force ** 2)
            self.targetAngle = math.atan2(y_force, x_force)

            # randomly shoot
            should_shoot = False
            if random.random() < .01:
                should_shoot = True

            command = Command(tank.index, magnitude, self.calculate_angvel(tank), should_shoot)
            self.commands.append(command)

        if self.commands:
            self.bzrc.do_commands(self.commands)

    def get_forces_on_tank(self, tank):
        forces = []
        x_force = 0
        y_force = 0

        forces.append(self.calculate_obstacles_force(tank))
        forces.append(self.calculate_goal_force(tank))
        forces.append(self.calculate_tangential_force(tank))
        forces.append(self.calculate_random_force(tank))

        for force in forces:
            x_force += force[0]
            y_force += force[1]

        return x_force, y_force

    def calculate_goal_force(self, tank):
        if self.has_flag:
            goal = self.flag_home
        else:
            goal = self.flag_goal

        x_force = min(goal.x - tank.x, 200)
        y_force = min(goal.y - tank.y, 200)


        return [x_force * self.G_FROB, y_force * self.G_FROB]

    def calculate_obstacles_force(self, tank):
        x_force = 0
        y_force = 0
        for obstacle in self.obstacles:
            forces = self.get_obstacle_force(obstacle, tank)
            x_force += forces[0]
            y_force += forces[1]


        return [x_force * self.O_FROB, y_force * self.O_FROB]

    def get_obstacle_force(self, obstacle, tank, use_exponential=True):
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

    def calculate_tangential_force(self, tank):
        x_force = 0
        y_force = 0
        for obstacle in self.obstacles:
            forces = self.get_obstacle_force(obstacle, tank, False)
            angle = math.atan2(forces[1], forces[0])
            magnitude = math.sqrt(forces[0] ** 2 + forces[1] ** 2)
            angle = self.normalize_angle(angle + 1.57)  # adds 90 degrees, normalizes angle
            x_force += magnitude * math.cos(angle)
            y_force += magnitude * math.sin(angle)
        return [x_force * self.T_FROB, y_force * self.T_FROB]

    def calculate_random_force(self, tank):
        return [random.randint(-10, 10) * self.R_FROB, random.randint(-10, 10) * self.R_FROB]

    def calculate_angvel(self, tank):
        target = self.two_pi_normalize(self.targetAngle)
        current = self.two_pi_normalize(tank.angle)
        return self.normalize_angle(target - current)

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

class HomeBase(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

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
            agent.tick()
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()
