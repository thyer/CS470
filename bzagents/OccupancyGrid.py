import sys
import random
import time
import math

class OccupancyGrid(object):
    def __init__(self, dimensions, true_hit_rate, false_alarm_rate, tank_sensor_range):
        no_data = .5
        self.grid = [[no_data for x in range(dimensions)] for x in range(dimensions)] 
        self.true_hit = true_hit_rate
        self.false_alarm = false_alarm_rate
        self.sensor_range = tank_sensor_range
        self.target_points = []
        self.init_target_points(tank_sensor_range)
        
    def get_point_density(self, i, j):
        unknown_points = 0
        total_points = 0
        for x in range(self.sensor_range):
            for y in range(self.sensor_range):
                point_x = i - self.sensor_range/2 + x
                point_y = j - self.sensor_range/2 + y
                if point_x >= len(self.grid) or point_x < 0 or point_y >= len(self.grid) or point_y < 0:
                    continue
                elif self.grid[point_x][point_y] > .0001 and self.grid[point_x][point_y] < .9999:
                    unknown_points += 1
                    total_points += 1
                else:
                    total_points += 1
                    
        return unknown_points / total_points
        
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
            
    def get_estimate(self, i, j):
        if self.grid[i][j] > .5:
            return true
        else:
            return false
            
    def get_dimensions(self):
        return len(self.grid)

    def get_grid(self):
        return self.grid
