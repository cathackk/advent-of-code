from math import sqrt


def gcd2(a: int, b: int) -> int:
    if a == 0 or b == 0:
        raise ZeroDivisionError("integer division or modulo by zero")

    a, b = abs(a), abs(b)
    if a == b:
        return a

    if a < b:
        a, b = b, a

    while a % b > 0:
        a, b = b, a % b

    return b


def gcd(*xs: int) -> int:
    result = None

    for x in xs:
        if result is None:
            result = x
        else:
            result = gcd2(result, x)

    if result is None:
        raise ValueError("no values given to gcd()")

    return result


def lcm2(a: int, b: int) -> int:
    return abs(a * b) // gcd2(a, b)


def lcm(*xs: int) -> int:
    result = None

    for x in xs:
        if result is None:
            result = x
        else:
            result = lcm2(result, x)

    if result is None:
        raise ValueError("no values given to lcm()")

    return result


def modular_inverse(x: int, m: int) -> int:
    t, newt = 0, 1
    r, newr = m, x % m
    while newr != 0:
        quotient = r // newr
        t, newt = newt, t - quotient * newt
        r, newr = newr, r - quotient * newr
    if r > 1:
        raise ValueError(f"no modular inverse for 1/{x} mod {m}")
    return t % m


def triangular_root(t: int) -> int:
    """
    Given a number `t`, find `n` such that `tr(n) <= t < tr(n+1)`.

    Perfect roots:

        >>> triangular_root(10)
        4
        >>> triangular_root(15)
        5
        >>> triangular_root(5050)
        100

    Close roots:

    tr(4) = 10 <= 12 < 15 = tr(4+1)

        >>> triangular_root(12)
        4

    tr(44) = 990 <= 1000 < 1035 = tr(44+1)

        >>> triangular_root(1000)
        44
        >>> triangular_root(990)
        44
        >>> triangular_root(1034)
        44
        >>> triangular_root(1035)
        45
    """

    # (n+1) * (n/2) = t
    # (n^2 + n) / 2 = t
    #     4n^2 + 4n = 8t
    # 4n^2 + 4n + 1 = 8t + 1
    #    (2n + 1)^2 = 8t + 1
    #        2n + 1 = sqrt(8t + 1)
    #            2n = sqrt(8t + 1) - 1
    #             n = (sqrt(8t + 1) - 1) / 2

    return int((sqrt(8 * t + 1) - 1) / 2)


def sgn(x) -> int:
    """
    >>> sgn(-15)
    -1
    >>> sgn(1/3)
    1
    >>> sgn(0)
    0
    >>> sgn(0.0)
    0
    """
    if x > 0:
        return +1
    elif x < 0:
        return -1
    else:
        return 0


def constrained(value, min_value, max_value):
    if value < min_value:
        return min_value
    elif max_value < value:
        return max_value
    else:
        return value


def mod1(a: int, b: int) -> int:
    """
    >>> [mod1(x, 3) for x in range(10)]
    [3, 1, 2, 3, 1, 2, 3, 1, 2, 3]
    """
    return (a % b) or b


def ceildiv(a: int, b: int) -> int:
    """
    >>> ceildiv(9, 3)
    3
    >>> ceildiv(10, 3)
    4
    >>> ceildiv(11, 3)
    4
    >>> ceildiv(12, 3)
    4
    >>> ceildiv(13, 3)
    5
    """
    return a // b + (a % b > 0)
