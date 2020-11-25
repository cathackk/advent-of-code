import math
from typing import Iterable
from typing import Tuple


Pos = Tuple[int, int]


def reverse_triangle(s: int) -> int:
    """
    >>> reverse_triangle(1)
    1
    >>> reverse_triangle(3)
    2
    >>> reverse_triangle(6)
    3
    >>> reverse_triangle(10)
    4
    >>> reverse_triangle(11)
    5
    >>> reverse_triangle(34)
    8
    >>> reverse_triangle(100)
    14
    """
    return math.ceil((math.sqrt(8 * s + 1) - 1) / 2)


def layer_index(n: int) -> int:
    """
    >>> layer_index(0)
    0
    >>> layer_index(1)
    1
    >>> layer_index(8)
    1
    >>> layer_index(9)
    2
    >>> layer_index(24)
    2
    >>> layer_index(25)
    3
    >>> layer_index(48)
    3
    >>> layer_index(49)
    4
    """
    return reverse_triangle(math.ceil(n / 8))


def layer_offset(ln: int) -> int:
    """
    >>> layer_offset(0)
    0
    >>> layer_offset(1)
    1
    >>> layer_offset(2)
    9
    >>> layer_offset(3)
    25
    >>> layer_offset(4)
    49
    >>> layer_offset(5)
    81
    """
    return (2 * ln - 1) ** 2 if ln > 0 else 0


def spiral_pos(n: int) -> Pos:
    """
    >>> spiral_pos(0)
    (0, 0)
    >>> [spiral_pos(n) for n in range(1, 9)]
    [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    >>> [spiral_pos(n) for n in range(9, 27, 3)]
    [(2, -1), (2, 2), (-1, 2), (-2, 0), (-1, -2), (2, -2)]
    >>> [spiral_pos(n) for n in [25, 33, 34, 42, 44, 50]]
    [(3, -2), (0, 3), (-1, 3), (-3, -3), (-1, -3), (4, -2)]
    """
    if n == 0:
        return 0, 0
    ln = layer_index(n)
    dn = n - layer_offset(ln)
    side = dn // (2 * ln)
    p = dn - (2 * ln * side) + 1
    if side == 0:
        return ln, p - ln
    elif side == 1:
        return ln - p, ln
    elif side == 2:
        return -ln, ln - p
    elif side == 3:
        return p - ln, -ln


def spiral_distance(a: int, b: int = 0) -> int:
    """
    >>> spiral_distance(0)
    0
    >>> spiral_distance(11)
    3
    >>> spiral_distance(22)
    2
    >>> spiral_distance(1023)
    31
    """
    ax, ay = spiral_pos(a)
    bx, by = spiral_pos(b)
    return abs(ax - bx) + abs(ay - by)


def n8(pos: Pos) -> Iterable[Pos]:
    x, y = pos
    yield x + 1, y
    yield x + 1, y + 1,
    yield x, y + 1
    yield x - 1, y + 1
    yield x - 1, y
    yield x - 1, y - 1
    yield x, y - 1
    yield x + 1, y - 1


def part_1(n: int) -> int:
    result = spiral_distance(n-1)
    print(f"part 1: it takes {result} steps to reach {n}")
    return result


def part_2(n: int) -> int:
    spiral = {(0, 0): 1}
    for k in range(1, n):
        pos = spiral_pos(k)
        nsum = sum(spiral.get(npos, 0) for npos in n8(pos))
        if nsum > n:
            print(f"part 2: {nsum} is the first value larger than {n}")
            return nsum
        spiral[pos] = nsum


if __name__ == '__main__':
    n_ = 265149
    part_1(n_)
    part_2(n_)
