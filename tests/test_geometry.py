import sys
sys.path.append(".")

from sympy import *
import sympy.modules.geometry as g

x = Symbol('x')
y = Symbol('y')
x1 = Symbol('x1')
x2 = Symbol('x2')
y1 = Symbol('y1')
y2 = Symbol('y2')
half = Rational(1,2)

def xtest_point():
    p1 = g.Point(x1, x2)
    p2 = g.Point(y1, y2)
    p3 = g.Point(0, 0)
    p4 = g.Point(1, 1)

    assert len(p1) == 2
    assert p2[1] == y2
    assert (p3+p4) == p4
    assert (p2-p1) == g.Point(y1-x1, y2-x2)
    assert p4*5 == g.Point(5, 5)
    assert -p2 == g.Point(-y1, -y2)

    assert g.Point.midpoint(p3, p4) == g.Point(half, half)
    assert g.Point.midpoint(p1, p4) == g.Point(half + half*x1, half + half*x2)
    assert g.Point.midpoint(p2, p2) == p2

    assert g.Point.distance(p3, p4) == sqrt(2)
    assert g.Point.distance(p1, p2) == simplify(sqrt((x1-y1)**2 + (x2-y2)**2))
    assert g.Point.distance(p1, p1) == 0
    assert g.Point.distance(p3, p2) == abs(p2)

    p1_1 = g.Point(x1, x1)
    p1_2 = g.Point(y2, y2)
    p1_3 = g.Point(x1 + 1, x1)
    assert g.Point.are_collinear(p3)
    assert g.Point.are_collinear(p3, p4)
    assert g.Point.are_collinear(p3, p4, p1_1, p1_2)
    assert g.Point.are_collinear(p3, p4, p1_1, p1_3) is False

    p2_1 = g.Point(x1, 0)
    p2_2 = g.Point(0, x1)
    p2_3 = g.Point(-x1, 0)
    p2_4 = g.Point(0, -x1)
    p2_5 = g.Point(x1, 5)
    assert g.Point.are_concyclic(p2_1)
    assert g.Point.are_concyclic(p2_1, p2_2)
    assert g.Point.are_concyclic(p2_1, p2_2, p2_3, p2_4)
    assert g.Point.are_concyclic(p2_1, p2_2, p2_3, p2_5) is False

def xtest_line():
    p1 = g.Point(0, 0)
    p2 = g.Point(1, 1)
    p3 = g.Point(x1, x1)
    p4 = g.Point(y1, y1)
    p5 = g.Point(x1, 1 + x1)

    l1 = g.Line(p1, p2)
    l2 = g.Line(p3, p4)
    l3 = g.Line(p3, p5)

    # Basic stuff
    assert g.Line(p1, p2) == g.Line(p2, p1)
    assert l1 == l2
    assert l1 != l3
    assert l1.slope == 1
    assert l3.slope == oo
    assert p1 in l1 # is p1 on the line l1?
    assert p1 not in l3

    assert simplify(l1.equation()) in (x-y, y-x)
    assert simplify(l3.equation()) in (x-x1, x1-x)

    assert l2.arbitrary_point() in l2
    for ind in xrange(0, 5):
        assert l3.random_point() in l3

    # Orthogonality
    p1_1 = g.Point(-x1, x1)
    l1_1 = g.Line(p1, p1_1)
    assert l1.perpendicular_line(p1) == l1_1
    assert g.LinearEntity.are_perpendicular(l1, l1_1)
    assert g.LinearEntity.are_perpendicular(l1 , l2) is False

    # Parallelity
    p2_1 = g.Point(-2*x1, 0)
    l2_1 = g.Line(p3, p5)
    assert l2.parallel_line(p1_1) == g.Line(p2_1, p1_1)
    assert l2_1.parallel_line(p1) == g.Line(p1, g.Point(0, 2))
    assert g.LinearEntity.are_parallel(l1, l2)
    assert g.LinearEntity.are_parallel(l2, l3) is False
    assert g.LinearEntity.are_parallel(l2, l2.parallel_line(p1_1))
    assert g.LinearEntity.are_parallel(l2_1, l2_1.parallel_line(p1))

    # Intersection
    assert g.intersection(l1, p1) == [p1]
    assert g.intersection(l1, p5) is None
    assert g.intersection(l1, l2) == [l1]
    assert g.intersection(l1, l1.parallel_line(p5)) is None

    # Concurrency
    l3_1 = g.Line(g.Point(5, x1), g.Point(-Rational(3,5), x1))
    assert g.LinearEntity.are_concurrent(l1, l3)
    assert g.LinearEntity.are_concurrent(l1, l3, l3_1)
    assert g.LinearEntity.are_concurrent(l1, l1_1, l3) is False

    # Projection
    assert l2.projection(p4) == p4
    assert l1.projection(p1_1) == p1
    assert l3.projection(p2) == g.Point(x1, 1)

    # TODO Finding angles


    # Testing Rays and Segments (very similar to Lines)
    r1 = g.Ray(p1, g.Point(-1, 5))
    r2 = g.Ray(p1, g.Point(-1, 1))
    r3 = g.Ray(p3, p5)
    assert l1.projection(r1) == g.Ray(p1, p2)
    assert l1.projection(r2) == p1
    assert r3 != r1

    s1 = g.Segment(p1, p2)
    s2 = g.Segment(p1, p1_1)
    assert s1.midpoint == g.Point(Rational(1,2), Rational(1,2))
    assert s2.length == sqrt( 2*(x1**2) )
    assert s1.perpendicular_bisector() == g.Line(g.Point(0, 1), g.Point(1, 0))

