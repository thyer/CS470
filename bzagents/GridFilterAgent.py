#!/usr/bin/python -tt

import sys
import random
import math

from bzrc import BZRC, Command
from OccupancyGrid import OccupancyGrid
from GFViz import GFViz


class GridFilterAgent(object):
    def __init__(self, bzrc, occupancy_grid, tank_index):
        self.bzrc = bzrc
        self.occupancy_grid = occupancy_grid
        self.tank_index = tank_index
        self.next_point = None
        self.commands = []
        self.stagnation_clicker = 0
        self.stagnation_point = (0, 0)
        self.G_FROB = 0.9
        self.R_FROB = 0.05

    def tick(self):
        self.commands = []
        tank = self.bzrc.get_mytanks()[self.tank_index]
        self.do_movement(tank)
        self.do_observe()
        return

    def do_movement(self, tank):
        if self.next_point is None: # we need to get a new traversal point
            self.next_point = self.occupancy_grid.get_target_point(tank.x, tank.y)
        elif self.occupancy_grid.get_distance(self.next_point, (tank.x, tank.y)) < 5: # we've hit our target
            self.occupancy_grid.post_process_point(self.next_point)
            self.next_point = None
            self.move(0, 0, tank)  # should get the tank to temporarily halt
        elif self.next_point is not None:   # we've got a point, but haven't hit it yet
            self.traverse_path(self.next_point, tank)

            # check for stagnation
            if (tank.x, tank.y) == self.stagnation_point:
                self.stagnation_clicker += 1
            else:
                self.stagnation_point = (tank.x, tank.y)
                self.stagnation_clicker = 0

            # limit stagnation to 20 ticks
            if self.stagnation_clicker >= 20:
                self.occupancy_grid.post_process_point(self.next_point)
                self.next_point = None
                self.move(0, 0, tank)
                self.stagnation_clicker = 0
    
    def do_observe(self):
        pos, ping_grid = self.bzrc.get_occgrid(self.tank_index)
        print str(pos)
        print "Grid length: " + str(len(ping_grid)) + " by " + str(len(ping_grid[0]))
        for x in range(len(ping_grid)):
            output = ""
            for y in range(len(ping_grid[x])):
                output += str(ping_grid[x][y])
            print output
        if random.randint(0,10) > 3:
            # TODO: converting to grid coordinates is off by one because the grid is zero-based. Try to put 400 instead of 300 and eventually you'll get an index out of bounds error in the occupancy grid
            self.occupancy_grid.observe(random.randint(-300, 0), random.randint(-300, 0), True)
        else:
            self.occupancy_grid.observe(random.randint(0, 300), random.randint(0, 300), False)
    
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
        
        weighting = min(math.sqrt(x_force ** 2 + y_force ** 2)/40, 1.0)
        output = [weighting * x_force * self.G_FROB, weighting * y_force * self.G_FROB]
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

    # Set up the occupancy grid and visualization
    world_size = int(bzrc.get_constants()['worldsize'])
    occupancy_grid = OccupancyGrid(world_size, .97, .1, 100)
    viz = GFViz(occupancy_grid, world_size)

    # Create our army
    agents = []
    agent = GridFilterAgent(bzrc, occupancy_grid, 0)
    agents.append(agent)

    # Run the agent
    try:
        while True:  # TODO: While our occupancy grid isn't "good enough"
            for agent in agents:
                agent.tick()
            viz.update_grid(occupancy_grid.get_grid())

        # Our occupancy grid is "good enough", enter an eternal loop so the visualization will be visible
        viz.loop_eternally()

    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()

if __name__ == '__main__':
    main()
