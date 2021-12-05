"""
Advent of Code 2021
Day 5: Hydrothermal Venture
https://adventofcode.com/2021/day/5
"""

from collections import Counter
from typing import Iterable

from rect import Rect
from utils import parse_line
from utils import sgn


def part_1(all_vents: Iterable['Vent']) -> int:
    """
    You come across a field of hydrothermal vents on the ocean floor! These vents constantly produce
    large, opaque clouds, so it would be best to avoid them if possible.

    They tend to form in **lines**; the submarine helpfully produces a list of nearby lines of vents
    (your puzzle input) for you to review. For example:

        >>> vents = vents_from_text('''
        ...
        ...     0,9 -> 5,9
        ...     8,0 -> 0,8
        ...     9,4 -> 3,4
        ...     2,2 -> 2,1
        ...     7,0 -> 7,4
        ...     6,4 -> 2,0
        ...     0,9 -> 2,9
        ...     3,4 -> 1,4
        ...     0,0 -> 8,8
        ...     5,5 -> 8,2
        ...
        ... ''')
        >>> len(vents)
        10

    Each line of vents is given as a line segment in the format `x1,y1 -> x2,y2` where `x1,y1` are
    the coordinates of one end the line segment and `x2,y2` are the coordinates of the other end.
    These line segments include the points at both ends:

        >>> Vent.parse('1,1 -> 1,3')
        Vent((1, 1), (1, 3))
        >>> list(_.points())
        [(1, 1), (1, 2), (1, 3)]

        >>> Vent.parse('9,7 -> 7,7')
        Vent((9, 7), (7, 7))
        >>> list(_.points())
        [(9, 7), (8, 7), (7, 7)]

    For now, **only consider horizontal and vertical lines**: lines where either `x1 = x2`
    or `y1 = y2`.

    So, the horizontal and vertical lines from the above list would produce the following diagram:

        >>> draw_map(vents)
        ·······1··
        ··1····1··
        ··1····1··
        ·······1··
        ·112111211
        ··········
        ··········
        ··········
        ··········
        222111····

    In this diagram, the top left corner is `0,0` and the bottom right corner is `9,9`. Each
    position is shown as **the number of lines which cover that point** or `·` if no line covers
    that point. The top-left pair of `1`s, for example, comes from `2,2 -> 2,1`; the very bottom row
    is formed by the overlapping lines `0,9 -> 5,9` and `0,9 -> 2,9`.

    To avoid the most dangerous areas, you need to determine **the number of points where at least
    two lines overlap**. In the above example, this is anywhere in the diagram with a `2` or larger
    - a total of **`5`** points.

    Consider only horizontal and vertical lines.
    **At how many points do at least two lines overlap?**

        >>> part_1(vents)
        part 1: at least two vents overlap at 5 points (horizontal and vertical only)
        5
    """

    point_counts = Counter(
        pos
        for vent in all_vents
        if vent.is_vertical() or vent.is_horizontal()
        for pos in vent.points()
    )
    overlaps = sum(1 for q in point_counts.values() if q > 1)

    print(f"part 1: at least two vents overlap at {overlaps} points (horizontal and vertical only)")
    return overlaps


