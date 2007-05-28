from sympy import Basic, Rational, Symbol, oo
from sympy.modules.simplify import simplify
from entity import GeometryEntity
from point import Point

class LinearEntity(GeometryEntity):
    """A linear entity (line, ray, segment, etc) in space."""
    def __init__(self, p1, p2, **kwargs):
        GeometryEntity.__init__(self, [p1, p2], **kwargs)
        if not isinstance(p1, Point) or not isinstance(p2, Point):
            raise TypeError("__init__ requires Point instances")
        if p1 == p2:
            raise RuntimeError("__init__ requires two distinct points")
        self._p1 = p1
        self._p2 = p2

    def _coeffs(self):
        """Returns the coefficients (a,b,c) for equation ax+by+c=0"""
        return (self._p1[1]-self._p2[1],
                self._p2[0]-self._p1[0],
                self._p1[0]*self._p2[1] - self._p1[1]*self._p2[0])

    @staticmethod
    def are_concurrent(*args):
        """Returns True if the set of lines are concurrent, False otherwise"""
        _args = args
        args = GeometryEntity._normalize_args(args)

        # Concurrency requires intersection at a single point. One line
        # cannot be concurrent, nor can overlapping lines.
        if len(args) <= 1 or len(args) != len(_args):
            return False

        try:
            # Get the intersection (if parallel)
            p = GeometryEntity.do_intersection(args[0], args[1])
            if p is None: return False

            # Make sure the intersection is on every line
            for ind in xrange(2, len(args)):
                if p[0] not in args[ind]:
                    return False
            return True
        except AttributeError:
            return False

    @staticmethod
    def are_parallel(l1, l2):
        """Returns True if l1 and l2 are parallel, False otherwise"""
        try:
            a1,b1,c1 = l1._coeffs()
            a2,b2,c2 = l2._coeffs()
            return bool(simplify(a1*b2 - b1*a2) == 0)
        except AttributeError:
            return False

    @staticmethod
    def are_perpendicular(l1, l2):
        """Returns True if l1 and l2 are perpendicular, False otherwise"""
        try:
            a1,b1,c1 = l1._coeffs()
            a2,b2,c2 = l2._coeffs()
            return bool(simplify(a1*a2 + b1*b2) == 0)
        except AttributeError:
            return False

    @staticmethod
    def angles(l1, l2):
        """Returns the two angles formed between these lines."""
        return None

    def parallel_line(self, p):
        """
        Returns a new Line which is parallel to this line and passes through
        the specified point.
        """
        d1 = self._p1[0] - self._p2[0]
        d2 = self._p1[1] - self._p2[1]
        p2 = Point(p[0] + d1, p[1] + d2)
        return Line(p, p2)

    def perpendicular_line(self, p):
        """
        Returns a new Line which is perpendicular to this line and passes
        through the specified point.
        """
        d1 = self._p1[0] - self._p2[0]
        d2 = self._p1[1] - self._p2[1]
        if d2 == 0: # If an horizontal line
            if p[1] == self._p1[1]: # if p is on this line
                p2 = Point(p[0], p[1] + Rational(1))
                return Line(p, p2)
            else:
                p2 = Point(p[0], self._p1[1])
                return Line(p, p2)
        else:
            p2 = Point(p[0] - d2, p[1] + d1)
            return Line(p, p2)

    def perpendicular_segment(self, p):
        """
        Returns a new Segment which connects p to a point on this line
        and is also perpendicular to this line. Returns None if p is on
        this line.
        """
        if p in self:
            return None
        pl = self.perpendicular_line(p)
        p2 = GeometryEntity.do_intersection(self, pl)[0]
        return Segment(p, p2)

    def projection(self, o):
        """Project a point, ray, or segment onto this line."""
        def project(p):
            """Projects a point onto self."""
            if p in self: return p
            l1 = self.perpendicular_line(p)
            return self.intersection(l1)[0]

        if isinstance(o, Point):
            return project(o)
        elif isinstance(o, (Ray, Segment)):
            n_p1 = project(o._p1)
            n_p2 = project(o._p2)
            if n_p1 == n_p2:
                return n_p1
            else:
                return (type(o))(n_p1, n_p2)
        else:
            raise ValueError("Line.projection accepts only Point, Ray, or Segment")

    @property
    def slope(self):
        """Returns the slope of this line, or sympy.oo (infinity) if vertical."""
        d1 = self._p1[0] - self._p2[0]
        d2 = self._p1[1] - self._p2[1]
        if d1 == Rational(0):
            return oo
        elif isinstance(d1, int) and isinstance(d2, int):
            return Rational(d2, d1)
        else:
            return d2/d1

    @property
    def points(self):
        """Get the two points used to define this linear entity."""
        return (self._p1, self._p2)

    def intersection(self, o):
        if isinstance(o, Point):
            if o in self:
                return [o]
            else:
                return None
        elif isinstance(o, LinearEntity):
            a1,b1,c1 = self._coeffs()
            a2,b2,c2 = o._coeffs()
            t = simplify(a1*b2 - a2*b1)
            if t == 0: # are parallel?
                if self == o:
                    return [o]
                else:
                    return None
            px = simplify((b1*c2 - c1*b2) / t)
            py = simplify((a2*c1 - a1*c2) / t)
            inter = Point(px, py)
            if inter in self and inter in o:
                return [inter]
            return None
        else:
            raise NotImplementedError()

    def __str__(self):
        n = type(self).__name__
        return "%s(%s, %s)" % (n, str(self._p1), str(self._p2))


