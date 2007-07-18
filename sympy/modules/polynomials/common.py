"""Simple helper functions common to several algorithms"""

from sympy import Add, Basic, Mul, Number, Pow, Rational, Real, Symbol
from sympy.modules.polynomials.base import PolynomialException, coeff_rings

def all(iterable):
    """True if all elements are True"""
    for element in iterable:
        if not element:
            return False
    return True

def one(iterable):
    """True if at least one element is True"""
    for element in iterable:
        if element:
            return True
    return False

def reverse(lisp):
    """Return a list with reversed order"""
    lisp.reverse()
    return lisp

def term_cmp(a, b, order):
    if order == 'lex':
        return cmp(a[1:], b[1:])
    elif order == 'grlex':
        return cmp([sum(a[1:])]+a[1:], [sum(b[1:])]+b[1:])
    elif order == 'grevlex':
        return cmp([sum(a[1:])]+reverse(map(lambda l:-l, a[1:])),
                   [sum(b[1:])]+reverse(map(lambda l:-l, b[1:])))
    elif order == '1-el':
        return cmp([a[1]]+[sum(a[2:])]+reverse(map(lambda l:-l,a[2:])),
                   [b[1]]+[sum(b[2:])]+reverse(map(lambda l:-l,b[2:])))
    else:
        raise PolynomialException(str(order) + 'is not an implemented order.')

def term_mult(a, b):
    """Returns a term that represents the multiplication of a and b.

    a and b are assumed to be terms of coefficient lists of
    Polynomials of same the variables.
    """
    return [(a[0]*b[0]).expand()] + map(lambda (x,y): x+y, zip(a[1:], b[1:]))

def term_div(a, b):
    """Returns a term that represents the division of a by b.

    a and b are assumed to be terms of coefficient lists of
    Polynomials of same the variables. Divisibility is not tested.
    """
    # TODO: Check if expand is necessary?
    return [(a[0]/b[0]).expand()] + map(lambda (x,y): x-y, zip(a[1:], b[1:]))

def term_is_mult(a, b):
    """Return True if a is a multiple of b

    a and b are assumed to be terms of coefficient lists of
    Polynomials of same the variables."""
    return all([x >= 0 for x in term_div(a, b)[1:]])

def term_lcm(a, b):
    # TODO: Compute lcm oder product of coefficients?
    r = [Rational(1)] # [a[0]*b[0]]
    for aa, bb in zip(a[1:], b[1:]):
        r.append(max(aa, bb))
    return r

def merge_var(*a):
    """Return a sorted list of the symbols in the arguments"""
    result = []
    for var in a:
        for sym in var:
            if not sym in result:
                result.append(sym)
    result.sort(key=str)
    return result

def copy_cl(cl):
    """Deep copy of nested lists like the coefficient list of Polynomial"""
    result = []
    for term in cl:
        result.append(term[:])
    return result

def sort_cl(cl, order):
    """Sort a given list with respect to the given order"""
    if order == 'lex':
        cl.sort(key=lambda x: x[1:], reverse=True)
    elif order == 'grlex':
        cl.sort(key=lambda x: [sum(x[1:])] + x[1:], reverse=True)
    elif order == 'grevlex':
        cl.sort(key=lambda x: [sum(x[1:])]
                 + reverse(map(lambda l:-l, x[1:])), reverse=True)
    elif order == '1-el':
        cl.sort(key=lambda x: [x[1]] + [sum(x[2:])]
                 + reverse(map(lambda l:-l, x[2:])), reverse=True)
    else:
        raise PolynomialException(str(order) + 'is not an implemented order.')
    return cl

def coeff_ring(atom):
    """Determine the coefficient ring of some atom, or some list of atoms.
    """
    if not isinstance(atom, list):
        if isinstance(atom, Rational):
            if atom.is_integer:
                return 'int'
            else:
                return 'rat'
        elif atom.is_number:
            if atom.is_real:
                return 'real'
            else:
                return 'cplx'
        elif isinstance(atom, Symbol):
            return 'sym'
        else:
            raise PolynomialException(
                "Coefficient of unknown type: %s", atom)
    else:
        # Get the coefficient ring of each atom and look for the worst case.
        result = 'int'
        for a in atom:
            cr = coeff_ring(a)
            assert type(cr) == str
            if coeff_rings.index(cr) > coeff_rings.index(result):
                result = cr
        return result

def integer_divisors(n):
    n = abs(n)
    r = []
    for i in range(1, n/2+1):
        if n % i == 0:
            r.append(i)
    r.append(n)
    return r

def get_numbers(b):
    result = []
    b = b.expand()
    if b.is_number:
        return [b]
    elif isinstance(b, Add):
        for summand in b:
            result += get_numbers(summand)
    elif isinstance(b, Mul):
        for factor in b:
            if factor.is_number:
                result.append(factor)
    return result
