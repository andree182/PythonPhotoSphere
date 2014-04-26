from math import sqrt
from array import array


class Matrix(object):

    def __init__(self, values = (), dim = None, **kwargs):
        super(Matrix, self).__init__()
        if dim is None:
            d = sqrt(len(values))
            if int(d) == d: dim = int(d)
            else: raise Exception("Matrix dimension is not calculable.")
        if dim <= 0: dim = 1
        self.dim = dim
        self.set(values)

    def __add__(self, other):
        return madd(self, other)

    def __sub__(self, other):
        return msub(self, other)

    def __mul__(self, x):
        if isinstance(x, (int, float, complex)):
            t = tuple( m*x for m in self._m )
            return self.__class__( values = t,dim = self.dim )
        return mmul(self, x)

    def __getitem__(self, key):
        d = self.dim
        r = range(d)
        if type(key) is tuple:
            x, y = key
            if type(y) is slice:
                if type(x) is slice:
                    result = ()
                    for n in tuple(r)[y]:
                        result += self[None,n][x]
                    return result
                elif type(x) is tuple:
                    if len(x) > d: raise IndexError
                    result = ()
                    for n in tuple(r)[y]:
                        result += tuple( self[None,n][i] for i in x )
                    return result
                else:
                    if x not in r: raise IndexError
                    return self[x][y]
            elif type(y) is tuple:
                if len(y) > d: raise IndexError
                if type(x) is slice:
                    result = ()
                    for n in y: result += self[None,n][x]
                    return result
                elif type(x) is tuple:
                    if len(x) > d: raise IndexError
                    result = ()
                    for n in y: result += tuple( self[i,n] for i in x )
                    return result
                else:
                    if x not in r: raise IndexError
                    return tuple( self[x,n] for n in y )
            elif type(x) is slice:
                if y not in r: raise IndexError
                return self[None,y][x]
            elif type(x) is tuple:
                if y not in r or len(x) > d: raise IndexError
                return tuple( self[None,y][i] for i in x )
            if y not in r: raise IndexError
            if x not in r:
                return tuple(self._m[y*d:(y+1)*d])
            else: return self._m[ x + y*d ]
        else:
            if key not in r: raise IndexError
            return tuple( self._m[key:len(self)-d+1+key:d] )

    def __setitem__(self, key, value):
        d = self.dim
        r = range(d)
        if type(key) is tuple:
            x, y = key
            if y not in r: raise IndexError
            if x not in r:
                if type(value) is not tuple: raise KeyError
                if len(value) < d: raise KeyError
                for i in r: self._m[y*d+i] = value[i]
            else:
                if type(value) is tuple: raise KeyError
                self._m[ x + y*d ] = value
        else:
            if key not in r: raise IndexError
            if type(value) is not tuple: raise KeyError
            if len(value) < d: raise KeyError
            for i in r: self._m[i*d+key] = value[i]

    def __contains__(self, value):
        return value in self._m

    def __eq__(self, other):
        return isinstance(other, Matrix) and \
            self._m == other._m

    def __len__(self):
        return int(self.dim*self.dim)

    def __repr__(self):
        return "<Matrix "+repr(list(self._m))+">"

    def tuple(self):
        return tuple(self._m)

    def tuples(self):
        d = self.dim
        return tuple( self[i,0:d] for i in range(d) )

    def set(self, *args):
        a = None
        if len(args) == 1:
            if isinstance(args[0], Matrix): a = args[0].tuple()
            elif type(args[0]) is tuple: args = args[0]
        if len(args) == 0: return self.reset()
        elif len(args) == len(self): a = args
        if a is not None: self._m = array('d', a)
        return self

    def reset(self):
        d = self.dim
        if d == 1: return self.set(1)
        r = (1,)
        for i in range(d-1): r += (0,)*d + (1,)
        return self.set(r)

    def copy(self):
        return self.__class__( values = self, dim = self.dim )

    def addDimension(self, n):
        result, d, _ = (), self.dim, None
        for i in range(d): result += self[_,i] + (0,)*n
        result += (0,)*d + (1,); dn = d+n
        for i in range(n-1): result += (0,)*dn + (1,)
        self.dim += n
        return self.set(*result)

    def transpose(self):
        for y in range(self.dim):
            for x in range(y,self.dim):
                self[x,y], self[y,x] = self[y,x], self[x,y]
        return self.set(self)

    def determinant(self):
        d = self.dim
        if   d == 1: return self._m[0]
        elif d == 2: return determinant2x2(*self.tuple())
        elif d == 3: return determinant3x3(*self.tuple())
        else:
            result, s, r = 0, -1, range(d)
            for i in r:
                l = list(r); l.remove(i); s *= -1
                result += s * self[i,0] * Matrix( dim = self.dim-1,
                        values = self[tuple(l), 1:] ).determinant()
            return result

    def invert(self):
        det, d = self.determinant(), self.dim
        if det == 0: return False
        if d == 1:
            self._m[0] = -self._m[0]
            return True
        values, a, r = [], 1, range(d)
        for y in r:
            h = list(r); h.remove(y); h = tuple(h); a *= -1; s = a
            for x in r:
                w = list(r); w.remove(x); w = tuple(w); s *= -1
                values.append( s * Matrix(dim=d-1,values=self[w,h]).determinant() )
        helper = Matrix( dim = d, values = tuple(values))
        self.set(helper.transpose() * (1/det))
        return True

def madd(a, b):
    if a.dim != b.dim: raise Exception("Both Matrix should have the same size.")
    return Matrix( tuple( a[x,y] + b[x,y] for y in range(a.dim) for x in range(b.dim) ) )

def msub(a, b):
    if a.dim != b.dim: raise Exception("Both Matrix should have the same size.")
    return Matrix( tuple( a[x,y] - b[x,y] for y in range(a.dim) for x in range(b.dim) ) )

def mmul(a, b):
    if a.dim != b.dim: raise Exception("Both Matrix should have the same size.")
    r, _ = Matrix(dim = a.dim), None
    for y in range(b.dim):
        for x in range(a.dim):
            temp, col, row = 0, b[x], a[_,y]
            for i in range(b.dim): temp += col[i] * row[i]
            r[x,y] = temp
    return r

def determinant2x2(*m):
    if len(m) == 1:
        if type(m[0]) is tuple: m = m[0]
    if len(m) != 4: return 0
    return m[0] * m[3] - m[1] * m[2]

def determinant3x3(*m):
    if len(m) == 1:
        if type(m[0]) is tuple: m = m[0]
    if len(m) != 9: return 0
    return  m[0] * m[4] * m[8] \
          + m[3] * m[7] * m[2] \
          + m[6] * m[1] * m[5] \
          - m[2] * m[4] * m[6] \
          - m[5] * m[7] * m[0] \
          - m[8] * m[1] * m[3]
