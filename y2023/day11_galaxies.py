"""
Advent of Code 2023
Day 11: Cosmic Expansion
https://adventofcode.com/2023/day/11
"""

from itertools import combinations
from typing import Iterable

from common.file import relative_path
from common.rect import Rect


def part_1(universe: 'Universe') -> int:
    """
    You continue following signs for "Hot Springs" and eventually come across an observatory.
    The Elf within turns out to be a researcher studying cosmic expansion using the giant telescope
    here.

    He doesn't know anything about the missing machine parts; he's only visiting for this research
    project. However, he confirms that the hot springs are the next-closest area likely to have
    people; he'll even take you straight there once he's done with today's observation analysis.

    Maybe you can help him with the analysis to speed things up?

    The researcher has collected a bunch of data and compiled the data into a single giant **image**
    (your puzzle input). The image includes **empty space** (`·`) and **galaxies** (`#`).
    For example:

        >>> universe_initial = Universe.from_text('''
        ...     ...#......
        ...     .......#..
        ...     #.........
        ...     ..........
        ...     ......#...
        ...     .#........
        ...     .........#
        ...     ..........
        ...     .......#..
        ...     #...#.....
        ... ''')

    The researcher is trying to figure out the sum of the lengths of the **shortest path between
    every pair of galaxies**. However, there's a catch: the universe expanded in the time it took
    the light from those galaxies to reach the observatory.

    Due to something involving gravitational effects, **only some space expands**.
    In fact, the result is that **any rows or columns that contain no galaxies** should all actually
    be twice as big.

    In the above example, three columns and two rows contain no galaxies:

        >>> print(format(universe_initial, 'expansions'))
           v  v  v
         ···#······
         ·······#··
         #·········
        >··········<
         ······#···
         ·#········
         ·········#
        >··········<
         ·······#··
         #···#·····
           ^  ^  ^

    These rows and columns need to be **twice as big**; the result of cosmic expansion therefore
    looks like this:

        >>> print(universe_expanded := universe_initial.expanded())
        ····#········
        ·········#···
        #············
        ·············
        ·············
        ········#····
        ·#···········
        ············#
        ·············
        ·············
        ·········#···
        #····#·······

    Equipped with this expanded universe, the shortest path between every pair of galaxies can be
    found. It can help to assign every galaxy a unique number:

        >>> print(format(universe_expanded, 'labels'))
        ····0········
        ·········1···
        2············
        ·············
        ·············
        ········3····
        ·4···········
        ············5
        ·············
        ·············
        ·········6···
        7····8·······

    In these 9 galaxies, there are **36 pairs**.

        >>> len(universe_expanded)
        9
        >>> len(list(universe_expanded.pairs()))
        36

    Only count each pair once; order within the pair doesn't matter. For each pair, find any
    shortest path between the two galaxies using only steps that move up, down, left, or right
    exactly one `.` or `#` at a time. (The shortest path between two galaxies is allowed to pass
    through another galaxy.)

    For example, here is one of the shortest paths between galaxies `4` and `8`:

        ····0········
        ·········1···
        2············
        ·············
        ·············
        ········3····
        ·4···········
        ·##·········5
        ··##·········
        ···##········
        ····##···6···
        7····8·······

    This path has length **`9`** because it takes a minimum of **nine steps** to get from galaxy `4`
    to galaxy `8` (the eight locations marked `#` plus the step onto galaxy `8` itself).

        >>> universe_expanded.distance(4, 8)
        9

    Here are some other examples of shortest path lengths:

        >>> universe_expanded.distance(0, 6)
        15
        >>> universe_expanded.distance(2, 5)
        17
        >>> universe_expanded.distance(7, 8)
        5

    In this example, after expanding the universe, the sum of the shortest path between all 36 pairs
    of galaxies is **`374`**.

        >>> sum(universe_expanded.pair_distances())
        374

    Expand the universe, then find the length of the shortest path between every pair of galaxies.
    **What is the sum of these lengths?**

        >>> part_1(universe_initial)
        part 1: after expanding, paths between galaxies sum to 374
        374
    """

    result = sum(universe.expanded().pair_distances())

    print(f"part 1: after expanding, paths between galaxies sum to {result}")
    return result


