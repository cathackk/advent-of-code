"""
Advent of Code 2017
Day 21: Fractal Art
https://adventofcode.com/2017/day/21
"""

from typing import Callable, Iterable, Iterator, Self

from common.iteration import dgroupby_pairs, single_value
from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(rulebook: 'RuleBook', iterations: int = 5) -> int:
    """
    You find a program trying to generate some art. It uses a strange process that involves
    repeatedly enhancing the detail of an image through a set of rules.

    The image consists of a two-dimensional square grid of pixels that are either on (`#`) or off
    (`·`). The program always begins with this pattern:

        >>> print(STARTING_PATTERN)
        ·#·
        ··#
        ###

    Because the pattern is both `3` pixels wide and `3` pixels tall, it is said to have a **size**
    of `3`.

    Then, the program repeats the following process:

      - If the size is evenly divisible by `2`, break the pixels up into `2x2` squares, and convert
        each `2x2` square into a `3x3` square by following the corresponding **enhancement rule**.
      - Otherwise, the size is evenly divisible by `3`; break the pixels up into `3x3` squares, and
        convert each `3x3` square into a `4x4` square by following the corresponding **enhancement
        rule**.

    Because each square of pixels is replaced by a larger one, the image gains pixels and so its
    **size** increases.

    The artist's book of enhancement rules is nearby (your puzzle input); however, it seems to be
    missing rules. The artist explains that sometimes, one must **rotate** or **flip** the input
    pattern to find a match. (Never rotate or flip the output pattern, though.) Each pattern is
    written concisely: rows are listed as single units, ordered top-down, and separated by slashes.
    For example, the following rules correspond to the adjacent patterns:

        ··/·#  =  ··
                  ·#

                        ·#·
        ·#·/··#/###  =  ··#
                        ###

                                #··#
        #··#/····/#··#/·##·  =  ····
                                #··#
                                ·##·

    When searching for a rule to use, rotate and flip the pattern as necessary. For example, all of
    the following patterns match the same rule:

        >>> print(STARTING_PATTERN)
        ·#·
        ··#
        ###
        >>> print(STARTING_PATTERN.flipped_x())
        ·#·
        #··
        ###
        >>> print(STARTING_PATTERN.rotated(1))
        #··
        #·#
        ##·
        >>> print(STARTING_PATTERN.flipped_y())
        ###
        ··#
        ·#·

    Suppose the book contained the following two rules:

        >>> example_rules = RuleBook.from_text('''
        ...     ../.# => ##./#../...
        ...     .#./..#/### => #..#/..../..../#..#
        ... ''')
        >>> example_rules  # doctest: +NORMALIZE_WHITESPACE
        RuleBook([Rule(grid_from=Grid(size=2, pixels=[(1, 1)]),
                         grid_to=Grid(size=3, pixels=[(0, 0), (0, 1), (1, 0)])),
                  Rule(grid_from=Grid(size=3, pixels=[(0, 2), (1, 0), (1, 2), (2, 1), (2, 2)]),
                         grid_to=Grid(size=4, pixels=[(0, 0), (0, 3), (3, 0), (3, 3)]))])


    As before, the program begins with this pattern:

        >>> pattern_0 = STARTING_PATTERN
        >>> print(pattern_0)
        ·#·
        ··#
        ###
        >>> pattern_0.size
        3

    The size of the grid (`3`) is not divisible by `2`, but it is divisible by `3`. It divides
    evenly into a single square:

        >>> subgrids_0 = list(pattern_0.divide())
        >>> len(subgrids_0)
        1
        >>> subgrids_0[0][1] == pattern_0
        True

    The square matches the second rule:

        >>> example_rules.matching_rule(pattern_0)  # doctest: +ELLIPSIS
        Rule(grid_from=Grid(size=3, ...))

    Which produces:

        >>> print(pattern_1 := example_rules.expand(pattern_0))
        #··#
        ····
        ····
        #··#
        >>> pattern_1.size
        4

    The size of this enhanced grid (`4`) is evenly divisible by `2`, so that rule is used.
    It divides evenly into four squares:

        >>> print_subgrids(subgrids_1 := list(pattern_1.divide()))
        #·|·#
        ··|··
        --+--
        ··|··
        #·|·#

    Each of these squares matches the same rule:

        >>> rule_1 = single_value(set(example_rules.matching_rule(grid) for _, grid in subgrids_1))
        >>> rule_1  # doctest: +ELLIPSIS
        Rule(grid_from=Grid(size=2, ...))

    ... three of which require some flipping and rotation to line up with the rule. The output for
    the rule is the same in all four cases:

        >>> print_subgrids(((x, y), rule_1.grid_to) for x in (0, 3) for y in (0, 3))
        ##·|##·
        #··|#··
        ···|···
        ---+---
        ##·|##·
        #··|#··
        ···|···

    Finally, the squares are joined into a new grid:

        >>> print(pattern_2 := example_rules.expand(pattern_1))
        ##·##·
        #··#··
        ······
        ##·##·
        #··#··
        ······

    Which could be further split into:

        >>> print_subgrids(pattern_2.divide())
        ##|·#|#·
        #·|·#|··
        --+--+--
        ··|··|··
        ##|·#|#·
        --+--+--
        #·|·#|··
        ··|··|··

    Thus, after 2 iterations, the grid contains 12 pixels that are on:

        >>> len(pattern_2.pixels)
        12

    **How many pixels stay on** after 5 iterations?

        >>> part_1(example_rules, iterations=2)
        part 1: after 2 iterations, there will be 12 pixels on
        12
    """

    pattern = STARTING_PATTERN
    for _ in range(iterations):
        pattern = rulebook.expand(pattern)

    pixels_on = len(pattern.pixels)

    print(f"part 1: after {iterations} iterations, there will be {pixels_on} pixels on")
    return pixels_on


