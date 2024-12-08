"""
Advent of Code 2024
Day 8: Resonant Collinearity
https://adventofcode.com/2024/day/8
"""

from itertools import chain, combinations
from typing import Iterable, Self

from common.canvas import Canvas
from common.file import relative_path
from common.iteration import dgroupby_pairs
from common.rect import Rect


def part_1(map_: 'Map') -> int:
    """
    You find yourselves on the roof (y2016/day25_clock.py) of a top-secret Easter Bunny
    installation.

    While The Historians do their thing, you take a look at the familiar **huge antenna**. Much to
    your surprise, it seems to have been reconfigured to emit a signal that makes people 0.1% more
    likely to buy Easter Bunny brand Imitation Mediocre Chocolate as a Christmas gift! Unthinkable!

    Scanning across the city, you find that there are actually many such antennas. Each antenna is
    tuned to a specific **frequency** indicated by a single lowercase letter, uppercase letter,
    or digit. You create a map (your puzzle input) of these antennas. For example:

        >>> example_map_0 = Map.from_text('''
        ...     ............
        ...     ........0...
        ...     .....0......
        ...     .......0....
        ...     ....0.......
        ...     ......A.....
        ...     ............
        ...     ............
        ...     ........A...
        ...     .........A..
        ...     ............
        ...     ............
        ... ''')
        >>> example_map_0.bounds.shape
        (12, 12)
        >>> example_map_0.antennas  # doctest: +ELLIPSIS
        {(8, 1): '0', (5, 2): '0', (7, 3): '0', (4, 4): '0', (6, 5): 'A', ...}
        >>> len(example_map_0.antennas)
        7

    The signal only applies its nefarious effect at specific **antinodes** based on the resonant
    frequencies of the antennas. In particular, an antinode occurs at any point that is perfectly in
    line with two antennas of the same frequency - but only when one of the antennas is twice as far
    away as the other. This means that for any pair of antennas with the same frequency, there are
    two antinodes, one on either side of them.

    So, for these two antennas with frequency `a`, they create the two antinodes marked with `#`:

        >>> example_antennas = {(4, 3): 'a', (5, 5): 'a'}
        >>> example_map_1 = Map(bounds=Rect.at_origin(10, 10), antennas=example_antennas)
        >>> list(example_map_1.antinodes())
        [(3, 1), (6, 7)]
        >>> print(format(example_map_1, '#'))
        ··········
        ···#······
        ··········
        ····a·····
        ··········
        ·····a····
        ··········
        ······#···
        ··········
        ··········

    Adding a third antenna with the same frequency creates several more antinodes. It would ideally
    add four antinodes, but two are off the right side of the map, so instead it adds only two:

        >>> example_antennas[(8, 4)] = 'a'
        >>> example_map_2 = Map(bounds=Rect.at_origin(10, 10), antennas=example_antennas)
        >>> print(format(example_map_2, '#'))
        ··········
        ···#······
        #·········
        ····a·····
        ········a·
        ·····a····
        ··#·······
        ······#···
        ··········
        ··········
        >>> list(example_map_2.antinodes())
        [(3, 1), (6, 7), (0, 2), (2, 6)]

    Antennas with different frequencies don't create antinodes; A and a count as different
    frequencies. However, antinodes **can** occur at locations that contain antennas. In this
    diagram, the lone antenna with frequency `A` creates no antinodes but has a `a`-frequency
    antinode at its location:

        >>> example_antennas[(6, 7)] = 'A'
        >>> example_map_3 = Map(bounds=Rect.at_origin(10, 10), antennas=example_antennas)
        >>> print(format(example_map_3, '#'))
        ··········
        ···#······
        #·········
        ····a·····
        ········a·
        ·····a····
        ··#·······
        ······A···
        ··········
        ··········
        >>> list(example_map_3.antinodes())
        [(3, 1), (6, 7), (0, 2), (2, 6)]


    The first example has antennas with two different frequencies, so the antinodes they create look
    like this, plus an antinode overlapping the topmost `A`-frequency antenna:

        >>> print(format(example_map_0, '#'))
        ······#····#
        ···#····0···
        ····#0····#·
        ··#····0····
        ····0····#··
        ·#····A·····
        ···#········
        #······#····
        ········A···
        ·········A··
        ··········#·
        ··········#·
        >>> (6, 5) in example_map_0.antinodes()
        True

    Because the topmost `A`-frequency antenna overlaps with a `0`-frequency antinode, there are
    **`14`** total unique locations that contain an antinode within the bounds of the map:

        >>> len(set(example_map_0.antinodes()))
        14

    Calculate the impact of the signal.
    **How many unique locations within the bounds of the map contain an antinode?**

        >>> part_1(example_map_0)
        part 1: map contains 14 antinodes
        14
    """

    result = len(set(map_.antinodes()))

    print(f"part 1: map contains {result} antinodes")
    return result


