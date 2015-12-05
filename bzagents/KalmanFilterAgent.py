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
        
        # constant matrices
        self.sigma_x = NP.matrix('0.1 0 0 0 0 0;' + \
        '0 0.1 0 0 0 0; 0 0 10 0 0 0; 0 0 0 0.1 0 0;' + \
        '0 0 0 0 0.1 0; 0 0 0 0 0 10')
        self.sigma_z = NP.matrix('25.0 0; 0 25')
        self.H = NP.matrix('1.0 0 0 0 0 0; 0 0 0 1 0 0')
        
        # instantiated matrices
        self.mu_t = NP.matrix('0.0; 0; 0; 0; 0; 0')
        self.sigma_t = NP.matrix('100.0 0 0 0 0 0;' + \
        '0 0.1 0 0 0 0; 0 0 0.1 0 0 0; 0 0 0 100 0 0;' + \
        '0 0 0 0 0.1 0; 0 0 0 0 0 0.1')
        
        # variable matrix
        self.F = NP.matrix('1.0 0.0 0.0 0 0 0; 0 1 0 0 0 0; 0 0 1 0 0 0;' + \
        '0 0 0 1 0 0; 0 0 0 0 1 0; 0 0 0 0 0 1')
        c = .01
        self.F[2, 1] = -c
        self.F[5, 4] = -c
        
        # other tracking variables
        self.delta_time = 0

    def tick(self):
        self.commands = []
        # print "tick"
        
        # update our F matrix depending on how much time has passed
        d_time = 1 # TODO: figure out how to determine the time passed
        if d_time != self.delta_time:
            self.update_f_matrix(d_time)
            selfdelta_time = d_time
            
        # get our updated location estimate and standard deviation
        enemy_tank = self.bzrc.get_othertanks()[0]
        x, y = enemy_tank.x, enemy_tank.y
        z_current = NP.matrix([[x], [y]])
        self.update_position_estimate(z_current)
        
        return

    def update_position_estimate(self, z_current):
        f_sigma_ft = self.F * self.sigma_t * self.F.T
        kalman_gain = self.calc_kalman_gain(f_sigma_ft)
        mu_current = self.F * self.mu_t + kalman_gain * (z_current - self.H * self.F * self.mu_t)
        sigma_current = self.calculate_sigma_current(f_sigma_ft, kalman_gain)
        print "sigma_current: " + str(sigma_current)

    def calc_kalman_gain(self, f_sigma_ft):
        top = f_sigma_ft * self.H.T
        bottom = self.H * (f_sigma_ft + self.sigma_x) * self.H.T + self.sigma_z
        kalman_gain = top * bottom.I
        return kalman_gain
    def update_f_matrix(self, delta_time):
        self.F[0,1] = delta_time
        self.F[0,2] = (delta_time ** 2) / 2
        self.F[1,2] = delta_time
        self.F[3,4] = delta_time
        self.F[3,5] = (delta_time ** 2) / 2
        self.F[4,5] = delta_time

    def calculate_sigma_current(self, f_sigma_ft, kalman_gain):
        left = NP.identity(6) - kalman_gain * self.H
        right = f_sigma_ft + self.sigma_x
        return left * right
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
