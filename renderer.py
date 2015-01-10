
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

MAX_RADIUS_SCALE_RATIO = 0.9
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
        self.scale = 0.0 # actually the way towards the sphere surface
        self.maxScale = self.radius * MAX_RADIUS_SCALE_RATIO
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
        
        im.thumbnail((8192, 4096))
        
        width, height = im.size
        c = numpy.asarray(im, numpy.uint8)
        self.tex.width = width
        self.tex.height = height
        self.tex.data = c
        #self.tex.data = numpy.asarray(im, dtype = 'uint8')

    def initialize(self):
        if self.initialized: return
        self.initialized = True
        glClearColor(*self.bgcolor)
        glClearDepth(self.depth)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_FLAT)
        glShadeModel (GL_SMOOTH)
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
        glTranslatef(0, 0, self.scale)
        glRotatef(self.rot.x, 1, 0, 0)
        glRotatef(self.rot.z, 0, 0, 1)
        glColor3f(*self.color)
        gluSphere(self.quadratic, self.radius, 50, 50)
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
        if b is not None:
            self.mouse[b].pos.set(cursor_x, cursor_y, 0)
            # button state
            if button_state == GLUT_UP:
                self.mouse[b].pressed = False
            elif button_state == GLUT_DOWN:
                self.mouse[b].pressed = True
        elif button in [3, 4]: # wheel event
            # button state
            if button == 3:
                self.scale += 0.001
            elif button == 4:
                self.scale -= 0.001
            # bounderies
            while self.scale < -self.radius: self.scale = -self.radius
            while self.scale >  self.radius: self.scale =  self.radius

    def onDrag(self, cursor_x, cursor_y):
        if self.mouse['left'].pressed:
            self.rot.x += self.radius * 0.5 * (self.mouse['left'].pos.y - cursor_y)
            self.rot.z += self.radius *       (cursor_x - self.mouse['left'].pos.x)
            self.mouse['left'].pos.set(cursor_x, cursor_y, 0)
            self.clampRotation()
        if self.mouse['middle'].pressed:
            self.scale += 0.002 * (self.mouse['middle'].pos.y - cursor_y)
            self.mouse['middle'].pos.set(cursor_x, cursor_y, 0)
            self.clampScale()

    def onSpecial(self, f, x = 0, y = 0):
        if f == GLUT_KEY_UP:
            self.rot.x -= 10
        if f == GLUT_KEY_DOWN:
            self.rot.x += 10
        if f == GLUT_KEY_LEFT:
            self.rot.z += 10
        if f == GLUT_KEY_RIGHT:
            self.rot.z -= 10
        if f == GLUT_KEY_PAGE_UP:
            self.scale += 0.01
        if f == GLUT_KEY_PAGE_DOWN:
            self.scale -= 0.01
        if f == GLUT_KEY_HOME:
            self.scale - 1
        self.clampRotation()
        self.clampScale()
            
    def clampRotation(self):
        if    self.rot.x < 0:   self.rot.x  = 0
        if    self.rot.x > 180: self.rot.x  = 180
        while self.rot.z < 0:   self.rot.z += 360
        while self.rot.z > 360: self.rot.z -= 360

    def clampScale(self):
        if self.scale < -self.maxScale: self.scale = -self.maxScale
        if self.scale >  self.maxScale: self.scale =  self.maxScale

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
        if '0' in keys:
            self.renderer.scale = 0.0
        if '+' in keys:
            self.renderer.onSpecial(GLUT_KEY_PAGE_UP)
        if '-' in keys:
            self.renderer.onSpecial(GLUT_KEY_PAGE_DOWN)
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
        glutSpecialFunc(self.renderer.onSpecial)
        glutMouseFunc(self.renderer.onClick)
        glutMotionFunc(self.renderer.onDrag)
        try:
            self.renderer.load(filename)
        except:
            print_exc()
        else:
            self.renderer.initialize()
            glutMainLoop()
