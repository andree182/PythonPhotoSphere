from . import Matrix
from vector import Vector
from math import sin, cos, asin

class RotationMatrix(Matrix):

    #def __init__(self, *args, dim = None, **kwargs):
    def __init__(self, *args, **kwargs):
        #dim = 3
        kwargs['dim'] = 3
        #super(RotationMatrix, self).__init__(*args, dim = dim, **kwargs)
        super(RotationMatrix, self).__init__(*args, **kwargs)

    def rotateX(self, angle):
        c, s = cos(angle), sin(angle)
        return self.set(
            self * Matrix( dim = 3, values =
                ( 1, 0, 0,
                  0, c,-s,
                  0, s, c)) )

    def rotateY(self, angle):
        c, s = cos(angle), sin(angle)
        return self.set(
            self * Matrix( dim = 3, values =
                ( c, 0, s,
                  0, 1, 0,
                 -s, 0, c)) )

    def rotateZ(self, angle):
        c, s = cos(angle), sin(angle)
        return self.set(
            self * Matrix( dim = 3, values =
                ( c,-s, 0,
                  s, c, 0,
                  0, 0, 1)) )

    def rotateXYZ(self, a, b, c):
        ca,sa,cb,sb,cc,sc = cos(a),sin(a),cos(b),sin(b),cos(c),sin(c)
        return self.set(
            self * Matrix( dim = 3, values =
                (           cb*cc, -sc*cb         ,    sb,
                   sa*sb*cc+ca*sc, -sa*sb*sc+ca*cc,-sa*cb,
                  -sb*ca*cc+sa*sc,  sc*sb*ca+sa*cc, ca*cb)) )

    def rotate(self, *args):
        if len(args) == 1:
            if isinstance(args[0], (int, float, complex)):
                return self.rotateZ(args[0])
        elif len(args) == 2:
            if   isinstance(args[0], Vector) and isinstance(args[1], (int, float, complex)):
                return self.rotateV(args[0], args[1])
            elif isinstance(args[1], Vector) and isinstance(args[0], (int, float, complex)):
                return self.rotateV(args[1], args[0])
        return self

    def rotateV(self, v, a):
        v = Vector(v).normalize()
        x, y, z, c, s = v.x, v.y, v.z, cos(a), sin(a); f = 1-c
        return self.set( self * Matrix( dim = 3, values =
            ( c+x*x*f , x*y*f-z*s, x*z*f+y*s,
             y*x*f+z*s,  c+y*y*f , y*z*f-x*s,
             z*x*f-y*s, z*y*f+x*s,  c+z*z*f )))

    def dorotate(self, vec):
        return Vector(self[0])*vec.x + Vector(self[1])*vec.y + Vector(self[2])*vec.z

    def rotateto(self, vec):
        this = Vector(self[0]) + Vector(self[1]) + Vector(self[2])
        cross = this * vec; cl = cross.length()
        value = cl / (this.length() * vec.length())
        a = asin(value); v = cross * (1/cl)
        x, y, z, c, s = v.x, v.y, v.z, cos(a), value; f = 1-c
        return self.set(self * Matrix( dim = 3, values =
            ( c+x*x*f , x*y*f-z*s, x*z*f+y*s,
             y*x*f+z*s,  c+y*y*f , y*z*f-x*s,
             z*x*f-y*s, z*y*f+x*s,  c+z*z*f )))



