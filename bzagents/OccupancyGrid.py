import sys
import random
import time
import math

class OccupancyGrid(object):
    def __init__(self, dimensions):
        no_data = .5
        self.grid = [[no_data for x in range(dimensions)] for x in range(dimensions)] 
        self.true_hit = .97
        self.false_alarm = .1
        
    def observe(self, i, j, ping):
        print("At [" + str(i) + ", " + str(j) + "]: " + str(self.grid[i][j]))
        # apply Bayes rule to update the probability value given prior observations
        if ping:
            bel_occ = self.true_hit * self.grid[i][j]
            bel_unocc = self.false_alarm * (1-self.grid[i][j])
            # print("BEL(OCC): " + str(bel_occ) + ", BEL(UNOCC): " + str(bel_unocc))
            self.grid[i][j] = bel_occ/(bel_occ + bel_unocc)
        else:
            bel_occ = (1-self.true_hit) * self.grid[i][j]
            bel_unocc = (1-self.false_alarm) * (1 - self.grid[i][j])
            self.grid[i][j] = bel_occ/(bel_occ + bel_unocc)
        
    def observe2(self, i, j, ping):
        print("At [" + str(i) + ", " + str(j) + "]: " + str(self.grid[i][j]))
        # apply Bayes rule to update the probability value given prior observations
        likelihood = 0
        predicted_prior = .9 * self.grid[i][j] + .1 * (1-self.grid[i][j])
        normalizer = 0
        if ping:
            likelihood = .97
            normalizer = .97 + .1
        else:
            likelihood = .03
            normalizer = .03 + .9
        
        self.grid[i][j] = likelihood * predicted_prior / normalizer
            
    def get_estimate(self, i, j):
        if self.grid[i][j] > .5:
            return true
        else:
            return false
            
    def get_dimensions(self):
        return len(self.grid)
