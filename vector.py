from math import sqrt, atan2, cos, sin

class Vector(object):
    def __init__(self, *args, **kwargs):
        super(Vector, self).__init__()
        _ = None
        values = kwargs.get('values', _)
        x, y, z = kwargs.get('x', _), kwargs.get('y', _), kwargs.get('z', _)
        if values is not None: self.set(values)
        elif x is not None or y is not None or z is not None:
            self.set(x or 0,y or 0,z or 0)
        else:
            self.set(*args)
        if not hasattr(self, 'x'): self.reset()

    @staticmethod
    def from_polar_xy(angle, length):
        return from_polar_xy(angle, length)

    def set(self, *args):
        a = None
        if len(args) == 1:
            if type(args[0]) is tuple: args = args[0]
            if len(args) == 0: return self.reset()
            elif isinstance(args[0], Vector): a = args[0].tuple()
        if len(args) == 0: return self.reset()
        elif len(args) == 3: a = args
        if a is not None: self.x, self.y, self.z = a
        return self

    def reset(self):
        return self.set(0, 0, 0)

    def copy(self):
        return Vector(*self.tuple())

    def __add__(self, other):
        return vadd(self, other)

    def __sub__(self, other):
        return vsub(self, other)

    def __mul__(self, x):
        if isinstance(x, Vector):
            return vcross(self, x)
        return vmul(x, self)

    def __truediv__(self, x):
        return vmul(1/x, self)

    def __eq__(self, other):
        return isinstance(other, Vector) and \
            self.x == other.x and self.y == other.y and self.z == other.z

    def __repr__(self):
        return "<Vector x={0} y={1} z={2}>".format(self.x, self.y, self.z)

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def tuple(self):
        return (self.x, self.y, self.z)

    def length(self):
        return vlength(self)

    def with_length(self, l):
        return self.normalize() * l

    def direction(self):
        return direction(self)

    def direction_to(self, other):
        return direction_to(self, other)

    def distance(self, other):
        return distance(self, other)

    def sq_distance(self, other):
        return squared_distance(self, other)

    def normalize(self):
        return self.set(vnormalize(self))

    def dot(self, other):
        return vdot(self, other)

def vsub(a, b):
    return Vector(a.x - b.x, a.y - b.y, a.z - b.z)

def vadd(a, b):
    return Vector(a.x + b.x, a.y + b.y, a.z + b.z)

def vmul(x, v):
    return Vector(x * v.x, x * v.y, x * v.z)

def vcross(a, b):
    return Vector(a.y * b.z - a.z * b.y,
                  a.z * b.x - a.x * b.z,
                  a.x * b.y - a.y * b.x)

def direction(a):
    return atan2(a.y, a.x)

def direction_to(a, b):
    return atan2(b.y - a.y, b.x - a.x)

def sqvlength(v):
    return vdot(v,v)

def vlength(v):
    return sqrt(sqvlength(v))

def distance(a, b):
    return vlength(vsub(a, b))

def squared_distance(a, b):
    return sqvlength(vsub(a, b))

def vnormalize(v):
    return vmul(1/vlength(v), v)

def from_polar_xy(angle, length):
    return Vector(
        x = cos(angle) * length,
        y = sin(angle) * length,
        z = 0)

def vdot(a, b): # alias scalar
    return a.x * b.x + a.y * b.y + a.z * b.z

def intersection_point(point1, direction1, point2, direction2):
    dir_cross = direction1 * direction2
    proof = (point2 - point1) * direction2
    multiplier = list(map(lambda t: None if t[0] == 0 else t[1] / t[0] ,
        zip(dir_cross.tuple(),proof.tuple())))
    if not None in multiplier:
        mr = list(map(lambda f: round(f,13) ,multiplier))
        if len(set(mr)) == 1:
            return point1 + (direction1 * multiplier[0])
    return None

def minimal_distance_between_straights(point1, direction1, point2, direction2):
    return abs(vdot(point2-point1, (direction1*direction2).normalize() ))

def straight_distance(point1, direction1, point2, direction2):
    u, v, w = direction1, direction2, point1 - point2
    a, b, c, d, e = u.dot(u), u.dot(v), v.dot(v), u.dot(w), v.dot(w)
    D = a * c - b * b
    if D < 0.00000000001:
        sc, tc = 0.0, d/b if b>c else e/c
    else:
        sc, tc = (b * e - c * d) / D, (a * e - b * d) / D
    return (point1 + u*sc , point2 + v*tc)


