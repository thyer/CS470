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
        self.temp_target_points = []
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
                elif self.get_gc(point_x, point_y) > .0001 and self.get_gc(point_x, point_y) < .9999:
                    unknown_points += 1
                    total_points += 1
                else:
                    total_points += 1
                    
        return unknown_points / total_points
    
    def get_gc(self, x, y):
        r, c = self.convert_to_grid(x, y)
        print "World " + str(x) + ", " + str(y) + " converts to: " + str(r) + ", " + str(c)
        return self.grid[r][c]
        
    def set_gc(self, x, y, value):
        r, c = self.convert_to_grid(x, y)
        self.grid[r][c] = value
        print "We just set grid coordinates " + str(r) + ", " + str(c) + " to be " + str(value)
    
    def convert_to_world(self, r, c):
        return (c-400, -1 * r + 400)
        
    def convert_to_grid(self, x, y):
        return (abs(y - 400), abs(x+400))
    
    def observe(self, i, j, ping):
        print("At [" + str(i) + ", " + str(j) + "]: " + str(self.get_gc(i, j)))
        # apply Bayes rule to update the probability value given prior observations
        if ping:
            bel_occ = self.true_hit * self.get_gc(i, j)
            bel_unocc = self.false_alarm * (1-self.get_gc(i, j))
            # print("BEL(OCC): " + str(bel_occ) + ", BEL(UNOCC): " + str(bel_unocc))
            print "setting " + str(i) + ", " + str(j) + " to " + str(bel_occ/(bel_occ + bel_unocc))
            self.set_gc(i, j, bel_occ/(bel_occ + bel_unocc))
        else:
            bel_occ = (1-self.true_hit) * self.get_gc(i, j)
            bel_unocc = (1-self.false_alarm) * (1 - self.get_gc(i, j))
            self.set_gc(i, j, bel_occ/(bel_occ + bel_unocc))
            
    def get_estimate(self, i, j):
        if self.get_gc(i, j) > .5:
            return true
        else:
            return false
            
    def get_dimensions(self):
        return len(self.grid)

    def get_grid(self):
        return self.grid

    def init_target_points(self, sensor_range):
        half_range = sensor_range / 2
        row = half_range

        while row < self.get_dimensions():
            col = half_range
            while col < self.get_dimensions():
                self.target_points.append((row, col))
                col += sensor_range
            row += sensor_range

        print("Target Points", self.target_points)
        
    def get_target_point(self, tank_x, tank_y):
        if len(self.target_points) == 0:
            self.target_points = self.temp_target_points
            self.temp_target_points = []
        if len(self.target_points) == 0:
            return None
        
        min_point = None
        min_dist = 100000
        tank_x, tank_y = self.convert_to_grid(tank_x, tank_y)
        print "tank x: " + str(tank_x)
        print "tank y: " + str(tank_y)
        for point in self.target_points:
            dist = self.get_distance(point, (tank_x, tank_y))
            print "distance from " + str(tank_x) + ", " + str(tank_y) + " to " + str(point) + " was " + str(dist)
            if  dist < min_dist:
                min_point = point
                min_dist = dist
        
        print "Best point was " + str(min_point)
        print "Distance was " + str(min_dist)
        min_point = self.convert_to_world(min_point[0], min_point[1])
        return min_point
    
    def get_distance(self, point1, point2):
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
            
