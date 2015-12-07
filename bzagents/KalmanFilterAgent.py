#!/usr/bin/python -tt

import sys
import random
import math
import time
import numpy as NP

from bzrc import BZRC, Command
from KalmanViz import KalmanViz


class KalmanFilterAgent(object):
    def __init__(self, bzrc, tank_index, viz):
        print "Constructing KalmanFilterAgent"
        self.bzrc = bzrc
        self.tank_index = tank_index
        self.viz = viz
        self.commands = []
        self.counter = 0
        tank = self.bzrc.get_mytanks()[self.tank_index]
        self.tank_pos = (tank.x, tank.y)
        self.shot_speed = int(self.bzrc.get_constants()['shotspeed'])
        
        # constant matrices
        self.sigma_x = NP.matrix('0.1 0.2 0 0 0 0;' + \
        '.2 0.1 0 0 0 0; 0 0 100 0 0 0; 0 0 0 0.1 0 0;' + \
        '0 0 0 0 0.1 0; 0 0 0 0 0 100')
        self.sigma_z = NP.matrix('25.0 0; 0 25')
        self.H = NP.matrix('1.0 0 0 0 0 0; 0 0 0 1 0 0')
        
        # instantiated matrices
        self.mu_t = NP.matrix('0.0; 0; 0; 0; 0; 0')
        self.sigma_t = NP.matrix('500.0 0 0 0 0 0;' + \
        '0 0.5 0 0 0 0; 0 0 0.1 0 0 0; 0 0 0 500 0 0;' + \
        '0 0 0 0 0.5 0; 0 0 0 0 0 0.1')
        
        # variable matrix
        self.F = NP.matrix('1.0 0.0 0.0 0 0 0; 0 1 0 0 0 0; 0 0 1 0 0 0;' + \
        '0 0 0 1 0 0; 0 0 0 0 1 0; 0 0 0 0 0 1')
        c = 0.01
        self.F[2, 1] = -c
        self.F[5, 4] = -c
        
        # other tracking variables
        self.delta_time = 0

    def tick(self, d_time):
        self.commands = []

        # update our F matrix depending on how much time has passed
        if d_time != self.delta_time:
            self.update_f_matrix(d_time)
            selfdelta_time = d_time
            
        # get our updated location estimate and standard deviation
        enemy_tank = self.bzrc.get_othertanks()[0]
        x, y = enemy_tank.x, enemy_tank.y
        z_current = NP.matrix([[x], [y]])
        self.update_position_estimate(z_current)

        if self.counter % 100 == 0: # if we update the visualizations too often, it bogs down the entire program
            mu_x = self.mu_t.item(0)
            mu_y = self.mu_t.item(3)
            sig_x = self.sigma_t.item((0, 0))
            sig_y = self.sigma_t.item((3, 3))
            rho = self.sigma_t.item((0, 3))
            self.viz.update_values(sig_x, sig_y, rho, mu_x, mu_y)
        self.counter += 1
        
        calc_position = self.calc_position_to_shoot(self.mu_t)
        # self.move_to_position(calc_position)
        
        return

    def calc_position_to_shoot(self, mu_t):
        pos_0 = mu_t.item(0), mu_t.item(3)
        d_0 = self.calc_distance(self.tank_pos, pos_0)
        t_0 = d_0/self.shot_speed
        best_guess_pos = pos_0
        best_guess_t = t_0
        
        next_estimate = self.predict_mu_after(best_guess_t)
        pos_next = next_estimate.item(0), next_estimate.item(3)
        d_next = self.calc_distance(self.tank_pos, pos_next)
        t_next = d_next/self.shot_speed
        
        while(abs(t_next - best_guess_t) > 0.01):
            best_guess_pos = pos_next
            best_guess_t = t_next
            next_estimate = self.predict_mu_after(best_guess_t)
            pos_next = next_estimate.item(0), next_estimate.item(3)
            d_next = self.calc_distance(self.tank_pos, pos_next)
            t_next = d_next/self.shot_speed
        return best_guess_pos
        
    def predict_mu_after(self, delta_t):
        print "Delta_time = " + str(delta_t)
        self.update_f_matrix(delta_t)
        prediction = self.F * self.mu_t
        return prediction
    
    def calc_distance(self, pos0, pos1):
        print "pos0: " + str(pos0) + ", pos1: " + str(pos1)
        return math.sqrt((pos0[0]-pos1[0]) ** 2 + (pos0[1]-pos1[1]) ** 2)
        
    def update_position_estimate(self, z_current):
        f_sigma_ft = self.F * self.sigma_t * self.F.T
        kalman_gain = self.calc_kalman_gain(f_sigma_ft)
        mu_current = self.F * self.mu_t + kalman_gain * (z_current - self.H * self.F * self.mu_t)
        sigma_current = self.calculate_sigma_current(f_sigma_ft, kalman_gain)
        x = mu_current[0,0]
        y = mu_current[3,0]
        u_x = sigma_current[0,0]
        u_y = sigma_current[3,3]
        print "Estimation: " + str(x) + ", " + str(y)
        # print "Full sigma matrix: " + str(sigma_current)
        print "Uncertainty: " + str(u_x) + ", " + str(u_y)
        self.mu_t = mu_current
        self.sigma_t = sigma_current

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

    world_size = int(bzrc.get_constants()['worldsize'])
    viz = KalmanViz(world_size)

    # Create our army
    # TODO: Are we only dealing with one agent on our team? If not, we need to be careful about visualizations!

    agents = []
    index = 0
    agent = KalmanFilterAgent(bzrc, index, viz)
    agents.append(agent)

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
        viz.destroy()

if __name__ == '__main__':
    main()
