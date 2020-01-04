#   +--+      +--+      +--+      +--+
#  /    \    /    \    /    \    /    \
# + 0, 0 +--+ 2, 0 +--+ 4, 0 +--+ 6, 0 +--+
#  \    /    \    /    \    /    \    /    \
#   +--+ 1, 1 +--+ 3, 1 +--+ 5, 1 +--+ 7, 1 +
#  /    \    /    \    /    \    /    \    /
# + 0, 2 +--+ 2, 2 +--+ 4, 2 +--+ 6, 2 +--+
#  \    /    \    /    \    /    \    /    \
#   +--+ 1, 3 +--+ 3, 3 +--+ 5, 3 +--+ 7, 3 +
#  /    \    /    \    /    \    /    \    /
# + 0, 4 +--+ 2, 4 +--+ 4, 4 +--+ 6, 4 +--+
#  \    /    \    /    \    /    \    /    \
#   +--+ 1, 5 +--+ 3, 5 +--+ 5, 5 +--+ 7, 5 +
#  /    \    /    \    /    \    /    \    /
# + 0, 6 +--+ 2, 6 +--+ 4, 6 +--+ 6, 6 +--+
#  \    /    \    /    \    /    \    /
#   +--+      +--+      +--+      +--+
#
#   N  = ( 0, -2)
#   S  = ( 0, +2)
#
#   NW = (-1, -1)
#   SE = (+1, +1)
#
#   SW = (-1, +1)
#   NE = (+1, -1)
#
from functools import reduce
from typing import Iterable
from typing import Tuple

from utils import maxk

Pos = Tuple[int, int]


def step(pos: Pos, direction: str) -> Pos:
    x, y = pos
    dx, dy = {
        'n':  (+0, -2),
        'ne': (+1, -1),
        'se': (+1, +1),
        's':  (+0, +2),
        'sw': (-1, +1),
        'nw': (-1, -1),
    }[direction.lower()]

    return x + dx, y + dy


def steps(start: Pos, directions: Iterable[str]) -> Iterable[Pos]:
    pos = start
    for d in directions:
        pos = step(pos, d)
        yield pos


def distance(pos1: Pos, pos2: Pos) -> int:
    """
    >>> all(distance((1, 3), p) == 1 for p in [(1, 1), (2, 2), (2, 4), (1, 5), (0, 4), (0, 2)])
    True
    >>> all(distance((4, 4), p) == 2 for p in [(4, 0), (5, 1), (6, 2), (6, 4), (6, 6), (5, 7)])
    True
    >>> all(distance((4, 4), p) == 2 for p in [(4, 8), (3, 7), (2, 6), (2, 4), (2, 2), (3, 1)])
    True
    >>> distance((0, 4), (5, 3))
    5
    >>> distance((0, 0), (2, 6))
    4
    >>> distance((0, 0), (6, 2))
    6
    >>> distance((0, 0), (5, 3))
    5
    """
    x1, y1 = pos1
    x2, y2 = pos2
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    assert (dx + dy) % 2 == 0

    if dx < dy:
        return dx + (dy - dx) // 2
    else:
        return dx


def load_steps(fn: str) -> Iterable[str]:
    return open(fn).readline().strip().split(',')


def part_1(fn: str) -> int:
    start = (0, 0)
    end = reduce(step, load_steps(fn), start)
    d = distance(start, end)
    print(f"part 1: distance is {d} {end}")
    return d


def part_2(fn: str) -> int:
    start = (0, 0)
    max_pos, max_d = maxk(
        steps(start, load_steps(fn)),
        key=lambda p: distance(start, p)
    )
    print(f"part 2: max distance is {max_d} {max_pos}")
    return max_d


if __name__ == '__main__':
    fn_ = "data/11-input.txt"
    part_1(fn_)
    part_2(fn_)