def xtest_ellipse():
    p1 = g.Point(0, 0)
    p2 = g.Point(1, 1)
    p3 = g.Point(x1, x2)
    p4 = g.Point(0, 1)
    p5 = g.Point(-1, 0)

    e1 = g.Ellipse(p1, 1, 1)
    e2 = g.Ellipse(p2, half, 1)
    e3 = g.Ellipse(p1, y1, y1)
    c1 = g.Circle(p1, 1)

    # Basic Stuff
    assert e1 == c1
    assert e1 != e2
    assert p4 in e1
    assert p2 not in e2
    assert e1.area == pi
    assert e2.area == pi/2
    assert e3.area == pi*(y1**2)
    assert c1.area == e1.area
    assert c1.circumference == 2*pi

    # XXX Requires trig simplification (i.e., sin(x)**2 + cos(x)**2 = 1)
    #assert e2.arbitrary_point() in e2
    #for ind in xrange(0, 5):
    #    assert e3.random_point() in e3

    # Tangents
    v = sqrt(2) / 2
    p1_1 = g.Point(v, v)
    p1_2 = p2 + g.Point(half, 0)
    p1_3 = p2 + g.Point(0, 1)
    assert e1.tangent_line(p4) == c1.tangent_line(p4)
    assert e2.tangent_line(p1_2) == g.Line(p1_2, p2 + g.Point(half, 1))
    assert e2.tangent_line(p1_3) == g.Line(p1_3, p2 + g.Point(half, 1))
    assert c1.tangent_line(p1_1) == g.Line(p1_1, g.Point(0, sqrt(2)))
    assert e2.is_tangent(g.Line(p1_2, p2 + g.Point(half, 1)))
    assert e2.is_tangent(g.Line(p1_3, p2 + g.Point(half, 1)))
    assert c1.is_tangent(g.Line(p1_1, g.Point(0, sqrt(2))))
    assert e1.is_tangent(g.Line(g.Point(0, 0), g.Point(1, 1))) is False

    # Intersection
    l1 = g.Line(g.Point(1, -5), g.Point(1, 5))
    l2 = g.Line(g.Point(-5, -1), g.Point(5, -1))
    l3 = g.Line(g.Point(-1, -1), g.Point(1, 1))
    l4 = g.Line(g.Point(-10, 0), g.Point(0, 10))
    pts_c1_l3 = [g.Point(sqrt(2)/2, sqrt(2)/2), g.Point(-sqrt(2)/2, -sqrt(2)/2)]

    assert g.intersection(e2, l4) is None
    assert g.intersection(c1, g.Point(1, 0)) == [g.Point(1, 0)]
    assert g.intersection(c1, l1) == [g.Point(1, 0)]
    assert g.intersection(c1, l2) == [g.Point(0, -1)]
    # Requires simplification of square roots [ sqrt(8) == 2sqrt(2) ]
    #assert g.intersection(c1, l3) in [pts_c1_l3, [pts_c1_l3[1], pts_c1_l3[0]]]

    e1 = g.Circle(g.Point(0, 0), 5)
    e2 = g.Ellipse(g.Point(0, 0), 5, 20)
    assert g.intersection(e1, e2) in \
        [[g.Point(5, 0), g.Point(-5, 0)], [g.Point(-5, 0), g.Point(5, 0)]]

    # Combinations of above
    assert e3.is_tangent(e3.tangent_line(p1 + g.Point(y1, 0)))

