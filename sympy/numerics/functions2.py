"""
Numerical implementations of special functions (gamma, ...)
"""

from float_ import Float, ComplexFloat
from constants import pi_float, gamma_float
from functions import exp, log, sqrt, sin, power
from utils_ import make_fixed

from sympy import Rational


#---------------------------------------------------------------------------#
#                                                                           #
#                              Gamma function                               #
#                                                                           #
#---------------------------------------------------------------------------#

"""
We compute the gamma function using Spouge's approximation

    x! = (x+a)**(x+1/2) * exp(-x-a) * [c_0 + S(x) + eps]

where S(x) is the sum of c_k/(x+k) from k = 1 to a-1 and the coefficients
are given by

  c_0 = sqrt(2*pi)

         (-1)**(k-1)
  c_k =  ----------- (a-k)**(k-1/2) exp(-k+a),  k = 1,2,...,a-1
          (k - 1)!

Due to an inequality proved by Spouge, if we choose a = int(1.26*n), the
error eps is less than 10**-n for any x in the right complex half-plane
(assuming a > 2). In practice, it seems that a can be chosen quite a bit
lower still (30-50%); this possibility should be investigated.

Reference:
John L. Spouge, "Computation of the gamma, digamma, and trigamma
functions", SIAM Journal on Numerical Analysis 31 (1994), no. 3, 931-944.
"""


#----------------------------------------------------------------------
#
# We first implement a helper function for calculating the coefficients
# c_k and caching them so that they can be re-used for multiple gamma
# function evaluations
#

_spouge_cache = {}

def _calc_spouge_coefficients(a, prec):
    """
    Calculate Spouge coefficients for approximation with parameter a.
    Return a list of big integers representing the coefficients in
    fixed-point form with a precision of prec bits.
    """

    # We'll store the coefficients as fixed-point numbers but calculate
    # them as Floats for convenience. The initial terms are huge, so we
    # need to allocate extra bits to ensure full accuracy. The integer
    # part of the largest term has size ~= exp(a) or 2**(1.4*a)
    floatprec = prec + int(a*1.4)
    Float.store()
    Float.setprec(floatprec)

    c = [0] * a
    b = exp(a-1)
    e = exp(1)
    c[0] = make_fixed(sqrt(2*pi_float()), prec)
    for k in range(1, a):
        # print "%02f" % (100.0 * k / a), "% done"
        c[k] = make_fixed(((-1)**(k-1) * (a-k)**k) * b / sqrt(a-k), prec)
        # Divide off e and k instead of computing exp and k! from scratch
        b = b / (e * k)

    Float.revert()
    return c

# Cached lookup of coefficients
def _get_spouge_coefficients(prec):

    # This exact precision has been used before
    if prec in _spouge_cache:
        return _spouge_cache[prec]

    for p in _spouge_cache:
        # Coefficients calculated for a slightly higher precision are ok
        # too. But if the difference is too big, we're better off
        # starting from scratch
        if 0.8 <= float(p)/prec < 1:
            return _spouge_cache[p]

    # Here we estimate the value of a based on Spouge's inequality for
    # the relative error
    a = max(3, int(0.39*prec))  # ~= 1.26*n

    # Compute and return
    coefs = _calc_spouge_coefficients(a, prec)
    _spouge_cache[prec] = (prec, a, coefs)
    return _spouge_cache[prec]


