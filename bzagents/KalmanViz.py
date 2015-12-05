#!/usr/bin/env python

from Gnuplot import GnuplotProcess

class KalmanViz(object):
    def __init__(self, world_size):
        self.world_size = world_size

    def gnuplot_header(self, minimum, maximum):
        '''Return a string that has all of the gnuplot sets and unsets.'''
        s = ''
        s += 'set xrange [%s: %s]\n' % (minimum, maximum)
        s += 'set yrange [%s: %s]\n' % (minimum, maximum)
        s += 'set pm3d\n'
        s += 'set view map\n'
        # The key is just clutter.  Get rid of it:
        s += 'unset key\n'
        # Make sure the figure is square since the world is square:
        s += 'set size square\n'
        # Add a pretty title (optional):
        s += "set title 'Kalman Filter Output'\n"

        # set what color scheme to use
        s += 'set palette model XYZ functions gray**0.35, gray**0.5, gray**0.8\n'
        # How fine the plotting should be, at some processing cost:
        s += 'set isosamples 100\n'
        return s

    def draw_noise(self, sigma_x, sigma_y, rho):
        # set up the values and plot them
        s = ''
        s += 'sigma_x = %s\n' % sigma_x
        s += 'sigma_y = %s\n' % sigma_y
        s += 'rho = %s\n' % rho
        s += 'splot 1.0/(2.0 * pi * sigma_x * sigma_y * sqrt(1 - rho**2)) \
             * exp(-1.0/2.0 * (x**2 / sigma_x**2 + y**2 / sigma_y**2 \
             - 2.0*rho*x*y/(sigma_x*sigma_y))) with pm3d\n'
        return s

    def update_values(self, sigma_x, sigma_y, rho):
        gp = GnuplotProcess(persist=True)
        gp.write(self.gnuplot_header(-self.world_size / 2, self.world_size / 2))
        gp.write(self.draw_noise(sigma_x, sigma_y, rho))


def main():
    viz = KalmanViz(800)
    viz.update_values(20, 30, .3)  # TODO: Fill these numbers in with actual values

if __name__ == '__main__':
    main()


