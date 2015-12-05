#!/usr/bin/python -tt

import sys
import random
import math

from bzrc import BZRC, Command


class FigureEightAgent(object):
    def __init__(self, bzrc, tank_index):
        self.bzrc = bzrc
        self.tank_index = tank_index
        self.commands = []
        self.angvel_increasing = False
        self.angvel = 0
        self.velocity = 1.00
        self.ticks = 0

    def tick(self):
        self.ticks += 1
        self.commands = []
        print "Ticks: " + str(self.ticks)
        print "Angvel: " + str(self.angvel) + ", Velocity: " + str(self.velocity)
        if self.angvel_increasing:
            self.angvel += 0.04
            if self.angvel > .90:
                self.angvel_increasing = False
        else:
            self.angvel -= 0.04
            if self.angvel < -.90:
                self.angvel_increasing = True
        if self.ticks % 10 == 0:
            print "tick!"
            self.velocity += random.randint(-50,50)/1000
        command = Command(self.tank_index, self.velocity, self.angvel, False)
        self.commands.append(command)
        
        if self.commands:
            self.bzrc.do_commands(self.commands)
        return


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

    # Create our army
    agents = []
    index = 0
    for tank in range(len(bzrc.get_mytanks())):
        agent = FigureEightAgent(bzrc, index)
        agents.append(agent)
        index += 1

    # Run the agent
    try:
        counter = 0
        while True:  # TODO: While our occupancy grid isn't "good enough"
            for agent in agents:
                agent.tick()
            counter += 1

    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()

if __name__ == '__main__':
    main()
