"""
Advent of Code 2024
Day 10: Hoof It
https://adventofcode.com/2024/day/10
"""

from typing import Iterable, Self

from common.file import relative_path
from common.heading import Heading
from common.rect import Rect


def part_1(map_: 'Map') -> int:
    """
    You all arrive at a Lava Production Facility (y2023/day15_lenses.py) on a floating island in
    the sky. As the others begin to search the massive industrial complex, you feel a small nose
    boop your leg and look down to discover a reindeer wearing a hard hat.

    The reindeer is holding a book titled "Lava Island Hiking Guide". However, when you open
    the book, you discover that most of it seems to have been scorched by lava! As you're about
    to ask how you can help, the reindeer brings you a blank topographic map of the surrounding area
    (your puzzle input) and looks up at you excitedly.

    Perhaps you can help fill in the missing hiking trails?

    The topographic map indicates the **height** at each position using a scale from `0` (lowest)
    to `9` (highest). For example:

        >>> example_0 = Map.from_text('''
        ...     0123
        ...     1234
        ...     8765
        ...     9876
        ... ''')
        >>> example_0.bounds.shape
        (4, 4)
        >>> example_0[1, 2]
        7

    Based on un-scorched scraps of the book, you determine that a good hiking trail is **as long as
    possible** and has an **even, gradual, uphill slope**. For all practical purposes, this means
    that a **hiking trail** is any path that starts at height `0`, ends at height `9`, and always
    increases by a height of exactly 1 at each step. Hiking trails never include diagonal steps -
    only up, down, left, or right (from the perspective of the map).

    You look up from the map and notice that the reindeer has helpfully begun to construct a small
    pile of pencils, markers, rulers, compasses, stickers, and other equipment you might need to
    update the map with hiking trails.

    A **trailhead** is any position that starts one or more hiking trails; these positions will
    always have height `0`. Assembling more fragments of pages, you establish that a trailhead's
    **score** is the number of `9`-height positions reachable from that trailhead via a hiking
    trail. In the above example, the single trailhead in the top left corner has a score of `1`
    because it can reach a single `9` (the one in the bottom left).

        >>> example_0.trailhead_score((0, 0))
        1

    This trailhead has a score of `2`:

        >>> example_1 = Map.from_text('''
        ...     ...0...
        ...     ...1...
        ...     ...2...
        ...     6543456
        ...     7.....7
        ...     8.....8
        ...     9.....9
        ... ''')
        >>> example_1.trailhead_score((3, 0))
        2

    (The positions marked `.` are impassable tiles to simplify these examples; they do not appear on
    your actual topographic map.)

    This trailhead has a score of `4` because every `9` is reachable via a hiking trail except the
    one immediately to the left of the trailhead:

        >>> example_2 = Map.from_text('''
        ...     ..90..9
        ...     ...1.98
        ...     ...2..7
        ...     6543456
        ...     765.987
        ...     876....
        ...     987....
        ... ''')
        >>> example_2.trailhead_score((3, 0))
        4

    This topographic map contains **two** trailheads; the trailhead at the top has a score of `1`,
    while the trailhead at the bottom has a score of `2`:

        >>> example_3 = Map.from_text('''
        ...     10..9..
        ...     2...8..
        ...     3...7..
        ...     4567654
        ...     ...8..3
        ...     ...9..2
        ...     .....01
        ... ''')
        >>> list(example_3.trailheads())
        [(1, 0), (5, 6)]
        >>> example_3.trailhead_score((1, 0))
        1
        >>> example_3.trailhead_score((5, 6))
        2

    Here's a larger example:

        >>> example_4 = Map.from_text('''
        ...     89010123
        ...     78121874
        ...     87430965
        ...     96549874
        ...     45678903
        ...     32019012
        ...     01329801
        ...     10456732
        ... ''')

    This larger example has 9 trailheads.

        >>> len(list(example_4.trailheads()))
        9

    Considering the trailheads in reading order, they have scores of:

        >>> [example_4.trailhead_score(th) for th in example_4.trailheads()]
        [5, 6, 5, 3, 1, 3, 5, 3, 5]

    Adding these scores together, the sum of the scores of all trailheads is **`36`**:

        >>> sum(_)
        36

    The reindeer gleefully carries over a protractor and adds it to the pile.
    **What is the sum of the scores of all trailheads on your topographic map?**

        >>> part_1(example_4)
        part 1: 9 trailheads have total score 36
        36
    """

    trailheads = list(map_.trailheads())
    result = sum(map_.trailhead_score(th) for th in trailheads)

    print(f"part 1: {len(trailheads)} trailheads have total score {result}")
    return result


