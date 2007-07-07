"""Module with some routines for polynomials"""

from sympy.modules.polynomials.base \
     import PolynomialException, Polynomial, coeff_list, ispoly, poly
from sympy.modules.polynomials.wrapper import coeff, div, \
factor, gcd, groebner, lcm, real_roots, resultant, roots, sqf, sqf_part
from sympy.modules.polynomials.ideals import Ideal