def part_2(all_vents: Iterable['Vent']) -> int:
    """
    Unfortunately, considering only horizontal and vertical lines doesn't give you the full picture;
    you need to also consider **diagonal lines**.

    Because of the limits of the hydrothermal vent mapping system, the lines in your list will only
    ever be horizontal, vertical, or a diagonal line at exactly 45 degrees:

        >>> list(Vent.parse('1,1 -> 3,3').points())
        [(1, 1), (2, 2), (3, 3)]
        >>> list(Vent.parse('9,7 -> 7,9').points())
        [(9, 7), (8, 8), (7, 9)]

    Considering all lines from the above example would now produce the following diagram:

        >>> vents = vents_from_text('''
        ...
        ...     0,9 -> 5,9
        ...     8,0 -> 0,8
        ...     9,4 -> 3,4
        ...     2,2 -> 2,1
        ...     7,0 -> 7,4
        ...     6,4 -> 2,0
        ...     0,9 -> 2,9
        ...     3,4 -> 1,4
        ...     0,0 -> 8,8
        ...     5,5 -> 8,2
        ...
        ... ''')
        >>> draw_map(vents, allow_diagonal=True)
        1·1····11·
        ·111···2··
        ··2·1·111·
        ···1·2·2··
        ·112313211
        ···1·2····
        ··1···1···
        ·1·····1··
        1·······1·
        222111····

    You still need to determine **the number of points where at least two lines overlap**.
    In the above example, this is still anywhere in the diagram with a 2 or larger - now a total
    of `12` points.

    Consider all of the lines. **At how many points do at least two lines overlap?**

        >>> part_2(vents)
        part 2: at least two vents overlap at 12 points
        12
    """

    point_counts = Counter(
        pos
        for vent in all_vents
        for pos in vent.points()
    )
    overlaps = sum(1 for q in point_counts.values() if q > 1)

    print(f"part 2: at least two vents overlap at {overlaps} points")
    return overlaps


Pos = tuple[int, int]


class Vent:
    def __init__(self, p1: Pos, p2: Pos):
        self.p1, self.p2 = p1, p2
        self.x1, self.y1 = self.p1
        self.x2, self.y2 = self.p2

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.p1}, {self.p2})'

    def __str__(self) -> str:
        return f'{self.x1},{self.y1} -> {self.x2},{self.y2}'

    @classmethod
    def parse(cls, line: str) -> 'Vent':
        # 3,4 -> 1,4
        x1, y1, x2, y2 = parse_line(line, '$,$ -> $,$')
        return cls((int(x1), int(y1)), (int(x2), int(y2)))

    @property
    def dx(self) -> int:
        return self.x2 - self.x1

    @property
    def dy(self) -> int:
        return self.y2 - self.y1

    def is_vertical(self) -> bool:
        return self.dx == 0

    def is_horizontal(self) -> bool:
        return self.dy == 0

    def is_diagonal(self) -> bool:
        return abs(self.dx) == abs(self.dy)

    def points(self) -> Iterable[Pos]:
        if self.is_vertical():
            # vertical: x1 == x2
            s = sgn(self.dy)
            return ((self.x1, y) for y in range(self.y1, self.y2 + s, s))

        elif self.is_horizontal():
            # horizontal: y1 == y2
            s = sgn(self.dx)
            return ((x, self.y1) for x in range(self.x1, self.x2 + s, s))

        elif abs(self.dx) == abs(self.dy):
            # 45 degree diagonal
            sx, sy = sgn(self.dx), sgn(self.dy)
            return (
                (self.x1 + sx * d, self.y1 + sy * d)
                for d in range(abs(self.dx) + 1)
            )

        else:
            raise ValueError('invalid vent direction')


def draw_map(vents: Iterable[Vent], allow_diagonal: bool = False) -> None:
    considered_vents = [
        vent
        for vent in vents
        if allow_diagonal or vent.is_vertical() or vent.is_horizontal()
    ]

    bounds = Rect.with_all(pos for vent in considered_vents for pos in (vent.p1, vent.p2))
    counts = Counter(p for vent in considered_vents for p in vent.points())
    lines = (
        ''.join(str(counts[(x, y)] or '·') for x in bounds.range_x())
        for y in bounds.range_y()
    )
    print('\n'.join(lines))


def vents_from_file(fn: str) -> list[Vent]:
    return [Vent.parse(line.strip()) for line in open(fn)]


def vents_from_text(text: str) -> list[Vent]:
    return [Vent.parse(line.strip()) for line in text.strip().split('\n')]


if __name__ == '__main__':
    vents_ = vents_from_file('data/05-input.txt')
    part_1(vents_)
    part_2(vents_)