def part_2(universe: 'Universe', expansion_factor: int = 1_000_000) -> int:
    """
    The galaxies are much **older** (and thus much **farther apart**) than the researcher initially
    estimated.

    Now, instead of the expansion you did before, make each empty row or column **one million
    times** larger. That is, each empty row should be replaced with `1_000_000` empty rows, and each
    empty column should be replaced with `1_000_000` empty columns.

    In the example above, if each empty row or column were merely `10` times larger, the sum of the
    shortest paths between every pair of galaxies would be:

        >>> universe_initial = Universe.from_file('data/11-example.txt')
        >>> sum(universe_initial.expanded(factor=10).pair_distances())
        1030

    And if each empty row or column were merely `100` times larger, the sum of the shortest paths
    between every pair of galaxies would be:

        >>> sum(universe_initial.expanded(factor=100).pair_distances())
        8410

    However, your universe will need to expand far beyond these values.

    Starting with the same initial image, expand the universe according to these new rules,
    then find the length of the shortest path between every pair of galaxies.
    **What is the sum of these lengths?**

        >>> part_2(universe_initial, expansion_factor=100)
        part 2: after expanding x100, paths between galaxies sum to 8410
        8410
    """

    result = sum(universe.expanded(expansion_factor).pair_distances())

    print(f"part 2: after expanding x{expansion_factor}, paths between galaxies sum to {result}")
    return result


Pos = tuple[int, int]


def manhattan_distance(pos_0: Pos, pos_1: Pos) -> int:
    (x_0, y_0), (x_1, y_1) = pos_0, pos_1
    return abs(x_0 - x_1) + abs(y_0 - y_1)


class Universe:
    def __init__(self, galaxies: Iterable[Pos]):
        self.galaxies = list(galaxies)
        self.bounds = Rect.with_all(self.galaxies)

    def __len__(self) -> int:
        return len(self.galaxies)

    def empty_columns(self) -> Iterable[int]:
        occupied_columns = {x for x, _ in self.galaxies}
        return (x for x in self.bounds.range_x() if x not in occupied_columns)

    def empty_rows(self) -> Iterable[int]:
        occupied_rows = {y for _, y in self.galaxies}
        return (y for y in self.bounds.range_y() if y not in occupied_rows)

    def expanded(self, factor: int = 2) -> 'Universe':
        def expanded_values(val_range: range, empties: Iterable[int]) -> Iterable[int]:
            empties_set = set(empties)
            offset = 0
            for val in val_range:
                if val in empties_set:
                    offset += factor - 1
                yield val + offset

        xs1 = list(expanded_values(self.bounds.range_x(), self.empty_columns()))
        ys1 = list(expanded_values(self.bounds.range_y(), self.empty_rows()))

        return type(self)((xs1[x], ys1[y]) for x, y in self.galaxies)

    def distance(self, index_0: int, index_1: int) -> int:
        pos_0, pos_1 = self.galaxies[index_0], self.galaxies[index_1]
        return manhattan_distance(pos_0, pos_1)

    def pairs(self) -> Iterable[tuple[Pos, Pos]]:
        return combinations(self.galaxies, 2)

    def pair_distances(self) -> Iterable[int]:
        return (
            manhattan_distance(pos_0, pos_1)
            for pos_0, pos_1 in self.pairs()
        )

    def __str__(self) -> str:
        return format(self, '')

    def __format__(self, format_spec: str) -> str:
        format_parts = format_spec.split(',')
        show_expansions = 'expansions' in format_parts
        show_labels = 'labels' in format_parts

        bounds = self.bounds
        canvas = {pos: '·' for pos in bounds}

        # draw galaxies (# or labels)
        canvas.update(
            (pos, str(num)[-1] if show_labels else '#')
            for num, pos in enumerate(self.galaxies)
        )

        # draw expansions
        if show_expansions:
            bounds = bounds.grow_by(1, 1)
            for x in self.empty_columns():
                canvas[(x, bounds.top_y)] = 'v'
                canvas[(x, bounds.bottom_y)] = '^'
            for y in self.empty_rows():
                canvas[(bounds.left_x, y)] = '>'
                canvas[(bounds.right_x, y)] = '<'

        return '\n'.join(
            ''.join(canvas.get((x, y), ' ') for x in bounds.range_x()).rstrip()
            for y in bounds.range_y()
        )

    @classmethod
    def from_file(cls, fn: str) -> 'Universe':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text: str) -> 'Universe':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Universe':
        return cls(
            (x, y)
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
            if char == '#'
        )


def main(input_fn: str = 'data/11-input.txt') -> tuple[int, int]:
    universe = Universe.from_file(input_fn)
    result_1 = part_1(universe)
    result_2 = part_2(universe)
    return result_1, result_2


if __name__ == '__main__':
    main()
