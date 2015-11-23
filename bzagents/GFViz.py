#!/usr/bin/env python

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy


class GFViz(object):
    def __init__(self, occupancy_grid, dimension):
        self.init_window(dimension, dimension)
        self.grid = None
        self.window = None

    def init_window(self, width, height):
        self.grid = numpy.zeros((width, height))
        glutInit(())
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
        glutInitWindowSize(width, height)
        glutInitWindowPosition(0, 0)
        window = glutCreateWindow("Grid filter")
        glutDisplayFunc(self.draw_grid)
        glViewport(0, height, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def draw_grid(self):
        # This assumes you are using a numpy array for your grid
        width, height = self.grid.shape
        glPixelZoom(1.0, -1.0)
        glRasterPos2f(-1, -1)
        glDrawPixels(width, height, GL_LUMINANCE, GL_FLOAT, self.grid)
        glFlush()
        glutSwapBuffers()

    def update_grid(self, new_grid):
        self.grid = numpy.array(new_grid)
        self.draw_grid()

    def loop_eternally(self):
        print("Program entering eternal loop, close the visualization to end the program")
        glutMainLoop()
