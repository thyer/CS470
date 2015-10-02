#!/usr/bin/env python

import matplotlib.pyplot as plt
from pylab import *
from bzrc import BZRC
from PathFinder import PathFinder

import os


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
        if point == path[len(path) - 1]:
            plot.plot(point[0], point[1], 'g*', markersize=12)  # goal point is green starr
        else:
            plot.plot(point[0], point[1], 'ro', markersize=6)
        prev_point = point


def plot_single(path, obstacles, filename):
    """Plot the path and some obstacles, and write the resulting
    image to a file"""
    fig, plot = initialize_plot(filename)
    show_path(plot, path)
    for obstacle in obstacles:
        show_obstacle(plot, obstacle)
    fig.savefig(filename, format='png')
    plt.close('all')


def plot_snapshots(snapshots, base_filename, obstacles, xlim=(-400, 400), ylim=(-400, 400)):
    for i in range(0, len(snapshots)):
        filename = base_filename + "_snap" + str(i) + ".png"
        fig, plot = initialize_plot(filename)
        snap = snapshots[i]

        for point in snap.visited:
            plot.plot(point[0], point[1], 'go', markersize=6)

        for point in snap.frontier:
            plot.plot(point[0], point[1], 'rx', markersize=8)


        for obstacle in obstacles:
            show_obstacle(plot, obstacle)

        fig.savefig(filename, format='png')
        plt.close('all')


def initialize_plot(filename, xlim=(-400, 400), ylim=(-400, 400)):
    print "Generating", filename
    fig = plt.figure()
    plot = plt.subplot(111)
    plot.set_xlim(xlim)
    plot.set_ylim(ylim)
    return fig, plot

def remove_old_plot_files():
    filelist = [ f for f in os.listdir("../plots/bfs_plots/") if f.endswith(".png") ]
    for f in filelist:
        os.remove("../plots/bfs_plots/" + f)

    filelist = [ f for f in os.listdir("../plots/dfs_plots/") if f.endswith(".png") ]
    for f in filelist:
        os.remove("../plots/dfs_plots/" + f)


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

    path_finder = PathFinder(bzrc, 0)
    remove_old_plot_files()

    ### Depth First Search Visualizations ###
    path = path_finder.get_depth_first_search_path()
    plot_single(path, bzrc.get_obstacles(), '../plots/dfs_plots/dfs.png')

    snapshots = path_finder.search_snapshots
    plot_snapshots(snapshots, "../plots/dfs_plots/dfs", bzrc.get_obstacles())

    ### Breadth First Search Visualizations ###
    path = path_finder.get_breadth_first_search_path()
    plot_single(path, bzrc.get_obstacles(), '../plots/bfs_plots/bfs.png')

    snapshots = path_finder.search_snapshots
    plot_snapshots(snapshots, "../plots/bfs_plots/bfs", bzrc.get_obstacles())


    print("finished")
    bzrc.close()

if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