def part_2(map_: 'Map') -> int:
    """
    The reindeer spends a few minutes reviewing your hiking trail map before realizing something,
    disappearing for a few minutes, and finally returning with yet another slightly-charred piece
    of paper.

    The paper describes a second way to measure a trailhead called its **rating**. A trailhead's
    rating is the **number of distinct hiking trails** which begin at that trailhead. For example:

        >>> example_0 = Map.from_text('''
        ...     .....0.
        ...     ..4321.
        ...     ..5..2.
        ...     ..6543.
        ...     ..7..4.
        ...     ..8765.
        ...     ..9....
        ... ''')

    The above map has a single trailhead:

        >>> list(example_0.trailheads())
        [(5, 0)]

    Its rating is `3`:

        >>> example_0.trailhead_rating((5, 0))
        3

    Because there are exactly three distinct hiking trails which begin at that position:

        >>> example_0.print_trails(example_0.trails((5, 0)))
        ·····0·   ·····0·   ·····0·
        ·····1·   ·····1·   ··4321·
        ·····2·   ·····2·   ··5····
        ·····3·   ··6543·   ··6····
        ·····4·   ··7····   ··7····
        ··8765·   ··8····   ··8····
        ··9····   ··9····   ··9····

    Here is a map containing a single trailhead with rating `13`:

        >>> example_1 = Map.from_text('''
        ...     ..90..9
        ...     ...1.98
        ...     ...2..7
        ...     6543456
        ...     765.987
        ...     876....
        ...     987....
        ... ''')
        >>> list(example_1.trailheads())
        [(3, 0)]
        >>> example_1.trailhead_rating((3, 0))
        13

    This map contains a single trailhead with rating `227` (because there are `121` distinct hiking
    trails that lead to the `9` on the right edge and `106` that lead to the `9` on the bottom):

        >>> example_2 = Map.from_text('''
        ...     012345
        ...     123456
        ...     234567
        ...     345678
        ...     4.6789
        ...     56789.
        ... ''')
        >>> example_2.trailhead_rating((0, 0))
        227

    Here's the larger example from before:

        >>> example_3 = Map.from_file('data/10-example.txt')
        >>> print(example_3)
        89010123
        78121874
        87430965
        96549874
        45678903
        32019012
        01329801
        10456732

    Considering its trailheads in reading order, they have ratings of:

        >>> [example_3.trailhead_rating(th) for th in example_3.trailheads()]
        [20, 24, 10, 4, 1, 4, 5, 8, 5]

    The sum of all trailhead ratings in this larger example topographic map is **`81`**:

        >>> sum(_)
        81

    You're not sure how, but the reindeer seems to have crafted some tiny flags out of toothpicks
    and bits of paper and is using them to mark trailheads on your topographic map.
    **What is the sum of the ratings of all trailheads?**

        >>> part_2(example_3)
        part 2: 9 trailheads have total score 81
        81
    """

    trailheads = list(map_.trailheads())
    result = sum(map_.trailhead_rating(th) for th in trailheads)

    print(f"part 2: {len(trailheads)} trailheads have total score {result}")
    return result


Pos = tuple[int, int]
Trail = list[Pos]


class Map:

    def __init__(self, bounds: Rect, heights: dict[Pos, int]):
        self.bounds = bounds
        self.heights = dict(heights)
        assert all(pos in bounds for pos in self.heights)

    def __contains__(self, pos: Pos) -> bool:
        return pos in self.heights

    def __getitem__(self, pos: Pos) -> int:
        return self.heights[pos]

    def items(self) -> Iterable[tuple[Pos, int]]:
        return self.heights.items()

    def trailheads(self) -> Iterable[Pos]:
        return (pos for pos, height in self.items() if height == 0)

    def trailhead_score(self, trailhead: Pos) -> int:
        return sum(1 for _ in self.reachable_ends(trailhead))

    def reachable_ends(self, start: Pos) -> Iterable[Pos]:
        current_height = self[start]
        if current_height == 9:
            return (start,)

        return set(
            end
            for heading in Heading
            if (pos := heading.move(start)) in self
            if self[pos] == current_height + 1
            for end in self.reachable_ends(pos)
        )

    def trailhead_rating(self, trailhead: Pos) -> int:
        return sum(1 for _ in self.trails(trailhead))

    def trails(self, start: Pos) -> Iterable[Trail]:
        current_height = self[start]
        if current_height == 9:
            return ([start],)

        return (
            [start] + tail
            for heading in Heading
            if (pos := heading.move(start)) in self
            if self[pos] == current_height + 1
            for tail in self.trails(pos)
        )

    def __str__(self) -> str:
        return "\n".join(self.render_lines())

    def render_lines(self, highlight: Iterable[Pos] = ()) -> Iterable[str]:
        highlight_set = set(highlight)

        def char(pos: Pos) -> str:
            if highlight_set and pos not in highlight_set:
                return '·'
            if pos not in self:
                return '·'
            return str(self[pos])

        for y in self.bounds.range_y():
            yield "".join(char((x, y)) for x in self.bounds.range_x())

    def print_trails(self, trails: Iterable[Trail]) -> None:
        for row_lines in zip(*(self.render_lines(trail) for trail in trails)):
            print("   ".join(row_lines))

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        heights: dict[Pos, int] = {}
        map_width, map_height = 0, 0

        for y, line in enumerate(lines):
            for x, char in enumerate(line.strip()):
                if char.isdigit():
                    heights[(x, y)] = int(char)
                if x >= map_width:
                    map_width = x + 1
            map_height = y + 1

        return cls(bounds=Rect.at_origin(map_width, map_height), heights=heights)


def main(input_fn: str = 'data/10-input.txt') -> tuple[int, int]:
    map_ = Map.from_file(input_fn)
    result_1 = part_1(map_)
    result_2 = part_2(map_)
    return result_1, result_2


if __name__ == '__main__':
    main()
