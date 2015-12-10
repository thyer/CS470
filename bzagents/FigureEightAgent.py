#!/usr/bin/python -tt

import sys
import random
import math

from bzrc import BZRC, Command


class FigureEightAgent(object):
    def __init__(self, bzrc, tank_index):
        self.bzrc = bzrc
        self.tank_index = tank_index
        self.angvel_increasing = False
        self.angvel = 0
        self.velocity = 0.8

    def tick(self):
        if self.angvel_increasing:
            self.angvel += 0.01
            if self.angvel > 5.5:
                self.angvel_increasing = False
        else:
            self.angvel -= 0.01
            if self.angvel < -5.5:
                self.angvel_increasing = True

        command = Command(self.tank_index, self.velocity, self.angvel, False)
        self.bzrc.do_commands([command])
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
        while True:
            for agent in agents:
                agent.tick()

    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()

if __name__ == '__main__':
    main()
