
from sympy.core import Basic, S
from sympy.core.function import SingleValuedFunction
from zeta_functions import zeta

###############################################################################
############################ COMPLETE GAMMA FUNCTION ##########################
###############################################################################

class gamma(SingleValuedFunction):

    nofargs = 1

    def fdiff(self, argindex=1):
        if argindex == 1:
            return gamma(self[0])*polygamma(0, self[0])
        else:
            raise ArgumentIndexError(self, argindex)

    @classmethod
    def _eval_apply(cls, arg):
        arg = Basic.sympify(arg)

        if isinstance(arg, Basic.Number):
            if isinstance(arg, Basic.NaN):
                return S.NaN
            elif isinstance(arg, Basic.Infinity):
                return S.Infinity
            elif isinstance(arg, Basic.Integer):
                if arg.is_positive:
                    return Basic.Factorial(arg-1)
                else:
                    return S.ComplexInfinity
            elif isinstance(arg, Basic.Rational):
                if arg.q == 2:
                    n = abs(arg.p) / arg.q

                    if arg.is_positive:
                        k, coeff = n, S.One
                    else:
                        n = k = n + 1

                        if n & 1 == 0:
                            coeff = S.One
                        else:
                            coeff = S.NegativeOne

                    for i in range(3, 2*k, 2):
                        coeff *= i

                    if arg.is_positive:
                        return coeff*Basic.sqrt(S.Pi) / 2**n
                    else:
                        return 2**n*Basic.sqrt(S.Pi) / coeff


    def _eval_expand_func(self, *args):
        arg = self[0]._eval_expand_basic()

        if isinstance(arg, Basic.Add):
            for i, coeff in enumerate(arg[:]):
                if isinstance(arg[i], Basic.Number):
                    terms = Basic.Add(*(arg[:i] + arg[i+1:]))

                    if isinstance(coeff, Basic.Rational):
                        if coeff.q != 1:
                            terms += Basic.Rational(1, coeff.q)
                            coeff = Basic.Integer(int(coeff))
                    else:
                        continue

                    return gamma(terms)*Basic.RisingFactorial(terms, coeff)

        return self.func(*self[:])

    def _eval_is_real(self):
        return self[0].is_real


###############################################################################
################## LOWER and UPPER INCOMPLETE GAMMA FUNCTIONS #################
###############################################################################

class lowergamma(SingleValuedFunction):
    """Lower incomplete gamma function"""

    nofargs = 2

    @classmethod
    def _eval_apply(cls, a, x):
        if isinstance(a, Basic.Number):
            if isinstance(a, Basic.One):
                return S.One - Basic.exp(-x)
            elif isinstance(a, Basic.Integer):
                b = a - 1

                if b.is_positive:
                    return b*cls(b, x) - x**b * Basic.exp(-x)


class uppergamma(SingleValuedFunction):
    """Upper incomplete gamma function"""

    nofargs = 2

    def fdiff(self, argindex=2):
        if argindex == 2:
            a, z = self[0:2]
            return -Basic.exp(-z)*z**(a-1)
        else:
            raise ArgumentIndexError(self, argindex)

    @classmethod
    def _eval_apply(cls, a, z):
        if isinstance(z, Basic.Number):
            if isinstance(z, Basic.NaN):
                return S.NaN
            elif isinstance(z, Basic.Infinity):
                return S.Zero
            elif isinstance(z, Basic.Zero):
                return gamma(a)

        if isinstance(a, Basic.Number):
            if isinstance(a, Basic.One):
                return Basic.exp(-z)
            elif isinstance(a, Basic.Integer):
                b = a - 1

                if b.is_positive:
                    return b*cls(b, z) + z**b * Basic.exp(-z)



###############################################################################
########################### GAMMA RELATED FUNCTIONS ###########################
###############################################################################

class polygamma(SingleValuedFunction):

    nofargs = 2

    def fdiff(self, argindex=2):
        if argindex == 2:
            n, z = self[0:2]
            return polygamma(n+1, z)
        else:
            raise ArgumentIndexError(self, argindex)

    @classmethod
    def _eval_apply(cls, n, z):
        n, z = map(Basic.sympify, (n, z))

        if n.is_integer:
            if n.is_negative:
                return loggamma(z)
            else:
                if isinstance(z, Basic.Number):
                    if isinstance(z, Basic.NaN):
                        return S.NaN
                    elif isinstance(z, Basic.Infinity):
                        if isinstance(n, Basic.Number):
                            if isinstance(n, Basic.Zero):
                                return S.Infinity
                            else:
                                return S.Zero
                    elif isinstance(z, Basic.Integer):
                        if z.is_nonpositive:
                            return S.ComplexInfinity
                        else:
                            if isinstance(n, Basic.Zero):
                                return -S.EulerGamma + Basic.harmonic(z-1, 1)
                            elif n.is_odd:
                                return (-1)**(n+1)*Basic.Factorial(n)*zeta(n+1, z)


    def _eval_expand_func(self, *args):
        n, z = self[0], self[1].expand(func=True)

        if isinstance(n, Basic.Integer) and n.is_nonnegative:
            if isinstance(z, Basic.Add):
                coeff, factors = z.as_coeff_factors()

                if isinstance(coeff, Basic.Integer):
                    tail = Add(*[ z + i for i in xrange(0, int(coeff)) ])
                    return self(n, z-coeff) + (-1)**n*Basic.Factorial(n)*tail
            elif isinstance(z, Basic.Mul):
                coeff, terms = z.as_coeff_terms()

                if isinstance(coeff, Basic.Integer) and coeff.is_positive:
                    tail = [ self(n, z + i/coeff) for i in xrange(0, int(coeff)) ]

                    if isinstance(n, Basic.Zero):
                        return S.Log(coeff) + Add(*tail)/coeff**(n+1)
                    else:
                        return Add(*tail)/coeff**(n+1)

        return self(n, z)

    def _eval_rewrite_as_zeta(self, n, z):
        return (-1)**(n+1)*Basic.Factorial(n)*zeta(n+1, z-1)

class loggamma(SingleValuedFunction):

    nofargs = 1

    def _eval_apply(self, z):
        return