def part_2(map_: 'Map') -> int:
    """
    Watching over your shoulder as you work, one of The Historians asks if you took the effects of
    resonant harmonics into your calculations.

    Whoops!

    After updating your model, it turns out that an antinode occurs at **any grid position** exactly
    in line with at least two antennas of the same frequency, regardless of distance. This means
    that some of the new antinodes will occur at the position of each antenna (unless that antenna
    is the only one of its frequency).

    So, these three `T`-frequency antennas now create many antinodes:

        >>> example_map_1 = Map(Rect.at_origin(10, 10), {(0, 0): 'T', (3, 1): 'T', (1, 2): 'T'})
        >>> print(format(example_map_1, '##'))
        T····#····
        ···T······
        ·T····#···
        ·········#
        ··#·······
        ··········
        ···#······
        ··········
        ····#·····
        ··········

    In fact, the three `T`-frequency antennas are all exactly in line with two antennas, so they are
    all also antinodes! This brings the total number of antinodes in the above example to **`9`**:

        >>> len(set(example_map_1.antinodes(multi=True)))
        9

    The original example now has **`34`** antinodes, including the antinodes that appear on every
    antenna:

        >>> example_map_0 = Map.from_file('data/08-example.txt')
        >>> print(format(example_map_0, '##'))
        ##····#····#
        ·#·#····0···
        ··#·#0····#·
        ··##···0····
        ····0····#··
        ·#···#A····#
        ···#··#·····
        #····#·#····
        ··#·····A···
        ····#····A··
        ·#········#·
        ···#······##
        >>> len(set(example_map_0.antinodes(multi=True)))
        34

    Calculate the impact of the signal using this updated model.
    **How many unique locations within the bounds of the map contain an antinode?**

        >>> part_2(example_map_0)
        part 2: map contains 34 antinodes
        34
    """

    result = len(set(map_.antinodes(multi=True)))

    print(f"part 2: map contains {result} antinodes")
    return result


Pos = tuple[int, int]


class Map:

    def __init__(self, bounds: Rect, antennas: dict[Pos, str]):
        self.bounds = bounds
        self.antennas = dict(antennas)

    def antinodes(self, multi: bool = False) -> Iterable[Pos]:
        # group antennas by frequence
        antennas_by_frequency = dgroupby_pairs((freq, pos) for pos, freq in self.antennas.items())
        return (
            antinode
            for freq, antennas in antennas_by_frequency.items()
            # for each pair of same-frequency antennas ...
            for a_1, a_2 in combinations(antennas, 2)
            # create one of multiple antinodes for each direction
            for antinode in chain(
                self._calculate_antinodes(a_1, a_2, multi),
                self._calculate_antinodes(a_2, a_1, multi),
            )
        )

    def _calculate_antinodes(self, antenna_1: Pos, antenna_2: Pos, multi: bool) -> Iterable[Pos]:
        (x_1, y_1), (x_2, y_2) = antenna_1, antenna_2
        dx, dy = x_1 - x_2, y_1 - y_2
        if multi:
            x, y = x_1, y_1
            while (x, y) in self.bounds:
                yield x, y
                x, y = x + dx, y + dy
        else:
            x, y = x_1 + dx, y_1 + dy
            if (x, y) in self.bounds:
                yield x, y

    def __format__(self, format_spec: str) -> str:
        canvas = Canvas(bounds=self.bounds)

        # optionally draw antinodes: '#' for singles (part 1) and '##' for multiple (part 2)
        if format_spec in ('#', '##'):
            multi = (format_spec == '##')
            canvas.draw_many((antinode_pos, '#') for antinode_pos in self.antinodes(multi))

        # draw antennas (possibly drawing over antinodes)
        canvas.draw_many(self.antennas)

        return canvas.render(empty_char='·')

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        antennas: dict[Pos, str] = {}
        width, height = 0, 0

        for y, line in enumerate(lines):
            for x, char in enumerate(line.strip()):
                if char not in ('.', '·'):
                    antennas[(x, y)] = char
                if x >= width:
                    width = x + 1
            height = y + 1

        return cls(bounds=Rect.at_origin(width, height), antennas=antennas)


def main(input_fn: str = 'data/08-input.txt') -> tuple[int, int]:
    map_ = Map.from_file(input_fn)
    result_1 = part_1(map_)
    result_2 = part_2(map_)
    return result_1, result_2


if __name__ == '__main__':
    main()
