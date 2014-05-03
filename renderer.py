
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import os
import sys
import copy
from math import cos, sin, pi
from traceback import print_exc

import numpy
import numpy.oldnumeric as Numeric
import PIL.Image as Image
import urllib, cStringIO

from vector import Vector

pi2 = 2.0 * pi

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'


class drug(object):
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])


class Renderer(object):

    def __init__(self, width, height):
        self.size(width, height)
        self.initialized = False
        self.rot = drug(x = 90, z = 0)
        v = Vector(width * 0.5, height * 0.5, 0)
        self.mouse = dict(
            left   = drug(pos = v,        pressed = False),
            right  = drug(pos = v.copy(), pressed = False),
            middle = drug(pos = v.copy(), pressed = False))
        # gl stuff
        self.textures = numpy.zeros(1, numpy.int32)
        self.bgcolor = (0.0, 0.0, 0.0, 1.0)
        self.color = (1.0, 1.0, 1.0)
        self.tex = drug(width = 0, height = 0, data = 0)
        self.pct = drug(offset = 0.15)
        self.radius = 0.1
        self.depth = 1.0

    def size(self, width, height):
        self.height = float(height)
        self.width = float(width)

    def load(self, filename):
        if os.path.isfile(filename):
            file = "file://{0}".format(os.path.abspath(filename))
        else:
            file = cStringIO.StringIO(urllib.urlopen(filename).read())
        im = Image.open(file)
        width, height = im.size
        pixels = im.getdata()
        pixelData = im.load()
        rowSkip = int(height * self.pct.offset)
        curHeight = int(height * (1 + 2 * self.pct.offset))
        c = numpy.zeros(width * curHeight * 3, numpy.uint8)
        for hj in range(curHeight):
            j = hj - rowSkip
            #if j in range(height):
            if (j >= 0) and (j < height):
                for i in range(width):
                    p = 3 * (hj * width + i)
                    d = pixelData[i,j]
                    c[p    ] = d[0]
                    c[p + 1] = d[1]
                    c[p + 2] = d[2]
        self.tex.width = width
        self.tex.height = curHeight
        self.tex.data = c
        #self.tex.data  = numpy.asarray(im, dtype = 'uint8')

    def initialize(self):
        if self.initialized: return
        self.initialized = True
        glClearColor(*self.bgcolor)
        glClearDepth(self.depth)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_FLAT)
        #glShadeModel (GL_SMOOTH)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        self.quadratic = gluNewQuadric()
        gluQuadricOrientation(self.quadratic, GLU_INSIDE)
        gluQuadricOrientation(self.quadratic, GLU_OUTSIDE)
        gluQuadricNormals(    self.quadratic, GLU_SMOOTH)
        gluQuadricDrawStyle(  self.quadratic, GLU_FILL)
        gluQuadricTexture(    self.quadratic, GL_TRUE)
        # ----
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_TEXTURE_2D)
        # ----
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glGenTextures(1, self.textures)
        # ----
        glBindTexture(  GL_TEXTURE_2D, self.textures[0])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(   GL_TEXTURE_2D, 0, GL_RGB,
                        self.tex.width, self.tex.height, 0,
                        GL_RGB, GL_UNSIGNED_BYTE, self.tex.data)

    def destroy(self):
        if not self.initialized: return
        self.initialized = False
        gluDeleteQuadric(self.quadratic)

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glDisable(GL_LIGHTING)
        glDisable(GL_NORMALIZE)
        glDisable(GL_CULL_FACE)
        # ----
        glPushMatrix()
        glRotatef(self.rot.x, 1, 0, 0)
        glRotatef(self.rot.z, 0, 0, 1)
        glColor3f(*self.color)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.textures[0])
        gluSphere(self.quadratic, self.radius, 50, 50)
        glBindTexture(GL_TEXTURE_2D, 0)
        glPopMatrix()
        # ----
        glFlush()
        glutSwapBuffers()

    def onClick(self, button, button_state, cursor_x, cursor_y):
        # cursor position
        if button == GLUT_LEFT_BUTTON:
            b = 'left'
        elif button == GLUT_RIGHT_BUTTON:
            b = 'right'
        elif button == GLUT_MIDDLE_BUTTON:
            b = 'middle'
        else: b = None
        self.mouse[b].pos.set(cursor_x, cursor_y, 0)
        # button state
        if button_state == GLUT_UP:
            self.mouse[b].pressed = False
        elif button_state == GLUT_DOWN:
            self.mouse[b].pressed = True

    def onDrag(self, cursor_x, cursor_y):
        if self.mouse['left'].pressed:
            self.rot.x += self.radius * 0.5 * (self.mouse['left'].pos.y - cursor_y)
            self.rot.z += self.radius *       (cursor_x - self.mouse['left'].pos.x)
            self.mouse['left'].pos.set(cursor_x, cursor_y, 0)
            # bounderies
            if    self.rot.x < 0:   self.rot.x  = 0
            if    self.rot.x > 180: self.rot.x  = 180
            while self.rot.z < 0:   self.rot.z += 360
            while self.rot.z > 360: self.rot.z -= 360


class Window(object):

    def __init__(self, width, height):
        self.renderer = Renderer(width, height)
        self.size(width, height)
        self.id = None
        # gl stuff
        self.fov = 75.0

    def size(self, width, height):
        self.height = int(height)
        self.width = int(width)

    def resize(self, width, height):
        if height == 0: height = 1
        self.size(width, height)
        self.renderer.size(width, height)
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov,
                       self.renderer.width / self.renderer.height,
                       0.0, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def onKeyPressed(self, *keys):
        if ESCAPE in keys or 'q' in keys:
            self.close()

    def close(self):
        self.renderer.destroy()
        sys.exit()

    def open(self, filename, argv = sys.argv):
        glutInit(argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(0, 0)
        self.id = glutCreateWindow("PhotoSphere Python viewer")
        glutDisplayFunc(self.renderer.draw)
        glutIdleFunc(self.renderer.draw)
        glutReshapeFunc(self.resize)
        glutKeyboardFunc(self.onKeyPressed)
        glutMouseFunc(self.renderer.onClick)
        glutMotionFunc(self.renderer.onDrag)
        try:
            self.renderer.load(filename)
        except:
            print_exc()
        else:
            self.renderer.initialize()
            glutMainLoop()