def xtest_polygon():
    p1 = g.Polygon(
        g.Point(0, 0), g.Point(3,-1),
        g.Point(6, 0), g.Point(4, 5),
        g.Point(2, 3), g.Point(0, 3))
    p2 = g.Polygon(
        g.Point(6, 0), g.Point(3,-1),
        g.Point(0, 0), g.Point(0, 3),
        g.Point(2, 3), g.Point(4, 5))

    #
    # General polygon
    #
    assert p1 == p2
    assert len(p1) == Rational(6)
    assert len(p1.sides) == 6
    assert p1.perimeter == 5+2*sqrt(10)+sqrt(29)+sqrt(8)
    assert p1.area == 22

    #
    # Regular polygon
    #
    p1 = g.RegularPolygon(g.Point(0, 0), 10, 5)
    p2 = g.RegularPolygon(g.Point(0, 0), 5, 5)

    assert p1 != p2
    assert p1.interior_angle == 3*pi/5
    assert p1.exterior_angle == 2*pi/5
    assert p2.apothem == 5*cos(pi/5)
    assert p2.circumcircle == g.Circle(g.Point(0, 0), 5)
    assert p2.incircle == g.Circle(g.Point(0, 0), p2.apothem)

    #
    # Triangle
    #
    five = Rational(5)
    p1 = g.Point(0, 0)
    p2 = g.Point(5, 0)
    p3 = g.Point(0, 5)
    t1 = g.Triangle(p1, p2, p3)
    t2 = g.Triangle(p1, p2, g.Point(Rational(5,2), sqrt(Rational(75,4))))
    t3 = g.Triangle(p1, g.Point(x1, 0), g.Point(0, x1))
    s1 = t1.sides
    s2 = t2.sides
    s3 = t3.sides

    # Basic stuff
    assert t1.area == Rational(25,2)
    assert t1.is_right()
    assert t2.is_right() is False
    assert t3.is_right()
    assert p1 in t1
    assert g.Point(five, five) not in t2

    assert t1.is_equilateral() is False
    assert t2.is_equilateral()
    assert t3.is_equilateral() is False
    assert g.Triangle.are_similar(t1, t2) is False
    assert g.Triangle.are_similar(t1, t3)
    assert g.Triangle.are_similar(t2, t3) is False

    # Bisectors
    #XXX Requires proper simplification of radicals
    #bisectors = t1.bisectors
    #assert bisectors[p1] == g.Segment(p1, g.Point(Rational(5,2), Rational(5,2)))
    ic = Rational(25) / (Rational(10) + sqrt(50))
    assert t1.incenter == g.Point(ic, ic)

    # Medians
    assert t1.medians[p1] == g.Segment(p1, g.Point(Rational(5,2), Rational(5,2)))
    assert t3.medians[p1] == g.Segment(p1, g.Point(x1/2, x1/2))

    # Perpendicular
    altitudes = t1.altitudes
    assert altitudes[p1] == g.Segment(p1, g.Point(Rational(5,2), Rational(5,2)))
    assert altitudes[p2] == s1[0]
    assert altitudes[p3] == s1[2]

    #
    # Combinations of things
    #
    #XXX Requires proper simplification of radicals
    #assert len(g.intersection(t1.bisectors[p1], t1.bisectors[p2])) == 1
    assert len(g.intersection(t1.altitudes[p1], t1.altitudes[p2])) == 1
    assert len(g.intersection(t1.medians[p1], t1.medians[p2])) == 1

def xtest_util():
    p = [g.Point(-5,-1), g.Point(-2,1), g.Point(-2,-1), g.Point(-1,-3), g.Point(0,0),
         g.Point(1,1), g.Point(2,2), g.Point(2,-1), g.Point(3,1), g.Point(4,-1), g.Point(6,2)]
    ch = g.Polygon(p[0], p[3], p[9], p[10], p[6], p[1])
    assert g.convex_hull(p) == ch

if __name__ == "__main__":
    from sys import modules,stderr,exc_info,excepthook
    import hotshot, hotshot.stats

    curr_module = modules[__name__]
    for member in dir(curr_module):
        if member.startswith("test_"):
            try:
                sys.stderr.write("Testing %s..." % member)
                curr_module.__dict__[member]()
                sys.stderr.write("SUCCESS!\n")
            except AssertionError, e:
                sys.stderr.write("FAILED!\n")
                sys.stderr.write('-' * 25 + '\n')
                excepthook(*exc_info())
                sys.stderr.write('-' * 25 + '\n')
