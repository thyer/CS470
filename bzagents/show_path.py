#!/usr/bin/env python

import matplotlib.pyplot as plt
from pylab import *
from PathAgent import PathAgent
from bzrc import BZRC


def show_obstacle(plot, points):
    """Draw a polygon. Points is a list if [x,y] tuples
    """
    for p1, p2 in zip(points, [points[-1]] + list(points)):
        plot.plot([p1[0], p2[0]], [p1[1], p2[1]], 'b')


def show_path(plot, path):
    prev_point = None
    for point in path:
        if prev_point:
            plot.plot([point[0], prev_point[0]], [point[1], prev_point[1]], 'r')
        plot.plot(point[0], point[1], 'r*', markersize=12)
        prev_point = point


def plot_single(path, obstacles, filename, xlim=(-400, 400), ylim=(-400, 400)):
    """Plot the path and some obstacles, and write the resulting
    image to a file"""
    print "Generating", filename
    fig = plt.figure()
    plot = plt.subplot(111)
    plot.set_xlim(xlim)
    plot.set_ylim(ylim)
    show_path(plot, path)
    for obstacle in obstacles:
        show_obstacle(plot, obstacle)
    fig.savefig(filename, format='png')


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
    agent = PathAgent(bzrc, 0)

    agent.depth_first_search()
    print agent.path
    plot_single(agent.path, bzrc.get_obstacles(), 'dfs.png')

    agent.breadth_first_search()
    print agent.path
    plot_single(agent.path, bzrc.get_obstacles(), 'bfs.png')

    print("finished")
    bzrc.close()

if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