# This function computes S
def _spouge_sum(x, prec, a, c):
    if isinstance(x, Float):
        # Regular fixed-point summation
        x = make_fixed(x, prec)
        s = c[0]
        for k in xrange(1, a):
            s += (c[k] << prec) // (x + (k << prec))
        return Float((s, -prec))
    elif isinstance(x, (Rational, int, long)):
        # Here we can save some work
        if isinstance(x, (int, long)):
            p, q = x, 1
        else:
            p, q = x.p, x.q
        s = c[0]
        for k in xrange(1, a):
            s += c[k] * q // (p+q*k)
        return Float((s, -prec))
    elif isinstance(x, ComplexFloat):
        """
        For a complex number a + b*I, we have

              c_k          (a+k)*c_k     b * c_k
        -------------  =   ---------  -  ------- * I
        (a + b*I) + k          M            M

                       2    2      2   2              2
        where M = (a+k)  + b   = (a + b ) + (2*a*k + k )
        """
        re = make_fixed(x.real, prec)
        im = make_fixed(x.imag, prec)
        sre, sim = c[0], 0
        mag = ((re**2)>>prec) + ((im**2)>>prec)
        for k in xrange(1, a):
            M = mag + re*(2*k) + ((k**2) << prec)
            sre += (c[k] * (re + (k << prec))) // M
            sim -= (c[k] * im) // M
        return ComplexFloat(Float((sre, -prec)), Float((sim, -prec)))


def gamma(x):
    """
    gamma(x) -- calculate the gamma function of a real or complex
    number x.
    
    x must not be a negative integer or 0
    """
    Float.store()
    Float._prec += 2

    if isinstance(x, complex):
        x = ComplexFloat(x)
    elif not isinstance(x, (Float, ComplexFloat, Rational, int, long)):
        x = Float(x)

    if isinstance(x, (ComplexFloat, complex)):
        re, im = x.real, x.imag
    else:
        re, im = x, 0

    # For negative x (or positive x close to the pole at x = 0),
    # we use the reflection formula
    if re < 0.25:
        if re == int(re) and im == 0:
            raise ZeroDivisionError, "gamma function pole"
        Float._prec += 3
        p = pi_float()
        g = p / (sin(p*x) * gamma(1-x))
    else:
        x -= 1
        prec, a, c = _get_spouge_coefficients(Float.getprec()+7)
        s = _spouge_sum(x, prec, a, c)
        if not isinstance(x, (Float, ComplexFloat)):
            x = Float(x)
        # TODO: higher precision may be needed here when the precision
        # and/or size of x are extremely large
        Float._prec += 10
        g = exp(log(x+a)*(x+Float(0.5))) * exp(-x-a) * s

    Float.revert()
    return +g


#---------------------------------------------------------------------------#
#                                                                           #
#                       Incomplete gamma functions                          #
#                                                                           #
#---------------------------------------------------------------------------#

"""
We compute the lower incomplete gamma function g(a,z) using the formula
g(a,z) = z**a * exp(-z) * S(a,z) / a, where
                 oo
                ___            k
               \              z
  S(a,z) = 1 +  )     ------------------.
               /___   (a+1)(a+2)...(a+k)
               k = 1

Then, in turn, various functions such as erf and exponential integrals
can be computed from the incomplete gamma function.
"""

def _lower_gamma_series(are, aim, zre, zim, prec):
    are = make_fixed(are, prec)
    aim = make_fixed(aim, prec)
    zre = make_fixed(zre, prec)
    zim = make_fixed(zim, prec)
    one = 1 << prec
    cre = sre = one
    cim = sim = 0
    while abs(cre) > 3 or abs(cim) > 3:
        # c = (c * z) << prec
        cre, cim = (cre*zre-cim*zim)>>prec, (cim*zre+cre*zim)>>prec
        # c = c / (a+k)
        are += one
        mag = ((are**2 + aim**2) >> prec)
        cre, cim = (cre*are + cim*aim)//mag, (cim*are - cre*aim)//mag
        sre += cre
        sim += cim
        #k += 1
    sre = Float((sre, -prec))
    sim = Float((sim, -prec))
    return ComplexFloat(sre, sim)

def lower_gamma(a, z):
    Float.store()
    prec = Float._prec
    # XXX: may need more precision
    Float._prec += 15
    a = ComplexFloat(a)
    z = ComplexFloat(z)
    s = _lower_gamma_series(a.real, a.imag, z.real, z.imag, prec)
    y = exp(log(z)*a) * exp(-z) * s / a
    Float.revert()
    return +y

