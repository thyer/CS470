#!/usr/bin/python -tt

import sys
import random
import math

from bzrc import BZRC, Command
from OccupancyGrid import OccupancyGrid
from GFViz import GFViz


class StraightLineAgent(object):
    def __init__(self, bzrc, tank_index):
        self.bzrc = bzrc
        self.tank_index = tank_index
        self.commands = []

    def tick(self):
        self.commands = []
        command = Command(self.tank_index, 4, 0, False)
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
        agent = StraightLineAgent(bzrc, index)
        agents.append(agent)

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
