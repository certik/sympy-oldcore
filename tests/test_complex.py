import sys
sys.path.append(".")

from sympy import Rational, Symbol, I, sin, cos, exp

def test_complex():
    a=Symbol("a")
    b=Symbol("b")
    e=(a+I*b)*(a-I*b)
    assert e.expand() == a**2+b**2
    assert e.expand() != a**2-b**2

    assert (a+I*b).conjugate() !=  a+I*b
    assert (a+I*b).conjugate() ==  a-I*b

    assert str(abs(a))=="abs(a)"

def test_abs1():
    a=Symbol("a", real=True)
    b=Symbol("b", real=True)
    assert abs(a) == a
    assert abs(-a) == a
    assert abs(-a) != -a
    assert abs(a+I*b) == (a*a+b*b).sqrt()

def test_abs2():
    a=Symbol("a", real=False)
    b=Symbol("b", real=False)
    assert abs(a) != a
    assert abs(-a) != a
    assert abs(a+I*b) != (a*a+b*b).sqrt()

def test_evalc():
    x=Symbol("x", real=True)
    y=Symbol("y", real=True)
    assert ((x+I*y)**2).evalc() == x**2+2*I*x*y - y**2

    assert exp(I*x) != cos(x)+I*sin(x)
    assert exp(I*x).evalc() == cos(x)+I*sin(x)

    assert exp(I*x+y).evalc() == exp(y)*cos(x)+I*sin(x)*exp(y)

    assert sin(I*x).evalc() == I * (exp(x)-exp(-x))/2
    assert sin(x+I*y).evalc() == sin(x)*(exp(y)+exp(-y))/2 + \
            I * (exp(y)-exp(-y))/2 * cos(x)

    assert cos(I*x).evalc() == (exp(x)+exp(-x))/2
    assert cos(x+I*y).evalc() == cos(x)*(exp(y)+exp(-y))/2 - \
            I * (exp(y)-exp(-y))/2 * sin(x)
