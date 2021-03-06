import sys
sys.path.append(".")

import py
import sympy

# polynomials/fast/modint.py

def test_ModularInteger():
    from sympy.polynomials.fast import modint
    
    p = 5
    IntMod5 = modint.ModularIntegerFactory(p)

    assert IntMod5(0) == IntMod5(15)
    assert IntMod5(-2) == IntMod5(3)
    
    assert str(IntMod5(2)) == '2 mod 5'

    assert int(IntMod5(2)) == 2
    assert int(IntMod5(3)) == -2

    assert +IntMod5(2) == IntMod5(2)
    assert -IntMod5(2) == IntMod5(3)
    assert IntMod5(4) + IntMod5(3) == IntMod5(2)
    assert IntMod5(2) - IntMod5(3) == IntMod5(4)
    assert IntMod5(3) * IntMod5(2) == IntMod5(1)
    assert IntMod5(1) / IntMod5(2) == IntMod5(3)
    assert IntMod5(3)**7 == IntMod5(1) / IntMod5(3)
    assert IntMod5(2)

    assert modint.crt([2, 3, 5], [0, 0, 0]) == 0
    assert modint.crt([2, 3, 5], [1, 1, 1]) == 1
    assert modint.crt([2, 3, 5], [-1, -1, -1], True) == -1
    assert modint.crt([2, 3, 5], [-1, -1, -1], False) == 2*3*5 - 1    

# polynomials/fast/gfpoly.py

def test_GFPoly():
    from sympy.polynomials.fast import gfpoly

    p = 5
    IntMod5Poly = gfpoly.GFPolyFactory(p)
    IntMod5 = IntMod5Poly.coeff_type
    
    f = IntMod5Poly.from_int_dict({2:1, 0:1})
    g = IntMod5Poly.from_int_dict({3:2, 1:1, 0:2})

    assert f[0] == IntMod5(1)
    assert f[1] == IntMod5(0)

    assert +f == f
    assert -f == IntMod5Poly.from_int_dict({2:-1, 0:-1})
    assert f.scale(IntMod5(2), 3) == IntMod5Poly.from_int_dict({5:2, 3:2})
    assert f + g == IntMod5Poly.from_int_dict({3:2, 2:1, 1:1, 0:3})
    assert f - g == IntMod5Poly.from_int_dict({3:-2, 2:1, 1:-1, 0:-1})
    assert f * g == IntMod5Poly.from_int_dict({5:2, 3:3, 2:2, 1:1, 0:2})
    assert f**5 == IntMod5Poly.from_int_dict({10:1, 0:1})
    assert (f*g).diff() == IntMod5Poly.from_int_dict({2:4, 1:4, 0:1})

    assert g.monic() \
           == (IntMod5(2), IntMod5Poly.from_int_dict({3:1, 1:-2, 0:1}))
    assert g.monic()[1].to_sym_int_dict() == {3:1, 1:-2, 0:1}

    q, r = gfpoly.div(f, g)
    assert (not q) and (r == f)
    q, r = gfpoly.div(g, f)
    assert q == IntMod5Poly.from_int_dict({1:2})
    assert r == IntMod5Poly.from_int_dict({1:4, 0:2})

    assert gfpoly.gcd(f, g) == IntMod5Poly.from_int_dict({1:1, 0:3})
    assert gfpoly.gcd(f**3, f**4) == f**3

    h, s, t = gfpoly.xgcd(f, g)
    assert h == IntMod5Poly.from_int_dict({1:1, 0:3})
    assert s == IntMod5Poly.from_int_dict({1:2})
    assert t == IntMod5Poly.from_int_dict({0:4})
    assert h == (s*f + t*g)
    
    assert gfpoly.truncate(f, 5) == f
    assert gfpoly.truncate(f, 1) == IntMod5Poly.from_int_dict({0:1})

    assert gfpoly.pow_mod(f, 3, IntMod5Poly.from_int_dict({2:1})) \
           == gfpoly.truncate(f**3, 2)

    p = 3
    IntMod3Poly = gfpoly.GFPolyFactory(p)
    f = IntMod3Poly.from_int_dict({1:1}) \
        * IntMod3Poly.from_int_dict({1:1, 0:1}) \
        * IntMod3Poly.from_int_dict({2:1, 0:1}) \
        * IntMod3Poly.from_int_dict({2:1, 1:1, 0:2})
    a = gfpoly.distinct_degree_factor(f)
    assert [g.to_sym_int_dict() for g in a] \
           == [{1: 1, 2: 1}, {0: -1, 1: 1, 3: 1, 4: 1}]
    b = gfpoly.equal_degree_factor(a[0], 1)
    assert sorted([g.to_sym_int_dict() for g in b]) \
           == sorted([{1:1}, {1:1, 0:1}])
    c = gfpoly.equal_degree_factor(a[1], 2)
    assert sorted([g.to_sym_int_dict() for g in c]) \
           == sorted([{2:1, 0:1}, {2:1, 1:1, 0:-1}])

    r = gfpoly.factor_sqf(f)
    assert r[0] == IntMod3Poly.coeff_type(1)
    r = r[1:]
    assert len(r) == 4
    assert IntMod3Poly.from_int_dict({1:1}) in r
    assert IntMod3Poly.from_int_dict({1:1, 0:1}) in r
    assert IntMod3Poly.from_int_dict({2:1, 0:1}) in r
    assert IntMod3Poly.from_int_dict({2:1, 1:1, 0:2}) in r

    f = IntMod3Poly.from_int_dict({1:1}) \
    * IntMod3Poly.from_int_dict({1:1, 0:1}) \
    * IntMod3Poly.from_int_dict({1:1, 0:1}) \
    * IntMod3Poly.from_int_dict({2:1, 0:1}) \
    * IntMod3Poly.from_int_dict({2:1, 1:1, 0:2}) \
    * IntMod3Poly.from_int_dict({2:1, 1:1, 0:2}) \
    * IntMod3Poly.from_int_dict({1:1, 0:1}) \
    * IntMod3Poly.from_int_dict({1:1, 0:1}) \
    * IntMod3Poly.from_int_dict({2:1, 0:1}) \
    * IntMod3Poly.from_int_dict({2:1, 1:1, 0:2}) \
    * IntMod3Poly.from_int_dict({2:1, 1:1, 0:2}) \
    * IntMod3Poly.from_int_dict({1:1, 0:1}) \
    * IntMod3Poly.from_int_dict({1:1, 0:1}) \
    * IntMod3Poly.from_int_dict({2:1, 0:1}) \
    * IntMod3Poly.from_int_dict({2:1, 1:1, 0:2}) \
    * IntMod3Poly.from_int_dict({2:1, 1:1, 0:2}) \
    * IntMod3Poly.from_int_dict({2:1, 1:1, 0:2})
    r = gfpoly.factor(f)
    assert r[0] == IntMod3Poly.coeff_type(1)
    test_dict = {}
    for item in r[1:]:
        test_dict[item[1]] = item[0].to_sym_int_dict()
    assert test_dict == {1: {1:1}, 3:{2:1, 0:1}, 6:{1:1, 0:1},
                         7:{2:1, 1:1, 0:-1}}


