#!/usr/bin/python -tt

import sys
import random
import time
import math

from bzrc import BZRC, Command
from OccupancyGrid import OccupancyGrid
from GFViz import GFViz


class GridFilterAgent(object):
    def __init__(self, bzrc, occupancy_grid, tank_index):
        self.bzrc = bzrc
        self.occupancy_grid = occupancy_grid
        self.tank_index = tank_index

    def tick(self, time_diff):
        self.commands = []
        tank = self.bzrc.get_mytanks()[self.tank_index]
        size = self.occupancy_grid.get_dimensions() - 1
        if random.randint(0,10) > 3:
            self.occupancy_grid.observe(0,0, True)
        else:
            self.occupancy_grid.observe(0,0, False)
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
    world_size = int(bzrc.get_constants()['worldsize'])
    occupancy_grid = OccupancyGrid(world_size)
    viz = GFViz(occupancy_grid, world_size)
    agent = GridFilterAgent(bzrc, occupancy_grid, index)
    agents.append(agent)

    prev_time = time.time()

    # Run the agent
    try:
        while True: # TODO: While our occupancy grid isn't "good enough"
            time_diff = time.time() - prev_time
            prev_time = time.time()
            for agent in agents:
                agent.tick(time_diff)
            viz.update_grid(occupancy_grid.get_grid())

        # Our occupancy grid is "good enough", enter an eternal loop so the visualization will be visible
        viz.loop_eternally()

    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()
