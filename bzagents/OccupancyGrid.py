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
        print "Getting point density for: " + str(i) + ", " + str(j)
        print "Sensor range of: " + str(self.sensor_range)
        for x in range(self.sensor_range):
            for y in range(self.sensor_range):
                r = i - self.sensor_range/2 + x
                c = j - self.sensor_range/2 + y
                if self.is_outside_rc_bounds(r, c):
                    continue
                elif self.grid[r][c] > .0001 and self.grid[r][c] < .9999:
                    unknown_points += 1
                    total_points += 1
                else:
                    total_points += 1
        print "Points needing more info: " + str(unknown_points) + ", of total: " + str(total_points)
        output = unknown_points / total_points
        return output
    
    def is_outside_rc_bounds(self, r, c):
        return r >= len(self.grid) or r < 0 or c >= len(self.grid) or c < 0
        
    def is_outside_grid_bounds(self, x, y):
        r, c = self.convert_to_grid(x, y)
        return is_outside_rc_bound(r, c)

    def get_gc(self, x, y):
        r, c = self.convert_to_grid(x, y)
        return self.grid[r][c]
        
    def set_gc(self, x, y, value):
        r, c = self.convert_to_grid(x, y)
        self.grid[r][c] = value

    def convert_to_world(self, r, c):
        half_dim = len(self.grid) / 2
        return (c-half_dim, -1 * r + half_dim)
        
    def convert_to_grid(self, x, y):
        half_dim = len(self.grid) / 2
        return (abs(y - half_dim), abs(x + half_dim))
    
    def observe(self, x, y, ping):
        # apply Bayes rule to update the probability value given prior observations
        if ping:
            bel_occ = self.true_hit * self.get_gc(x, y)
            bel_unocc = self.false_alarm * (1-self.get_gc(x, y))
            self.set_gc(x, y, bel_occ/(bel_occ + bel_unocc))
        else:
            bel_occ = (1-self.true_hit) * self.get_gc(x, y)
            bel_unocc = (1-self.false_alarm) * (1 - self.get_gc(x, y))
            self.set_gc(x, y, bel_occ/(bel_occ + bel_unocc))
            
    def get_estimate(self, x, y):
        if self.get_gc(x, y) > .5:
            return True
        else:
            return False
            
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

    def get_target_point(self, tank_x, tank_y):
        if len(self.target_points) == 0:
            self.target_points = self.temp_target_points
            self.temp_target_points = []
        if len(self.target_points) == 0:
            return None
        
        min_point = None
        min_dist = float('inf')
        tank_x, tank_y = self.convert_to_grid(tank_x, tank_y)
        for point in self.target_points:
            dist = self.get_distance(point, (tank_x, tank_y))
            if dist < min_dist:
                min_point = point
                min_dist = dist
        
        self.target_points.remove(min_point)
        min_point = self.convert_to_world(min_point[0], min_point[1])
        return min_point
    
    def get_distance(self, point1, point2):
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

    def post_process_point(self, point):
        point_i, point_j = self.convert_to_grid(point[0], point[1])
        if self.get_point_density(point_i, point_j) > .15:
            self.temp_target_points.append((point_i, point_j))
        else:
            print "Target point successfully assessed: " + str(point)