class Line(LinearEntity):
    """A line in space."""

    def arbitrary_point(self, parameter_name='t'):
        """Returns a symbolic point that is on this line."""
        t = Symbol(parameter_name)
        if self.slope == oo:
            return Point(self._p1[0], t)
        else:
            x = simplify(self._p1[0] + t*(self._p2[0] - self._p1[0]))
            y = simplify(self._p1[1] + t*(self._p2[1] - self._p1[1]))
            return Point(x, y)

    def random_point(self):
        """Returns a random point on this line."""
        from random import randint
        from sys import maxint
        t = Symbol('t')
        p = self.arbitrary_point('t')
        subs_val = randint(-maxint-1, maxint)
        return Point(p[0].subs(t, subs_val), p[1].subs(t, subs_val))

    def equation(self, xaxis_name='x', yaxis_name='y'):
        """Returns the equation for this line"""
        x = Symbol(xaxis_name)
        y = Symbol(yaxis_name)
        a,b,c = self._coeffs()
        #return simplify(a*x + b*y + c)
        return a*x + b*y + c

    def __contains__(self, o):
        if isinstance(o, Line):
            return self.__eq__(o)
        elif isinstance(o, Point):
            x = Symbol('x')
            y = Symbol('y')
            r = self.equation().subs_dict({x: o[0], y: o[1]})
            x = simplify(r)
            return bool(x == 0)
        else:
            return False

    def __eq__(self, o):
        if not isinstance(o, Line): return False
        return Point.are_collinear(self._p1, self._p2, o._p1, o._p2)


