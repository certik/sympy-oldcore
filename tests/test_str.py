import sys
sys.path.append(".")

import sympy as g
from sympy import Symbol, Rational, Derivative, sqrt, exp

from sympy.core.stringPict import *

x = g.Symbol('x')
y = g.Symbol('y')
z = g.Symbol('z')
w = g.Symbol('w')

def test_poly_str():
    #if any of these tests fails, it can still be correct, just the terms can
    #be in a different order. That happens for example when we change the 
    #hash algorithm. If it is correct, just add another item in the list [] of
    #correct results.
    assert str((2*x-(7*x**2 - 2) + 3*y)) in ["2*x-(-2+7*x**2)+3*y",
            "-(-2+7*x**2)+2*x+3*y", "3*y-(-2+7*x**2)+2*x", "-(-2+7*x**2)+3*y+2*x",
            "2*x+3*y-(-2+7*x**2)", "3*y+2*x-(-2+7*x**2)"]
    assert str(x-y) in ["x-y", "-y+x"]
    assert str(2+-x) == "2-x"
    assert str(x-2) in ["x-2","-2+x"]
    assert str(x-y-z-w) in ["x-y-z-w","-w-y-z+x","x-w-y-z", "-w+x-y-z", "-z-w-y+x"]
    assert str(x-y-z-w) in ["-w-y-z+x","x-w-y-z","-w+x-z-y",
            "-y-w-z+x","-y+x-z-w","-y+x-w-z", "-w+x-y-z", "-z-w-y+x"]
    assert str(x-z*y**2*z*w) in ["-z**2*y**2*w+x", "x-w*y**2*z**2",
            "-y**2*z**2*w+x","x-w*z**2*y**2","x-y**2*z**2*w","x-y**2*w*z**2",
            "x-z**2*y**2*w", "-w*z**2*y**2+x", "-w*y**2*z**2+x"]

def test_bug1():
    e=(x-1*y*x*y)
    #this raised an exception (both lines are needed)
    a=str(e)
    a=str(e.eval())

def test_bug2():
    e=x-y
    a=str(e)
    b=str(e)
    assert a==b

def test_bug3():
    x = Symbol("x")
    e = sqrt(x)
    assert str(e) == "x**(1/2)"

def test_bug4():
    x=Symbol("x")
    w=Symbol("w")
    e=-2*sqrt(x)-w/sqrt(x)/2
    assert str(e) not in ["(-2)*x**1/2(-1/2)*x**(-1/2)*w",
            "-2*x**1/2(-1/2)*x**(-1/2)*w","-2*x**1/2-1/2*x**-1/2*w"]
    assert str(e) in ["-2*x**(1/2)-1/2*x**(-1/2)*w", "-2*x**(1/2)-1/2*w*x**(-1/2)", 
                      "-1/2*x**(-1/2)*w-2*x**(1/2)", "-1/2*w*x**(-1/2)-2*x**(1/2)"]

def test_bug5():
    x=Symbol("x")
    e=1/x
    assert str(e) != "x**-1"
    assert str(e) == "x**(-1)"

def test_Derivative():
    x = Symbol("x")
    e = Derivative(x**2, x)
    assert str(e) == "(x**2)'"
    
def test_pretty_print():
    assert str( (x**2).pretty() ) == ' 2\nx '
    assert str( (x**2 + x + 1).pretty( )) in ['     2\n1+x+x ']
    assert str( (2*x + exp(x)).pretty() ) in ['     x\n2*x+e ']
    
