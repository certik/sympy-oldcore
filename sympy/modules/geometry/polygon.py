from sympy import Basic, Rational, Symbol, cos, sin, pi
from sympy.modules.simplify import simplify
from entity import GeometryEntity
from point import Point
from ellipse import Circle
from line import Line, Segment


class Polygon(GeometryEntity):
    """A simple polygon in space."""
    def __init__(self, *args, **kwargs):
        GeometryEntity.__init__(self, *args, **kwargs)
        if not isinstance(args[0], Point):
            self._vertices = tuple(args[0])
        else:
            self._vertices = tuple(args)

        for p in self._vertices:
            if not isinstance(p, Point):
                raise TypeError("__init__ requires Point instances")

        if len(self._vertices) < 3:
            raise RuntimeError("A polygon must have at least three points")

    @property
    def area(self):
        """Returns the area of the polygon."""
        area = 0
        for ind in xrange(0, len(self._vertices)-1):
            pi = self._vertices[ind]
            pii = self._vertices[ind+1]
            area += pi[0]*pii[1]-pii[0]*pi[1]
        return simplify(area) / Rational(2)

    @property
    def angles(self):
        """
        Returns a dictionary of {point: angle} entries containing the
        measure of all the internal angle of this polygon at each vertex.
        """
        def tarea(a, b, c):
            return (b[0] - a[0])*(c[1] - a[1]) - (c[0] - a[0])*(b[1] - a[1])

        def isright(a, b, c):
            return (tarea(a, b, c) <= 0)

        # Determine orientation of points
        cw = True
        if not isright(self._vertices[-1], self._vertices[0], self._vertices[1]):
            cw = False

        ret = {}
        if cw:
            for i in xrange(0, len(self._vertices)):
                a,b,c = self._vertices[i-2], self._vertices[i-1], self._vertices[i]
                ang = Line.angle_between(Line(b, a), Line(b, c))
                if not isright(a, b, c):
                    ret[b] = 360 - ang
                else:
                    ret[b] = ang
        else:
            for i in xrange(0, len(self._vertices)):
                a,b,c = self._vertices[i-2], self._vertices[i-1], self._vertices[i]
                ang = Line.angle_between(Line(b, a), Line(b, c))
                if isright(a, b, c):
                    ret[b] = 360 - ang
                else:
                    ret[b] = ang
        return ret

    @property
    def perimeter(self):
        """Returns the perimeter of the polygon."""
        p = 0
        for ind in xrange(-1, len(self._vertices)-1):
            p += Point.distance(self._vertices[ind], self._vertices[ind+1])
        return simplify(p)

    @property
    def vertices(self):
        """Returns the vertices that define the polygon."""
        return self._vertices

    @property
    def centroid(self):
        """Returns the centroid of the polygon."""
        # TODO Double check this formula
        x = Rational(0)
        y = Rational(0)
        n = len(self._points)
        for p in self._vertices:
            x += p[0]
            y += p[1]
        x = simplify(x/n)
        y = simplify(y/n)
        return Point(x, y)

    @property
    def sides(self):
        """Returns a list of the sides."""
        res = []
        for ind in xrange(0, len(self._vertices)-1):
            res.append( Segment(self._vertices[ind], self._vertices[ind+1]) )
        res.append( Segment(self._vertices[-1], self._vertices[0]) )
        return res

    def is_convex(self):
        """Returns True if this polygon is convex, False otherwise."""
        #XXX Should we override this in RegularPoygon and Triangle since they
        #    are never convex (if the tiny performance boost is important)
        def tarea(a, b, c):
            return (b[0] - a[0])*(c[1] - a[1]) - (c[0] - a[0])*(b[1] - a[1])

        def isright(a, b, c):
            return (tarea(a, b, c) <= 0)

        # Determine orientation of points
        cw = True
        if not isright(self._vertices[-2], self._vertices[-1], self._vertices[0]):
            cw = False

        if cw:
            for i in xrange(0, len(self._vertices)):
                if not isright(self._vertices[i-2], self._vertices[i-1], self._vertices[i]):
                    return False
        else:
            for i in xrange(0, len(self._vertices)):
                if isright(self._vertices[i-2], self._vertices[i-1], self._vertices[i]):
                    return False
        return True

    def _intersection(self, o):
        res = []
        for side in self.sides:
            inter = GeometryEntity.do_intersection(side, o)
            if inter is not None:
                res.extend(inter)
        return res

    def __len__(self):
        return len(self._vertices)

    def __getitem__(self, ind):
        return self._vertices[ind]

    def __eq__(self, o):
        if not isinstance(o, Polygon):
            return False

        # Find index of the first point that is the same
        n1,n2 = len(self._vertices), len(o._vertices)
        start_indices = []
        for ind in xrange(0, n1):
            if self._vertices[ind] == o._vertices[0]:
                start_indices.append(ind)

        if len(start_indices) == 0:
            return False

        # Check vertices
        imax = max(n1, n2)
        for start_ind in start_indices:
            i = start_ind

            # Check to see what orientation we should check
            dir = 0
            if self._vertices[(i + 1) % n1] == o._vertices[1]:
                dir = 1
            elif self._vertices[(i - 1) % n1] == o._vertices[1]:
                dir = -1

            # If either point to the left or right if the first point
            # is value (i.e., dir is nonzero) then check in that direction
            if dir != 0:
                areEqual = True
                for ind in xrange(2, imax):
                    if self._vertices[(i + dir*ind) % n1] != o._vertices[ind % n2]:
                        areEqual = False
                        break
                if areEqual: return True

        return False

    def __contains__(self, o):
        if isinstance(o, Polygon):
            return self == o
        elif isinstance(o, Segment):
            return o in self.sides
        elif isinstance(o, Point):
            if o in self._vertices:
                return True
            for side in self.sides:
                if o in side:
                    return True
            return False
        else:
            return False

    def __str__(self):
        return "Polygon(%d sides)" % (len(self._vertices)-1)