# polynomials/fast/intpoly.py

def test_IntPoly():
    from sympy.polynomials.fast import intpoly

    f = intpoly.IntPoly()
    lc, pp = f.primitive()
    assert lc == 0
    assert pp == f
    assert f.evaluate(0) == 0
    assert f.evaluate(100) == 0
    assert f.evaluate(-2) == 0
    
    f = intpoly.IntPoly({2:12, 1:8, 0:-20})
    lc, pp = f.primitive()
    assert lc == 4
    assert pp == intpoly.IntPoly({2:3, 1:2, 0:-5})
    assert f.evaluate(0) == -20
    assert f.evaluate(100) == 120780

    g = intpoly.IntPoly({1:3})
    q, r = intpoly.div(f, g)
    assert q == intpoly.IntPoly({1:4})
    assert r == intpoly.IntPoly({1:8, 0:-20})

    assert intpoly.gcd_small_primes(f, g) == intpoly.IntPoly({0: 1})
    assert intpoly.gcd_heuristic(f, g) == intpoly.IntPoly({0: 1})
    f = intpoly.IntPoly({3:2, 2:3})
    g = intpoly.IntPoly({1:10, 0:15})
    assert intpoly.gcd_small_primes(f, g) == intpoly.IntPoly({1:2, 0:3})
    assert intpoly.gcd_heuristic(f, g) == intpoly.IntPoly({1:2, 0:3})

    assert intpoly.squarefree_part(f).coeffs == {2:2, 1:3}

    f = intpoly.IntPoly({4:1, 0:-1})
    g = intpoly.IntPoly({3:1, 2:2, 1:-1, 0:-2})
    h = intpoly.IntPoly({1:1, 0:-2})
    s = intpoly.IntPoly({0:-2})
    t = intpoly.IntPoly({2:2, 1:-2, 0:-1})
    gg, hh, ss, tt = intpoly.hensel_step(5, f, g, h, s, t)
    assert gg == intpoly.IntPoly({3:1, 2:7, 1:-1, 0:-7})
    assert hh == intpoly.IntPoly({1:1, 0:-7})
    assert ss == intpoly.IntPoly({0:8})
    assert tt == intpoly.IntPoly({2:-8, 1:-12, 0:-1})

    f1 = intpoly.IntPoly({1:1, 0:-1})
    f2 = intpoly.IntPoly({1:1, 0:-2})
    f3 = intpoly.IntPoly({1:1, 0:2})
    f4 = intpoly.IntPoly({1:1, 0:1})
    ff_list = intpoly.multi_hensel_lift(5, f, [f1, f2, f3, f4], 4)
    assert [ff.coeffs for ff in ff_list] \
           == [{0: -1, 1: 1}, {0: -182, 1: 1}, {0: 182, 1: 1}, {0: 1, 1: 1}]

    f = intpoly.IntPoly({4:6, 3:5, 2:15, 1:5, 0:4})
    factors = [ff.coeffs for ff in intpoly.zassenhaus(f)]
    assert {2:2, 1:1, 0:4} in factors
    assert {2:3, 1:1, 0:1} in factors
    
