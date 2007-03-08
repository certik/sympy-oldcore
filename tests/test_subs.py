import sys
sys.path.append(".")

import py

import sympy as g

def test_subs():
    n3=g.Rational(3)
    n2=g.Rational(2)
    n6=g.Rational(6)
    x=g.Symbol("x")
    c=g.Symbol("c")
    e=x
    assert str(e) == "x"
    e=e.subs(x,n3)
    assert str(e) == "3"

    e=2*x
    assert e == 2*x
    e=e.subs(x,n3)
    assert str(e) == "6"

    e=(g.sin(x)**2).diff(x)
    assert e == 2*g.sin(x)*g.cos(x)
    e=e.subs(x,n3)
    assert e == 2*g.cos(n3)*g.sin(n3)

    e=(g.sin(x)**2).diff(x)
    assert e == 2*g.sin(x)*g.cos(x)
    e=e.subs(g.sin(x),g.cos(x))
    assert e == 2*g.cos(x)**2

def test_logexppow():
    x=g.Symbol("x")
    w=g.Symbol("dummy :)")
    e=(3**(1+x)+2**(1+x))/(3**x+2**x)
    e=e.eval()
    assert e.subs(2**x,w)!=e
    assert e.subs(g.exp(x*g.log(g.Rational(2))),w)!=e

def test_bug():
    x1=g.Symbol("x1")
    x2=g.Symbol("x2")
    y=x1*x2
    y.subs(x1,g.Real(3.0))

def test_subbug1():
    x=g.Symbol("x")
    e=(x**x).subs(x,1)
    e=(x**x).subs(x,1.0)
