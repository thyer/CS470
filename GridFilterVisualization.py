#!/usr/bin/env python

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy
import random

grid = None

def draw_grid():
    # This assumes you are using a numpy array for your grid
    width, height = grid.shape
    glRasterPos2f(-1, -1)
    glDrawPixels(width, height, GL_LUMINANCE, GL_FLOAT, grid)
    glFlush()
    glutSwapBuffers()

def update_grid(new_grid):
    global grid
    grid = numpy.array(new_grid)


def init_window(width, height):
    global window
    global grid
    grid = numpy.zeros((width, height))
    glutInit(())
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(0, 0)
    window = glutCreateWindow("Grid filter")
    glutDisplayFunc(draw_grid)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def main():
    init_window(600, 600)

    x = 0
    while x < 10:
        arr = [[0 for _ in range(600)] for _ in range(600)]
        for i in range(0, 600):
            for j in range(0, 600):
                arr[i][j] = random.random()

        update_grid(arr)
        draw_grid()
        x += 1

    print("Program entering eternal loop, close the visualization to end the program")
    glutMainLoop()

if __name__ == '__main__':
    main()