class RegularPolygon(Polygon):
    """A regular polygon."""
    def __init__(self, c, r, n, **kwargs):
        r = Basic.sympify(r)

        if not isinstance(c, Point):
            raise ValueError("RegularPolygon.__init__ requires c to be a Point instance")

        if not isinstance(r, Basic):
            raise ValueError("RegularPolygon.__init__ requires c to be a number or Basic instance")

        self._c = c
        self._r = r
        points = []
        for k in xrange(0, n):
            points.append( Point(c[0] + r*cos(2*k*pi/n), c[1] + r*sin(2*k*pi/n)) )
        Polygon.__init__(self, points, **kwargs)

    @property
    def center(self):
        """
        Returns the center of the regular polygon (i.e., the center of the
        circumscribing circle).
        """
        return self._c

    @property
    def radius(self):
        """
        Returns the radius of the regular polygon (i.e., the radius of the
        circumscribing circle).
        """
        return self._r

    @property
    def apothem(self):
        """
        Returns the apothem/inradius of the regular polygon (i.e., the
        radius of the inscribed circle).
        """
        n = len(self._vertices)
        return self._r * cos(pi/n)

    @property
    def interior_angle(self):
        """Returns the measure of the interior angles."""
        n = len(self._vertices)
        return (n-2)*pi/n

    @property
    def exterior_angle(self):
        """Returns the measure of the exterior angles."""
        n = len(self._vertices)
        return 2*pi/n

    @property
    def circumcircle(self):
        """Returns a Circle instance describing the circumcircle."""
        return Circle(self._c, self._r)

    @property
    def incircle(self):
        """Returns a Circle instance describing the inscribed circle."""
        return Circle(self._c, self.apothem)

    @property
    def angles(self):
        ret = {}
        ang = self.interior_angle
        for v in self._vertices:
            ret[v] = ang
        return ret