class Ray(LinearEntity):
    """A ray in space."""

    def projection(self, o):
        """
        Project a point or segment onto this ray and return it, or None if
        it is impossible to do.
        """
        res = LinearEntity.projection(self, o)
        if res in self:
            return res
        else:
            return None

    def random_point(self):
        """Returns a random point on this ray."""
        from random import randint
        from sys import maxint
        if self.slope == oo:
            x = self._p1[0]
            y = randint(self._p1[1], maxint)
        else:
            lower,upper = -maxint-1,maxint
            # TODO Avoid using < and >
            if self._p1[0] < self._p2[0]:
                lower = self._p1[0]
            else:
                upper = self._p1[0]

            a,b,c = self._coeffs()
            x = simplify( randint(lower, upper) )
            y = simplify( (-c - a*x) / b )
        return Point(x, y)

    #def intersection(self, o):
    #    s = LinearEntity.intersection(self, o)
    #    if s is None:
    #        return None
    #    elif s[0] in self:
    #        return s
    #    else:
    #        return None

    def __eq__(self, o):
        if not isinstance(o, Ray):
            return False
        return ((self._p1 == o._p1) and (o._p2 in self))

    def __contains__(self, o):
        if isinstance(o, Ray):
            d = o._p2 - o._p1
            return ((o._p1 in self) and d[0])
        elif isinstance(o, Segment):
            return ((o._p1 in self) and (o._p2 in self))
        elif isinstance(o, Point):
            if Point.are_collinear(self._p1, self._p2, o):
                return True
                # Ignore comparisons for now, symbolic stuff might cause issues
                #if self._p1[0] == self._p2[0]:
                #    if self._p1[1] < self._p2[1]:
                #        return o[1] >= self._p1[1]
                #    else:
                #        return o[1] <= self._p1[1]
                #elif self._p1[0] <= self._p2[0]:
                #    return o[0] >= self._p1[0]
                #else:
                #    return o[0] <= self._p1[0]
            else:
                return False
        else:
            return False

    def __str__(self):
        return "Ray(%s, %s)" % (str(self._p1), str(self._p2))

class Segment(LinearEntity):
    """A line segment in space."""

    def projection(self, o):
        """Project a point onto this ray and return it, or None if impossible."""
        res = LinearEntity.projection(self, o)
        if res in self:
            return res
        else:
            return None

    def random_point(self):
        """Returns a random point on this segment."""
        from random import randint
        from sys import maxint
        if self.slope == oo:
            x = self._p1[0]
            y = randint(self._p1[1], self._p2[1])
        else:
            a,b,c = self._coeffs()
            x = simplify( randint(self._p1[0], self._p2[0]) )
            y = simplify( (-c - a*x) / b )
        return Point(x, y)

    #def intersection(self, o):
    #    s = LinearEntity.intersection(self, o)
    #    if s is None:
    #        return None
    #    elif s[0] in self:
    #        return s
    #    else:
    #        return None

    def perpendicular_bisector(self, p=None):
        """
        Returns the perpendicular bisector of this segment. If no point is
        specified then a Line instance is returned. If a Point is given then
        a segment is returned joining it and the midpoint of this segment.
        """
        if p is None:
            return LinearEntity.perpendicular_line(self, self.midpoint)
        else:
            l = LinearEntity.perpendicular_line(self, self.midpoint)
            if p in l:
                return Segment(self.midpoint, p)
            else:
                return None

    @property
    def length(self):
        """Returns the length of this segment."""
        return Point.distance(self._p1, self._p2)

    @property
    def midpoint(self):
        """Returns the midpoint of this segment."""
        return Point.midpoint(self._p1, self._p2)

    def __len__(self, ind):
        return 2

    def __getitem__(self, ind):
        return (self._p1, self._p2)[ind]

    def __eq__(self, o):
        try:
            if not isinstance(o, Segment):
                return False
            return ((self._p1 == o._p1) and (self._p2 == o._p2)) or \
                   ((self._p1 == o._p2) and (self._p2 == o._p1))
        except AttributeError:
            return False

    def __contains__(self, o):
        if isinstance(o, Segment):
            return ((o._p1 in self) and (o._p2 in self))
        elif isinstance(o, Point):
            if Point.are_collinear(self._p1, self._p2, o):
                return True
                #x1,x2 = self._p1[0], self._p2[0]
                #return (min(x1,x2) <= o[0] <= max(x1,x2))
            else:
                return False
        else:
            return False

    def __str__(self):
        return "Segment(%s, %s)" % (str(self._p1), str(self._p2))