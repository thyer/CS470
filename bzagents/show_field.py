#!/usr/bin/env python

"""
README

This should get some of the boilerplate out of the way for you in visualizing
your potential fields.

Notably absent from this code is anything dealing with vectors, the
interaction of multiple fields, etc. Your code will be a lot easier if you
define your potential fields in terms of vectors (angle, magnitude). For
plotting, however, you'll need to turn them back into dx and dy.
"""


import matplotlib.pyplot as plt
from pylab import *
import math
import random
from PFAgent import PFAgent
from bzrc import BZRC

from math import atan2, cos, sin, sqrt, pi


##### PLOTTING FUNCTIONS #####


def show_obstacle(plot, points):
    """Draw a polygon. Points is a list if [x,y] tuples
    """
    for p1, p2 in zip(points, [points[-1]] + list(points)):
        plot.plot([p1[0], p2[0]], [p1[1], p2[1]], 'b')


def show_arrows(plot, potential_func, xlim=(-400, 400), ylim=(-400, 400), res=20):
    """
    Arguments:
        fns: a list of potential field functions
        xlim, ylim: the limits of the plot
        res: resolution for (spacing between) arrows
    """
    plot.set_xlim(xlim)
    plot.set_ylim(ylim)
    for x in range(xlim[0], xlim[1] + res, res):
        for y in range(ylim[0], ylim[1] + res, res):
            force = potential_func(DummyTank(x,  y))
            dx = force[0]
            dy = force[1]
            if dx + dy == 0: continue
            plot.arrow(x, y, dx, dy, head_width=res/7.0, color='red', linewidth=.3)


def plot_single(potential_func, obstacles, filename, xlim=(-400, 400), ylim=(-400, 400)):
    """Plot a potential function and some obstacles, and write the resulting
    image to a file"""
    print "Generating", filename
    fig = plt.figure()
    plot = plt.subplot(111)
    show_arrows(plot, potential_func, xlim=xlim, ylim=ylim)
    for obstacle in obstacles:
        show_obstacle(plot, obstacle)
    fig.savefig(filename, format='png')


class DummyTank(object):
     def __init__(self, x, y):
         self.x = x
         self.y = y


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
    agent = PFAgent(bzrc)

    plot_single(agent.calculate_obstacles_force, agent.obstacles, 'obstacles.png')
    plot_single(agent.calculate_goal_force, agent.obstacles, 'goal.png')
    plot_single(agent.calculate_random_force, agent.obstacles, 'random.png')
    plot_single(agent.calculate_tangential_force, agent.obstacles, 'tangential.png')

    plot_single(agent.get_forces_on_tank, agent.obstacles, 'combined.png')

    print("finished")
    bzrc.close()

if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
