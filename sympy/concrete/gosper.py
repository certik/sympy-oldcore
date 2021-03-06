"""

"""

from sympy.core.basic import Basic, S
from sympy.core.symbol import Symbol
from sympy.core.add import Add
from sympy.core.mul import Mul

from sympy.polynomials import gcd, quo, roots, resultant
from sympy.simplify import ratsimp, combsimp

from sympy.concrete.utilities import nni_roots

def normal(f, g, n):
    """Given relatively prime univariate polynomials 'f' and 'g',
       rewrite their quotient to a normal form defined as follows:

                       f(n)       A(n) C(n+1)
                       ----  =  Z -----------
                       g(n)       B(n)  C(n)

       where Z is arbitrary constant and A, B, C are monic
       polynomials in 'n' with follwing properties:

           (1) gcd(A(n), B(n+h)) = 1 for all 'h' in N
           (2) gcd(B(n), C(n+1)) = 1
           (3) gcd(A(n), C(n)) = 1

       This normal form, or rational factorization in other words,
       is crucial step in Gosper's algorithm and in difference
       equations solving. It can be also used to decide if two
       hypergeometric are similar or not.

       This procedure will return return triple containig elements
       of this factorization in the form (Z*A, B, C). For example:

       >>> from sympy import Symbol
       >>> n = Symbol('n', integer=True)

       >>> normal(4*n+5, 2*(4*n+1)*(2*n+3), n)
       (1/4, 3/2 + n, 1/4 + n)

    """
    f, g = map(Basic.sympify, (f, g))

    if f.is_polynomial:
        p = f.as_polynomial(n)
    else:
        raise ValueError("'f' must be a polynomial")

    if g.is_polynomial:
        q = g.as_polynomial(n)
    else:
        raise ValueError("'g' must be a polynomial")

    a, p = p.as_monic()
    b, q = q.as_monic()

    A = p.sympy_expr
    B = q.sympy_expr

    C, Z = S.One, a / b

    h = Symbol('h', dummy=True)

    res = resultant(A, B.subs(n, n+h), n)

    if not res.is_polynomial(h):
        res = quo(*res.as_numer_denom())

    _nni_roots = nni_roots(res, h)

    if _nni_roots == []:
        return (f, g, S.One)
    else:
        _nni_roots.sort()

        for i in _nni_roots:
            d = gcd(A, B.subs(n, n+i), n)

            A = quo(A, d, n)
            B = quo(B, d.subs(n, n-i), n)

            C *= Mul(*[ d.subs(n, n-j) for j in xrange(1, i+1) ])

        return (Z*A, B, C)

def gosper(term, k, a, n):
    from sympy.solvers import rsolve_poly

    #expr, hyper = combsimp(term.subs(k, k+1)/term, k, verify=True)

    if not hyper:
        return None
    else:
        p, q = expr.as_numer_denom()
        A, B, C = normal(p, q, k)

        B = B.subs(k, k-1)

        R = rsolve_poly([-B, A], C, k)
        symbol = []

        if not (R is None or isinstance(R, Basic.Zero)):
            if symbol != []:
                symbol = symbol[0]

                W = R.subs(symbol, S.Zero)

                if isinstance(W, Basic.Zero):
                    R = R.subs(symbol, S.One)
                else:
                    R = W

            Z = B*R*term/C
            return simplify(Z.subs(k, n+1) - Z.subs(k, a))
        else:
            return None