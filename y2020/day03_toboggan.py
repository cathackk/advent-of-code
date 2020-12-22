"""
Advent of Code 2020
Day 3: Toboggan Trajectory
https://adventofcode.com/2020/day/3
"""

from typing import Iterable
from typing import Set
from typing import Tuple

from rect import Rect
from utils import join_and
from utils import product


def part_1(trees: 'TreesMap'):
    r"""
    Trees in this area only grow on exact integer coordinates in a grid. You make a map
    (your puzzle input) of the open squares (`.`) and trees (`#`) you can see.

    For example:

        >>> tmap = TreesMap.from_text(r'''
        ...
        ...     ..##.......
        ...     #...#...#..
        ...     .#....#..#.
        ...     ..#.#...#.#
        ...     .#...##..#.
        ...     ..#.##.....
        ...     .#.#.#....#
        ...     .#........#
        ...     #.##...#...
        ...     #...##....#
        ...     .#..#...#.#
        ...
        ... ''')
        >>> tmap == TreesMap.example_map()
        True
        >>> len(tmap)
        37
        >>> (2, 0) in tmap
        True
        >>> (0, 2) in tmap
        False
        >>> tmap.height
        11

    These aren't the only trees, though; the same pattern repeats to the right many times:

        ..##.........##.........##.........##.........##.........##.......  --->
        #...#...#..#...#...#..#...#...#..#...#...#..#...#...#..#...#...#..
        .#....#..#..#....#..#..#....#..#..#....#..#..#....#..#..#....#..#.
        ..#.#...#.#..#.#...#.#..#.#...#.#..#.#...#.#..#.#...#.#..#.#...#.#
        .#...##..#..#...##..#..#...##..#..#...##..#..#...##..#..#...##..#.
        ..#.##.......#.##.......#.##.......#.##.......#.##.......#.##.....  --->
        .#.#.#....#.#.#.#....#.#.#.#....#.#.#.#....#.#.#.#....#.#.#.#....#
        .#........#.#........#.#........#.#........#.#........#.#........#
        #.##...#...#.##...#...#.##...#...#.##...#...#.##...#...#.##...#...
        #...##....##...##....##...##....##...##....##...##....##...##....#
        .#..#...#.#.#..#...#.#.#..#...#.#.#..#...#.#.#..#...#.#.#..#...#.#  --->

        >>> tmap.x_period
        11
        >>> (2 + tmap.x_period, 0) in tmap
        True
        >>> (2 + tmap.x_period * 1000, 0) in tmap
        True

    You start on the open square (`.`) in the top-left corner and need to reach the bottom (below
    the bottom-most row on your map). The toboggan can only follow a few specific slopes; start by
    counting all the trees you would encounter for the slope *right 3, down 1*:

    From your starting position at the top-left, check the position that is right 3 and down 1.
    Then, check the position that is right 3 and down 1 from there, and so on until you go past
    the bottom of the map. The locations you'd check in the above example are marked here with `O`
    where there was an open square and `X` where there was a tree:

        ..##.........##.........##........  --->
        #..O#...#..#...#...#..#...#...#..#
        .#....X..#..#....#..#..#....#..#..
        ..#.#...#O#..#.#...#.#..#.#...#.#.
        .#...##..#..X...##..#..#...##..#..
        ..#.##.......#.X#.......#.##......  --->
        .#.#.#....#.#.#.#.O..#.#.#.#....#.
        .#........#.#........X.#........#.
        #.##...#...#.##...#...#.X#...#...#
        #...##....##...##....##...#X....##
        .#..#...#.#.#..#...#.#.#..#...X.#.  --->

        >>> (3, 1) in tmap
        False
        >>> (6, 2) in tmap
        True
        >>> (9, 3) in tmap
        False
        >>> (12, 4) in tmap
        True
        >>> list(tmap.encounter_positions(slope=(3, 1)))
        [(6, 2), (12, 4), (15, 5), (21, 7), (24, 8), (27, 9), (30, 10)]

    In this example, traversing the map using this slope would cause you to encounter *7 trees*.

        >>> tmap.encounter_count(slope=(3, 1))
        7

    Starting at the top-left corner of your map and following a slope of *right 3 and down 1*,
    *how many trees would you encounter?*

        >>> part_1(tmap)
        part 1: encountered 7 tree(s)
        7
    """

    result = trees.encounter_count(slope=(3, 1))
    print(f"part 1: encountered {result} tree(s)")
    return result


