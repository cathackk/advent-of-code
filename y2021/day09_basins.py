"""
Advent of Code 2021
Day 9: Smoke Basin
https://adventofcode.com/2021/day/9
"""

from typing import Iterable

from common.file import relative_path
from common.rect import Rect
from common.utils import ro


def part_1(heights: 'HeightMap') -> int:
    """
    If you can model how the smoke flows through the caves, you might be able to avoid it and be
    that much safer. The submarine generates a heightmap of the floor of the nearby caves for you
    (your puzzle input).

    Smoke flows to the lowest point of the area it's in. For example, consider the following
    heightmap:

        >>> hmap = HeightMap.from_file('data/09-example.txt')
        >>> print(hmap)
        2199943210
        3987894921
        9856789892
        8767896789
        9899965678
        >>> hmap.bounds
        Rect((0, 0), (9, 4))
        >>> hmap[(0, 0)]
        2
        >>> hmap[(2, 1)]
        8

    Each number corresponds to the height of a particular location, where `9` is the highest and `0`
    is the lowest a location can be.

    Your first goal is to find the **low points** - the locations that are lower than any of its
    adjacent locations. Most locations have four adjacent locations (up, down, left, and right);
    locations on the edge or corner of the map have three or two adjacent locations, respectively.
    (Diagonal locations do not count as adjacent.)

        >>> list(adjacent((0, 0)))
        [(1, 0), (0, 1), (-1, 0), (0, -1)]

    In the above example, there are **four** low points: two are in the first row (a `1` and a `0`),
    one is in the third row (a `5`), and one is in the bottom row (also a `5`). All other locations
    on the heightmap have some lower adjacent location, and so are not low points.

        >>> list(hmap.low_point_values())
        [1, 0, 5, 5]

    The **risk level** of a low point is **1 plus its height**. In the above example, the risk
    levels of the low points are `2`, `1`, `6`, and `6`. The sum of the risk levels of all low
    points in the heightmap is therefore **`15`**.

        >>> hmap.total_risk_level()
        15

    Find all of the low points on your heightmap. **What is the sum of the risk levels of all low
    points on your heightmap?**

        >>> part_1(hmap)
        part 1: risk level is 15
        15
    """

    result = heights.total_risk_level()

    print(f"part 1: risk level is {result}")
    return result


def part_2(heights: 'HeightMap') -> int:
    """
    Next, you need to find the largest basins so you know what areas are most important to avoid.

    A **basin** is all locations that eventually flow downward to a single low point. Therefore,
    every low point has a basin, although some basins are very small. Locations of height 9 do not
    count as being in any basin, and all other locations will always be part of exactly one basin.

    The size of a basin is the number of locations within the basin, including the low point.
    The example above has four basins:

        >>> hmap = HeightMap.from_file('data/09-example.txt')
        >>> basins = list(hmap.basins())
        >>> len(basins)
        4

    The top-left basin:

        >>> len(basins[0])
        3
        >>> print(hmap.draw_basins(basins[0]))
        21█·······
        3█········
        █·········
        ··········
        ··········

    The top-right basin:

        >>> len(basins[1])
        9
        >>> print(hmap.draw_basins(basins[1]))
        ····█43210
        ·····█4█21
        ······█·█2
        ·········█
        ··········

    The middle basin:

        >>> len(basins[2])
        14
        >>> print(hmap.draw_basins(basins[2]))
        ··███·····
        ·█878█····
        █85678█···
        87678█····
        █8███·····

    The bottom-right basin:

        >>> len(basins[3])
        9
        >>> print(hmap.draw_basins(basins[3]))
        ··········
        ·······█··
        ······█8█·
        ·····█678█
        ····█65678

    Find the three largest basins and multiply their sizes together.
    In the above example, this is `9 * 14 * 9 = 1134`.

    **What do you get if you multiply together the sizes of the three largest basins?**

        >>> part_2(hmap)
        part 2: three largest basin sizes multiplied = 14 * 9 * 9 = 1134
        1134
    """

    basin_sizes = sorted((len(b) for b in heights.basins()), reverse=True)
    assert len(basin_sizes) >= 3
    size_1, size_2, size_3 = basin_sizes[:3]
    result = size_1 * size_2 * size_3

    print(
        f"part 2: three largest basin sizes multiplied = {size_1} * {size_2} * {size_3} = {result}"
    )
    return result


Pos = tuple[int, int]


class HeightMap:
    def __init__(self, heights: Iterable[tuple[Pos, int]]):
        self.heights = dict(heights)
        self.bounds = Rect.with_all(self.heights.keys())

    @classmethod
    def from_text(cls, text: str) -> 'HeightMap':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_file(cls, fn: str) -> 'HeightMap':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'HeightMap':
        return cls(
            ((x, y), int(h))
            for y, line in enumerate(lines)
            for x, h in enumerate(line.strip())
        )

    def __str__(self) -> str:
        return '\n'.join(
            ''.join(str(self[(x, y)]) for x in self.bounds.range_x())
            for y in self.bounds.range_y()
        )

    def __getitem__(self, pos: Pos) -> int:
        return self.heights[pos]

    def __contains__(self, pos: Pos) -> bool:
        return pos in self.heights

    def low_point_values(self) -> Iterable[int]:
        return (
            h
            for pos, h in self.heights.items()
            if all(
                self[adj] > h
                for adj in adjacent(pos)
                if adj in self
            )
        )

    def total_risk_level(self) -> int:
        return sum(lp + 1 for lp in self.low_point_values())

    def basins(self) -> Iterable[set[Pos]]:
        # unvisited positions
        poss_left = set(pos for pos, h in self.heights.items() if h < 9)
        while poss_left:

            # take one
            pos = min(poss_left, key=ro)
            poss_left.remove(pos)

            # and grow it into basin
            basin = {pos}
            adjs_left = set(adjacent(pos))
            while adjs_left:
                adj = adjs_left.pop()
                if adj in poss_left and self[adj] < 9:
                    poss_left.remove(adj)
                    basin.add(adj)
                    adjs_left.update(adjacent(adj))

            yield basin

    def draw_basins(self, *basins: set[Pos]) -> str:
        all_basins = set.union(*basins)

        def char(pos: Pos) -> str:
            if pos in all_basins:
                return str(self[pos])
            elif self[pos] == 9 and all_basins & set(adjacent(pos)):
                return '█'
            else:
                return '·'

        return '\n'.join(
            ''.join(char((x, y)) for x in self.bounds.range_x())
            for y in self.bounds.range_y()
        )


def adjacent(pos: Pos) -> Iterable[Pos]:
    x, y = pos
    yield x + 1, y
    yield x, y + 1
    yield x - 1, y
    yield x, y - 1


if __name__ == '__main__':
    heights_ = HeightMap.from_file('data/09-input.txt')
    part_1(heights_)
    part_2(heights_)
    # print(heights_.draw_basins(*sorted(heights_.basins(), key=len, reverse=True)[:3]))