class Triangle(Polygon):
    """A triangle (3 sided polygon)."""

    def __init__(self, *args, **kwargs):
        Polygon.__init__(self, *args, **kwargs)
        if len(self._vertices) != 3:
            raise RuntimeError("A triangle requires exactly 3 points")

    def _is_similar(t1, t2):
        """Returns True if triangles t1 and t2 are similar, False otherwise."""
        if not isinstance(t2, Polygon) or len(t2) != 3:
            return False

        s1_1, s1_2, s1_3 = [side.length for side in t1.sides]
        s2 = [side.length for side in t2.sides]
        def _are_similar(u1, u2, u3, v1, v2, v3):
            e1 = simplify(u1/v1)
            e2 = simplify(u2/v2)
            e3 = simplify(u3/v3)
            return bool(e1 == e2) and bool(e2 == e3)

        # There's only 6 permutations, so write them out
        return _are_similar(s1_1, s1_2, s1_3, *s2) or \
               _are_similar(s1_1, s1_3, s1_2, *s2) or \
               _are_similar(s1_2, s1_1, s1_3, *s2) or \
               _are_similar(s1_2, s1_3, s1_1, *s2) or \
               _are_similar(s1_3, s1_1, s1_2, *s2) or \
               _are_similar(s1_3, s1_2, s1_1, *s2)

    def is_equilateral(self):
        """Returns True if the triangle is equilateral, False otherwise."""
        s = self.sides
        return bool(s[0].length == s[1].length) and bool(s[1].length == s[2].length)

    def is_right(self):
        """Returns True if the triangle is right-angled, False otherwise."""
        #for angle in self.angles:
        #    if angle == pi/2: return True
        #return False
        s = self.sides
        return Segment.is_perpendicular(s[0], s[1]) or \
               Segment.is_perpendicular(s[1], s[2]) or \
               Segment.is_perpendicular(s[0], s[2])

    @property
    def altitudes(self):
        """
        Returns the altitudes of the triangle in a dictionary where the key
        is the vertex and the value is the altitude at that point.
        """
        s = self.sides
        v = self._vertices
        return {v[0]: s[1].perpendicular_segment(v[0]),
                v[1]: s[2].perpendicular_segment(v[1]),
                v[2]: s[0].perpendicular_segment(v[2])}

    @property
    def orthocenter(self):
        """Returns the orthocenter of the triangle."""
        a = self.altitudes
        return GeometryEntity.intersect(a[1], a[2])[0]

    @property
    def circumcenter(self):
        return self.orthocenter

    @property
    def circumradius(self):
        return Point.distance(self.circumcenter, self._vertices[0])

    @property
    def circumcircle(self):
        return Circle(self.circumcenter, self.circumradius)

    @property
    def bisectors(self):
        """
        Returns the bisectors of the triangle in a dictionary where the key
        is the vertex and the value is the bisector at that point.
        """
        s = self.sides
        v = self._vertices
        c = self.incenter
        l1 = Segment(v[0], GeometryEntity.do_intersection(Line(v[0], c), s[1])[0])
        l2 = Segment(v[1], GeometryEntity.do_intersection(Line(v[1], c), s[2])[0])
        l3 = Segment(v[2], GeometryEntity.do_intersection(Line(v[2], c), s[0])[0])
        return {v[0]: l1, v[1]: l2, v[2]: l3}

    @property
    def incenter(self):
        """Returns the incenter of the triangle."""
        s = self.sides
        v = self._vertices
        A,B,C = v[0],v[1],v[2]
        a,b,c = s[1].length,s[2].length,s[0].length
        x = simplify( (a*A[0] + b*B[0] + c*C[0]) / (a+b+c) )
        y = simplify( (a*A[1] + b*B[1] + c*C[1]) / (a+b+c) )
        return Point(x, y)

    @property
    def inradius(self):
        """Returns the inradius of the triangle."""
        return simplify(self.area / self.perimeter)

    @property
    def incircle(self):
        """Returns the incircle of the triangle."""
        return Circle(self.incenter, self.inradius)

    @property
    def medians(self):
        """
        Returns the medians of the triangle in a dictionary where the key
        is the vertex and the value is the median at that point.
        """
        # XXX See Triangle.altitudes for comments on the usage of self.sides 
        s = self.sides
        v = self._vertices
        return {v[0]: Segment(s[1].midpoint, v[0]),
                v[1]: Segment(s[2].midpoint, v[1]),
                v[2]: Segment(s[0].midpoint, v[2])}

    @property
    def medial(self):
        """Returns the medial triangle of the triangle."""
        s = self.sides
        return Triangle(s[0].midpoint, s[1].midpoint, s[2].midpoint)

    @property
    def excircles(self):
        """
        Returns a list of the three excircles for this triangle.
        """
        pass

    def __str__(self):
        fmt_tuple = (str(self._vertices[0]), str(self._vertices[1]), str(self._vertices[2]))
        return "Triangle(%s, %s, %s)" % fmt_tuple