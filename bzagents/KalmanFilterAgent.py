#!/usr/bin/python -tt

import sys
import random
import math
import numpy as NP

from bzrc import BZRC, Command


class KalmanFilterAgent(object):
    def __init__(self, bzrc, tank_index):
        print "Constructing KalmanFilterAgent"
        self.bzrc = bzrc
        self.tank_index = tank_index
        self.commands = []
        self.ticks = 0
        self.mu_t = NP.matrix('0.0 0 0 0 0 0')
        self.sigma_x = NP.matrix('0.1 0 0 0 0 0;' + \
        '0 0.1 0 0 0 0; 0 0 10 0 0 0; 0 0 0 0.1 0 0;' + \
        '0 0 0 0 0.1 0; 0 0 0 0 0 10')
        self.sigma_z = NP.matrix('25.0 0; 0 25')
        self.sigma_t = NP.matrix('100.0 0 0 0 0 0;' + \
        '0 0.1 0 0 0 0; 0 0 0.1 0 0 0; 0 0 0 100 0 0;' + \
        '0 0 0 0 0.1 0; 0 0 0 0 0 0.1')
        self.H = NP.matrix('1.0 0 0 0 0 0; 0 0 0 1 0 0')
        self.F = NP.matrix('0.0 0.0 0.0 0 0 0; 0 0 0 0 0 0; 0 0 0 0 0 0;' + \
        '0 0 0 0 0 0; 0 0 0 0 0 0; 0 0 0 0 0 0')
        c = .01
        self.F[2, 1] = c
        self.F[5, 4] = c

    def tick(self):
        self.ticks += 1
        self.commands = []
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
        agent = KalmanFilterAgent(bzrc, index)
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