def part_2(trees: 'TreesMap'):
    """
    Determine the number of trees you would encounter if, for each of the following slopes,
    you start at the top-left corner and traverse the map all the way to the bottom:

        - Right 1, down 1.
        - Right 3, down 1. (This is the slope you already checked.)
        - Right 5, down 1.
        - Right 7, down 1.
        - Right 1, down 2.

    In the above example, these slopes would find 2, 7, 3, 4, and 2 tree(s) respectively:

        >>> tmap = TreesMap.example_map()
        >>> tmap.encounter_count((1, 1))
        2
        >>> tmap.encounter_count((3, 1))
        7
        >>> tmap.encounter_count((5, 1))
        3
        >>> tmap.encounter_count((7, 1))
        4
        >>> tmap.encounter_count((1, 2))
        2

    Multiplied together, these produce the answer:

        >>> 2 * 7 * 3 * 4 * 2
        336

    *What do you get if you multiply together the number of trees encountered on each of the listed
    slopes?*

        >>> part_2(tmap)
        part 2: encountered 2, 7, 3, 4, and 2 tree(s); product is 336
        336
    """

    slopes = [(1, 1), (3, 1), (5, 1), (7, 1), (1, 2)]
    encounters = [trees.encounter_count(slope) for slope in slopes]
    result = product(encounters)
    print(f"part 2: encountered {join_and(encounters, True)} tree(s); product is {result}")
    return result


Pos = Tuple[int, int]
Vector = Tuple[int, int]


class TreesMap:
    TREE_CHAR = '#'
    OPEN_CHAR = '.'

    def __init__(self, trees: Set[Pos], bounds: Rect):
        self.trees = trees
        self.bounds = bounds

    @classmethod
    def from_file(cls, fn: str):
        return cls.from_lines(open(fn))

    @classmethod
    def from_text(cls, text: str):
        return cls.from_lines(text.strip().split('\n'))

    @classmethod
    def example_map(cls):
        """
        Example map from the instructions so it doesn't have to be repeated in part_2's docstring.
        """

        return cls.from_text('''
            ..##.......
            #...#...#..
            .#....#..#.
            ..#.#...#.#
            .#...##..#.
            ..#.##.....
            .#.#.#....#
            .#........#
            #.##...#...
            #...##....#
            .#..#...#.#
        ''')

    @classmethod
    def from_lines(cls, lines: Iterable[str]):
        height, width = 0, None
        trees = set()

        for y, line in enumerate(lines):
            line = line.strip()
            assert all(ch in (cls.TREE_CHAR, cls.OPEN_CHAR) for ch in line)

            height += 1
            if width is None:
                # width is determined by the length of the first line
                width = len(line)
            else:
                # all lines must have the equal length
                assert width == len(line)

            trees.update(
                (x, y)
                for x, ch in enumerate(line)
                if ch == cls.TREE_CHAR
            )

        return cls(
            trees=trees,
            bounds=Rect.at_origin(width=width, height=height)
        )

    @property
    def x_period(self) -> int:
        # Could be named `width`, but that would be misleading as the map repeats along its x-axis.
        return self.bounds.width

    @property
    def height(self) -> int:
        return self.bounds.height

    def __len__(self):
        return len(self.trees)

    def __contains__(self, pos: Pos):
        # map repeats along its x-axis -> wrap x
        x, y = pos
        return (x % self.x_period, y) in self.trees

    def encounter_positions(self, slope: Vector, start: Pos = (0, 0)) -> Iterable[Pos]:
        x, y = start
        dx, dy = slope
        while y <= self.bounds.bottom_y:
            if (x, y) in self:
                yield x, y
            x, y = x + dx, y + dy

    def encounter_count(self, slope: Vector, start: Pos = (0, 0)) -> int:
        return sum(1 for _ in self.encounter_positions(slope, start))

    def __str__(self):
        # inverse to TreesMap.from_text()
        return '\n'.join(
            ''.join(
                self.TREE_CHAR if (x, y) in self.trees else self.OPEN_CHAR
                for x in self.bounds.range_x()
            )
            for y in self.bounds.range_y()
        )

    def __eq__(self, other):
        return self.trees == other.trees and self.bounds == other.bounds


if __name__ == '__main__':
    trees_map = TreesMap.from_file('data/03-input.txt')
    assert trees_map.x_period == 31
    assert trees_map.height == 323

    part_1(trees_map)
    part_2(trees_map)
