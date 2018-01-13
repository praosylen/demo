from __future__ import print_function
from time import sleep
import operator
ARRAY_SIZE = (100, 50)
XRES_OVER_YRES = 0.5

#A class representing arbitrary-dimensional vectors that's designed to be as straightforward to use as possible.
class V:
    def __init__(self, *args):
        if len(args) == 1 and hasattr(args[0], '__iter__'):
            self._t = tuple(map(float, args[0]))
            self._d = len(self._t)
        else:
            self._t = tuple(map(float, args))
            self._d = len(args)
    def __str__(self):
        return "<" + str(self._t)[1:-1] + ">"
    def __repr__(self):
        return "V" + str(self._t)
    def __eq__(self, other):
        return self._t == other._t
    def __ne__(self, other):
        return self._t != other._t
    __hash__ = None
    def __len__(self):
        return self._d
    def __getitem__(self, ind):
        return self._t[ind]
    def __setitem__(self, ind, val):
        foo = self._t[ind] #To raise the correct exceptions
        l = list(self._t)
        l[ind] = val
        self._t = tuple(l)
    def __iter__(self):
        return (i for i in self._t)
    def __add__(self, other):
        return V(map(operator.add, self._t, other._t))
    def __sub__(self, other):
        return V(map(operator.sub, self._t, other._t))
    def __mul__(self, other): #Scalar multiplication or dot product (cross products not supported).
        if type(other) == type(self):
            return sum(map(operator.mul, self._t, other._t))
        else:
            return V(map(operator.mul, self._t, (other,)*self._d))
    def __div__(self, other):
        return V(map(operator.div, self._t, (other,)*self._d))
    def __truediv__(self, other):
        return V(map(operator.truediv, self._t, (other,)*self._d))
    def __mod__(self, other):
        return V(map(operator.mod, self._t, (other,)*self._d))
    def __neg__(self):
        return V(map(operator.neg, self._t))
    '''def __concat__(self, other):
        return V(self._t+other._t)'''
    def __abs__(self):
        return sum(map(operator.mul, self._t, self._t))**0.5

class Obj:
    def __init__(self, x, v, a, disp=None):
        self.x = x
        self.v = v
        self.a = a
        self.visible = disp is not None
        if self.visible:
            self.disp = disp
    def tick(self, dt, n):
        for i in xrange(n):
            self.v += self.a*dt
            self.x += self.v*dt
        if self.visible:
            self.disp.objsToDisp.append(self)
    '''def handlecoll(self, other):
        pass'''
    def jerk(self, j, dt):
        self.a += j*dt
    def getSymbol(self):
        return "?"

class Disp:
    def __init__(self, x_ul, xres):
        self.objsToDisp = []
        self.x = x_ul
        self.xres = xres
        self.yres = xres/XRES_OVER_YRES
    def display(self):
        disp = [[" " for i in xrange(ARRAY_SIZE[0])] for j in xrange(ARRAY_SIZE[1])]
        for obj in self.objsToDisp:
            x_obj = obj.x
            s = obj.getSymbol()
            disp[int(x_obj[1]/self.yres)][int(x_obj[0]/self.xres)] = s
        #Print display and then back up cursor to (0,0)
        print("\n".join(["".join(i) for i in disp]), end="\r"+"\x1b[A"*(len(disp)-1))
        self.objsToDisp = []

'''
class Collision:
    def __init__(self, t1, t2, d):
        self.t1 = t1
        self.t2 = t2
        d[(t1,t2)] = self
    def __call__(self, obj1, obj2):
        return self.collide(obj1, obj2)
    def collide(self, obj1, obj2):
        pass
class Physics:
    def __init__(self):
        self.display = Disp(V(0,0),1)
        self.objects = []'''
        
#A demonstration of the non-intuitive nature of "trivalent" physics.
#In normal "bivalent" physics, this would result in a conic orbit.
#Best viewed with a terminal sized at at least 100 x 51.
d = Disp(V(0,0),1)
q = Obj(V(0,25),V(0,-3),V(0,0),d)
z = Obj(V(15,25),V(0,0),V(0,0),d)
t = 0.1
for i in xrange(int(15/t)):
    q.jerk((z.x-q.x)/abs(z.x-q.x)**3*60, t)
    q.tick(t, not not i)
    z.tick(t, not not i)
    d.display()
    sleep(t)