def upper_gamma(a, z):
    return gamma(a) - lower_gamma(a, z)

def erf(x):
    x = ComplexFloat(x)
    if x == 0: return Float(0)
    if x.real < 0: return -erf(-x)
    Float.store()
    Float._prec += 10
    y = lower_gamma(0.5, x**2) / sqrt(pi_float())
    if x.imag == 0:
        y = y.real
    Float.revert()
    return +y


#---------------------------------------------------------------------------#
#                                                                           #
#                         Riemann zeta function                             #
#                                                                           #
#---------------------------------------------------------------------------#

"""
We use zeta(s) = eta(s) * (1 - 2**(1-s)) and Borwein's approximation
                  n-1
                  ___       k
             -1  \      (-1)  (d_k - d_n)
  eta(s) ~= ----  )     ------------------
             d_n /___              s
                 k = 0      (k + 1)
where
             k
             ___                i
            \     (n + i - 1)! 4
  d_k  =  n  )    ---------------.
            /___   (n - i)! (2i)!
            i = 0

If s = a + b*I, the absolute error for eta(s) is bounded by

    3 (1 + 2|b|)
    ------------ * exp(|b| pi/2)
               n
    (3+sqrt(8))

Disregarding the linear term, we have approximately,

  log(err) ~= log(exp(1.58*|b|)) - log(5.8**n)
  log(err) ~= 1.58*|b| - log(5.8)*n
  log(err) ~= 1.58*|b| - 1.76*n
  log2(err) ~= 2.28*|b| - 2.54*n

So for p bits, we should choose n > (p + 2.28*|b|) / 2.54.

Reference:
Peter Borwein, "An Efficient Algorithm for the Riemann Zeta Function"
http://www.cecm.sfu.ca/personal/pborwein/PAPERS/P117.ps

http://en.wikipedia.org/wiki/Dirichlet_eta_function
"""

_d_cache = {}

def _zeta_coefs(n):
    if n in _d_cache:
        return _d_cache[n]
    ds = [0] * (n+1)
    d = 1
    s = ds[0] = 1
    for i in range(1, n+1):
        d = d * 4 * (n+i-1) * (n-i+1)
        d //= ((2*i) * ((2*i)-1))
        s += d
        ds[i] = s
    _d_cache[n] = ds
    return ds

# Integer logarithms
_log_cache = {}

def _logk(k):
    p = Float._prec
    if k in _log_cache and _log_cache[k][0] >= p:
        return +_log_cache[k][1]
    else:
        x = log(k)
        _log_cache[k] = (p, x)
        return x

def zeta(s):
    """
    zeta(s) -- calculate the Riemann zeta function of a real or complex
    argument s.

    """
    Float.store()
    Float._prec += 8
    si = s
    s = ComplexFloat(s)
    if s.real < 0:
        # Reflection formula (XXX: gets bad around the zeros)
        pi = pi_float()
        y = power(2, s) * power(pi, s-1) * sin(pi*s/2) * gamma(1-s) * zeta(1-s)
    else:
        p = Float._prec
        n = int((p + 2.28*abs(float(s.imag)))/2.54) + 3
        d = _zeta_coefs(n)
        if isinstance(si, (int, long)):
            t = 0
            for k in range(n):
                t += (((-1)**k * (d[k] - d[n])) << p) // (k+1)**si
            y = (Float((t, -p)) / -d[n]) / (Float(1) - Float(2)**(1-si))
        else:
            t = Float(0)
            for k in range(n):
                t += (-1)**k * Float(d[k]-d[n]) * exp(-_logk(k+1)*s)
            y = (t / -d[n]) / (Float(1) - exp(log(2)*(1-s)))
    Float.revert()
    if isinstance(y, ComplexFloat) and s.imag == 0:
        return +y.real
    else:
        return +y