def part_2(rulebook: 'RuleBook', iterations: int = 18) -> int:
    """
    **How many pixels stay on** after 18 iterations?
    """

    pixels_on = count_pixels(STARTING_PATTERN, rulebook, iterations)
    print(f"part 2: after {iterations} iterations, there will be {pixels_on} pixels on")
    return pixels_on


Pos = tuple[int, int]
Transformation = Callable[[int, int], Pos]


class Grid:
    def __init__(self, size: int, pixels: Iterable[Pos]):
        self.size = size
        self.pixels = set(pixels)
        for x, y in self.pixels:
            assert x in range(self.size)
            assert y in range(self.size)

    def __repr__(self) -> str:
        return f'{type(self).__name__}(size={self.size}, pixels={sorted(self.pixels)!r})'

    def str_lines(self) -> Iterable[str]:
        return (
            ''.join('#' if (x, y) in self.pixels else '·' for x in range(self.size))
            for y in range(self.size)
        )

    def __str__(self):
        return format(self)

    def __format__(self, format_spec: str) -> str:
        return (format_spec or "\n").join(self.str_lines())

    @classmethod
    def from_line(cls, line: str) -> Self:
        rows = line.split('/')
        size = len(rows)
        assert all(len(row) == size for row in rows), line
        return cls(
            size,
            ((x, y) for y, row in enumerate(rows) for x, char in enumerate(row) if char == '#')
        )

    def __int__(self):
        return sum(
            1 << (x + y * self.size)
            for x, y in self.pixels
        )

    def __eq__(self, other):
        return (
            isinstance(other, type(self))
            and self.size == other.size
            and int(self) == int(other)
        )

    def __hash__(self):
        return hash((self.size, int(self)))

    def _transformed(self, trans: Transformation) -> Self:
        def trm(x: int, y: int) -> Pos:
            x, y = trans(x, y)
            return x % self.size, y % self.size

        return type(self)(
            size=self.size,
            pixels=(trm(x, y) for x, y in self.pixels)
        )

    def rotated(self, rotations: int) -> Self:
        """
        0 -> no rotation
        1 -> 90° clockwise
        2 -> 180°
        3 -> 90° counter-clockwise
        """
        rotations %= 4
        if rotations == 0:
            return self
        elif rotations == 1:
            return self._transformed(lambda x, y: (-y-1, x))
        elif rotations == 2:
            return self._transformed(lambda x, y: (-x-1, -y-1))
        elif rotations == 3:
            return self._transformed(lambda x, y: (y, -x-1))
        else:
            raise ValueError(rotations)

    def flipped_x(self) -> Self:
        return self._transformed(lambda x, y: (-x-1, y))

    def flipped_y(self) -> Self:
        return self._transformed(lambda x, y: (x, -y-1))

    def variants(self) -> Iterable[Self]:
        flipped = self.flipped_x()
        for r in range(4):
            yield self.rotated(r)
            yield flipped.rotated(r)

    def normalized(self) -> Self:
        return min(self.variants(), key=int)

    def divide(self) -> Iterable[tuple[Pos, Self]]:
        if self.size % 2 == 0:
            return self.subgrids(2)
        elif self.size % 3 == 0:
            return self.subgrids(3)
        else:
            raise ValueError(f"grid size {self.size} not divisible by 2 or 3")

    def subgrids(self, subsize: int) -> Iterable[tuple[Pos, Self]]:
        assert self.size % subsize == 0

        if self.size == subsize:
            return [((0, 0), self)]

        subpixels = dgroupby_pairs(
            (
                # top-left corner of the subgrid
                (sub_x := (x // subsize) * subsize, sub_y := (y // subsize) * subsize),
                # position in the new subgrid
                (x - sub_x, y - sub_y)
            )
            for x, y in self.pixels
        )

        return (
            ((sub_pos := (sub_x, sub_y)), type(self)(subsize, subpixels.get(sub_pos, ())))
            for sub_y in range(0, self.size, subsize)
            for sub_x in range(0, self.size, subsize)
        )

    @classmethod
    def join(cls, subgrids: Iterable[tuple[Pos, Self]]) -> Self:
        subgrids_dict = dict(subgrids)

        sub_size = single_value(set(sg.size for sg in subgrids_dict.values()))
        max_x = max(x for x, _ in subgrids_dict.keys())
        max_y = max(y for _, y in subgrids_dict.keys())
        assert max_x % sub_size == 0
        assert max_y % sub_size == 0

        return cls(
            size=max(max_x, max_y) + sub_size,
            pixels=(
                (cx + x, cy + y)
                for (cx, cy), sg in subgrids_dict.items()
                for x, y in sg.pixels
            )
        )


STARTING_PATTERN = Grid.from_line('.#./..#/###')


class Rule:
    def __init__(self, grid_from: Grid, grid_to: Grid):
        assert grid_from.size + 1 == grid_to.size
        self.grid_from = grid_from
        self.grid_to = grid_to

    def __repr__(self) -> str:
        return f'{type(self).__name__}(grid_from={self.grid_from!r}, grid_to={self.grid_to!r})'

    def __str__(self):
        return f"{self.grid_from:/} => {self.grid_to:/}"

    @classmethod
    def from_str(cls, line: str) -> Self:
        # "../.# => ##./#../..."
        g_from, g_to = parse_line(line.strip(), "$ => $")
        return cls(Grid.from_line(g_from), Grid.from_line(g_to))


class RuleBook:
    def __init__(self, rules: Iterable[Rule]):
        self.rdict: dict[int, Rule] = {
            hash(rule.grid_from.normalized()): rule
            for rule in rules
        }

    def __repr__(self) -> str:
        return f'{type(self).__name__}({list(self)!r})'

    def __len__(self) -> int:
        return len(self.rdict)

    def __iter__(self) -> Iterator[Rule]:
        return iter(self.rdict.values())

    def matching_rule(self, grid: Grid) -> Rule:
        grid_id = hash(grid.normalized())
        if grid_id not in self.rdict:
            raise KeyError(f"no rule for {grid!r}")
        return self.rdict[grid_id]

    def expand(self, grid: Grid) -> Grid:
        return Grid.join(self._expanded_subgrids(grid))

    def _expanded_subgrids(self, grid: Grid) -> Iterable[tuple[Pos, Grid]]:
        for (c_x, c_y), subgrid in grid.divide():
            matching_rule = self.matching_rule(subgrid)
            expanded_subgrid = matching_rule.grid_to
            assert expanded_subgrid.size == subgrid.size + 1
            ecx = (c_x // subgrid.size) * expanded_subgrid.size
            ecy = (c_y // subgrid.size) * expanded_subgrid.size
            yield (ecx, ecy), expanded_subgrid

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(fn))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        return cls(Rule.from_str(line) for line in lines)


def count_pixels(grid: Grid, rulebook: RuleBook, steps: int) -> int:
    """
    Optimized method for recursively calculating pixels count
    after large number of expansion steps (tested up to 900).

    Note: Working only for starting grids 3x3 and steps divisible by 3.
    """

    # optimized only for these values:
    assert grid.size == 3
    assert steps % 3 == 0

    # dictionary of grids by their codes
    code_to_grid: dict[int, Grid] = {int(grid): grid}
    # code of 3x3 grid -> 9 subresult codes (nine 3x3 subresults after three-steps expansion)
    expand_cache: dict[int, list[int]] = {}
    # (code, steps) -> pixels_count
    pixels_count_cache: dict[tuple[int, int], int] = {(int(grid), 0): len(grid.pixels)}

    def _expand_to_nine_subgrids(grid3: Grid) -> list[Grid]:
        key = int(grid3)
        if key not in expand_cache:
            # expand in three steps from 3x3 -> 9x9
            assert grid.size == 3
            grid4 = rulebook.expand(grid3)
            assert grid4.size == 4
            grid6 = rulebook.expand(grid4)
            assert grid6.size == 6
            grid9 = rulebook.expand(grid6)
            assert grid9.size == 9
            # ... yielding nine 3x3 subresults
            subgrids = list(sg for _, sg in grid9.divide())
            assert len(subgrids) == 9

            # store subresults codes
            subgrids_codes = [int(sg) for sg in subgrids]
            # ... into expansion cache,
            expand_cache[key] = subgrids_codes
            for subgrid_code, subgrid in zip(subgrids_codes, subgrids):
                if subgrid_code not in code_to_grid:
                    # ... dictionary,
                    code_to_grid[subgrid_code] = subgrid
                    # ... and pixels count cache
                    pixels_count_cache[(subgrid_code, 0)] = len(subgrid.pixels)

        return [code_to_grid[h] for h in expand_cache[key]]

    def _pixels_count(grid3: Grid, in_steps: int) -> int:
        key = (int(grid3), in_steps)
        if key not in pixels_count_cache:
            assert in_steps % 3 == 0
            assert in_steps >= 0
            pixels_count_cache[key] = sum(
                _pixels_count(sg, in_steps - 3)
                for sg in _expand_to_nine_subgrids(grid3)
            )
        return pixels_count_cache[key]

    return _pixels_count(grid, steps)


def print_subgrids(subgrids: Iterable[tuple[Pos, Grid]]) -> None:
    subgrids_dict = dict(subgrids)
    super_xs = sorted(set(x for x, _ in subgrids_dict.keys()))
    super_ys = sorted(set(y for _, y in subgrids_dict.keys()))
    subgrid_size = single_value(set(subgrid.size for subgrid in subgrids_dict.values()))
    separator = "+".join("-" * subgrid_size for _ in super_xs)

    for y in super_ys:
        if y > 0:
            print(separator)
        for rows in zip(*(subgrids_dict[x, y].str_lines() for x in super_xs)):
            print("|".join(rows))


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    rulebook = RuleBook.from_file(input_path)
    result_1 = part_1(rulebook)
    result_2 = part_2(rulebook)
    return result_1, result_2


if __name__ == '__main__':
    main()
