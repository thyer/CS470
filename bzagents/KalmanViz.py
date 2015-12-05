#!/usr/bin/env python

from Gnuplot import GnuplotProcess

class KalmanViz(object):
    def __init__(self, world_size):
        self.gp = GnuplotProcess(persist=False)
        self.gp.write(self.gnuplot_header(-world_size / 2, world_size / 2))


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

    def draw_noise(self, sigma_x, sigma_y, rho, mu_x, mu_y):
        # set up the values and plot them
        s = ''
        s += 'sigma_x = %s\n' % sigma_x
        s += 'sigma_y = %s\n' % sigma_y
        s += 'rho = %s\n' % rho
        s += 'mu_x = %s\n' % mu_x
        s += 'mu_y = %s\n' % mu_y

        piece_1 = '1.0 / (2.0 * pi * sigma_x * sigma_y * sqrt(1 - rho**2))'
        piece_2 = '-1.0 / (2.0 * (1.0 - rho**2))'
        piece_3 = '(x - mu_x)**2 / sigma_x**2'
        piece_4 = '(y - mu_y)**2 / sigma_y**2'
        piece_5 = '(2.0 * rho * (x - mu_x) * (y - mu_y)) / (sigma_x * sigma_y)'
        s += 'splot %s * exp(%s * (%s + %s - %s)) with pm3d\n' % (piece_1, piece_2, piece_3, piece_4, piece_5)

        return s

    def update_values(self, sigma_x, sigma_y, rho, mu_x, mu_y):
        self.gp.write(self.draw_noise(sigma_x, sigma_y, rho, mu_x, mu_y))
        self.gp.flush()

    def destroy(self):
        self.gp.write('exit')
        self.gp.flush()


