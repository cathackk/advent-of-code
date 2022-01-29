"""
Advent of Code 2017
Day 11: Hex Ed
https://adventofcode.com/2017/day/11
"""

from typing import Iterable

from common.file import relative_path
from common.iteration import last
from common.iteration import maxk


def part_1(directions: Iterable[str]) -> int:
    r"""
    Crossing the bridge, you've barely reached the other side of the stream when a program comes up
    to you, clearly in distress. "It's my child process," she says, "he's gotten lost in an infinite
    grid!"

    Fortunately for her, you have plenty of experience with infinite grids.

    Unfortunately for you, it's a hex grid.

    The hexagons ("hexes") in this grid are aligned such that adjacent hexes can be found to the
    north, northeast, southeast, south, southwest, and northwest:

          \ n  /
        nw +--+ ne
          /    \
        -+      +-
          \    /
        sw +--+ se
          / s  \

    You have the path the child process took. Starting where he started, you need to determine the
    fewest number of steps required to reach him. (A "step" means to move from the hex you are in to
    any adjacent hex.)

    For example:

        >>> distance_after_steps(['ne', 'ne', 'ne'])
        3
        >>> distance_after_steps(['ne', 'ne', 'sw', 'sw'])
        0
        >>> distance_after_steps(['ne', 'ne', 's', 's'])
        2

        >>> part_1(['se', 'sw', 'se', 'sw', 'sw'])
        part 1: distance to the program is 3
        3
    """
    result = distance_after_steps(directions)
    print(f"part 1: distance to the program is {result}")
    return result


def part_2(directions: Iterable[str]) -> int:
    """
    **How many steps away** is the **furthest** he ever got from his starting position?

        >>> part_2(['n', 'ne', 'n', 'ne', 'se', 's', 'nw', 'sw', 'sw'])
        part 2: max distance was 4
        4
    """

    origin = (0, 0)
    _, max_distance = maxk(steps(origin, directions), lambda pos: distance(origin, pos))
    print(f"part 2: max distance was {max_distance}")
    return max_distance


Pos = tuple[int, int]


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

STEPS = {
    'n':  (+0, -2),
    's':  (+0, +2),
    'nw': (-1, -1),
    'se': (+1, +1),
    'sw': (-1, +1),
    'ne': (+1, -1),
}


def distance_after_steps(directions: Iterable[str]) -> int:
    origin = (0, 0)
    target = last(steps(origin, directions))
    return distance(origin, target)


def steps(start: Pos, directions: Iterable[str]) -> Iterable[Pos]:
    pos = start
    for d in directions:
        pos = step(pos, d)
        yield pos


def step(pos: Pos, direction: str) -> Pos:
    x, y = pos
    dx, dy = STEPS[direction.lower()]
    return x + dx, y + dy


def distance(pos_1: Pos, pos_2: Pos) -> int:
    x1, y1 = pos_1
    x2, y2 = pos_2
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    assert (dx + dy) % 2 == 0

    if dx < dy:
        return dx + (dy - dx) // 2
    else:
        return dx


def directions_from_file(fn: str) -> list[str]:
    return open(relative_path(__file__, fn)).readline().strip().split(',')


if __name__ == '__main__':
    directions_ = directions_from_file('data/11-input.txt')
    part_1(directions_)
    part_2(directions_)
