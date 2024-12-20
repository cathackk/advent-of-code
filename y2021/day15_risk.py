"""
Advent of Code 2021
Day 15: Chiton
https://adventofcode.com/2021/day/15
"""

from typing import Iterable, Self

from common.graph import shortest_path
from common.rect import Rect
from meta.aoc_tools import data_path


def part_1(risk_map: 'RiskMap') -> int:
    """
    The cavern is large, but has a very low ceiling, restricting your motion to two dimensions.
    The shape of the cavern resembles a square; a quick scan of chiton density produces a map of
    **risk level** throughout the cave (your puzzle input). For example:

        >>> cave_map = RiskMap.from_text('''
        ...
        ...     1163751742
        ...     1381373672
        ...     2136511328
        ...     3694931569
        ...     7463417111
        ...     1319128137
        ...     1359912421
        ...     3125421639
        ...     1293138521
        ...     2311944581
        ...
        ... ''')

    You start in the top left position, your destination is the bottom right position, and you
    cannot move diagonally. The number at each position is its **risk level**; to determine the
    total risk of an entire path, add up the risk levels of each position you **enter** (that is,
    don't count the risk level of your starting position unless you enter it; leaving it adds no
    risk to your total).

    Your goal is to find a path with the **lowest total risk**. In this example, a path with
    the lowest total risk is highlighted here:

        >>> path_risk, path = cave_map.safest_path()
        >>> print(cave_map.draw_path(path))
        1·········
        1·········
        2136511···
        ······15··
        ·······1··
        ·······13·
        ········2·
        ········3·
        ········21
        ·········1
        >>> path_risk
        40
        >>> len(path)
        18
        >>> path[:9]
        [(0, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (6, 3)]
        >>> path[9:]
        [(7, 3), (7, 4), (7, 5), (8, 5), (8, 6), (8, 7), (8, 8), (9, 8), (9, 9)]

    The total risk of this path is **`40`** (the starting position is never entered, so its risk is
    not counted).

        >>> cave_map.risk_values(path)
        [1, 2, 1, 3, 6, 5, 1, 1, 1, 5, 1, 1, 3, 2, 3, 2, 1, 1]

    A simple counter-example to solutions consisting only of down and right steps:

        >>> cave_map_2 = RiskMap.from_text('''
        ...
        ...     191919
        ...     181111
        ...     161953
        ...     121191
        ...
        ... ''')
        >>> path_2_risk, path_2 = cave_map_2.safest_path()
        >>> path_2_risk
        15
        >>> print(cave_map_2.draw_path(path_2))
        1·····
        1·1111
        1·1··3
        121··1

    **What is the lowest total risk of any path from the top left to the bottom right?**

        >>> part_1(cave_map)
        part 1: safest path has risk 40
        40
    """

    risk, _ = risk_map.safest_path()
    print(f"part 1: safest path has risk {risk}")
    return risk


def part_2(risk_map: 'RiskMap') -> int:
    """
    Now that you know how to find low-risk paths in the cave, you can try to find your way out.

    The entire cave is actually **five times larger in both dimensions** than you thought; the area
    you originally scanned is just one tile in a 5x5 tile area that forms the full map. Your origi-
    nal map tile repeats to the right and downward; each time the tile repeats to the right or down-
    ward, all of its risk levels **are 1 higher** than the tile immediately up or left of it.
    However, risk levels above `9` wrap back around to `1`. So, if your original map had some
    position with a risk level of `8`, then that same position on each of the 25 total tiles would
    be as follows:

        >>> mini_cave = RiskMap([((0, 0), 8)])
        >>> print(mini_cave)
        8
        >>> print(mini_cave.extended(times=5))
        89123
        91234
        12345
        23456
        34567

    Each single digit above corresponds to the example position with a value of `8` on the top-left
    tile. Because the full map is actually five times larger in both dimensions, that position
    appears a total of 25 times, once in each duplicated tile, with the values shown above.

    Here is the full five-times-as-large version of the first example above:

        >>> original_cave_map = RiskMap.from_file(data_path(__file__, 'example.txt'))
        >>> original_cave_map.bounds.shape
        (10, 10)
        >>> larger_cave_map = original_cave_map.extended(times=5)
        >>> larger_cave_map.bounds.shape
        (50, 50)
        >>> print(larger_cave_map)  # doctest: +ELLIPSIS
        11637517422274862853338597396444961841755517295286
        13813736722492484783351359589446246169155735727126
        21365113283247622439435873354154698446526571955763
        ...
        75698651748671976285978218739618932984172914319528
        56475739656758684176786979528789718163989182927419
        67554889357866599146897761125791887223681299833479

    Equipped with the full map, you can now find a path from the top left corner to the bottom right
    corner with the lowest total risk:

        >>> path_risk, path = larger_cave_map.safest_path()
        >>> print(larger_cave_map.draw_path(path))
        1·················································
        1·················································
        2·················································
        3·················································
        7·················································
        1·················································
        1·················································
        3·················································
        1·················································
        2·················································
        2·················································
        2·················································
        324···············································
        ··1···············································
        ··7···············································
        ··21··············································
        ···1123532········································
        ·········1········································
        ·········2342·····································
        ············332···································
        ··············1···································
        ··············61··································
        ···············44·································
        ················4·································
        ················1·································
        ················2461······························
        ···················4······························
        ···················3······························
        ···················4564···························
        ······················554·························
        ························3163······················
        ···························2······················
        ···························8······················
        ···························125····················
        ·····························6413·················
        ································7·················
        ································26················
        ·································21···············
        ··································7···············
        ··································6112············
        ·····································5············
        ·····································4············
        ·····································1············
        ·····································34725········
        ·········································3········
        ·········································2········
        ·········································24·······
        ··········································1431····
        ·············································2····
        ·············································33479

    The total risk of this path is **`315`** (the starting position is still never entered, so its
    risk is not counted).

        >>> path_risk
        315

    Using the full map, **what is the lowest total risk of any path from the top left to the bottom
    right?**

        >>> part_2(original_cave_map)
        part 2: safest path in the extended map has risk 315
        315
    """

    extended_map = risk_map.extended(times=5)
    risk, _ = extended_map.safest_path()

    print(f"part 2: safest path in the extended map has risk {risk}")
    return risk


Pos = tuple[int, int]
Path = list[Pos]


def adjacent(pos: Pos) -> Iterable[Pos]:
    x, y = pos
    yield x, y - 1
    yield x, y + 1
    yield x - 1, y
    yield x + 1, y


class RiskMap:

    def __init__(self, values: Iterable[tuple[Pos, int]]):
        self.values = dict(values)
        self.bounds = Rect.with_all(self.values.keys())
        assert len(self.values) == self.bounds.area

    def __str__(self) -> str:
        return '\n'.join(
            ''.join(str(self[(x, y)]) for x in self.bounds.range_x())
            for y in self.bounds.range_y()
        )

    def __getitem__(self, pos: Pos) -> int:
        return self.values[pos]

    def __contains__(self, pos: Pos) -> bool:
        return pos in self.values

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(fn))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        return cls(
            ((x, y), int(ch))
            for y, line in enumerate(lines)
            for x, ch in enumerate(line.strip())
        )

    def safest_path(self, origin: Pos = None, destination: Pos = None) -> tuple[int, Path]:
        return shortest_path(
            start=origin or self.bounds.top_left,
            target=destination or self.bounds.bottom_right,
            edges=lambda pos: (
                (npos, npos, self[npos])
                for npos in adjacent(pos)
                if npos in self
            ),
            nodes_count=self.bounds.area
        )

    def draw_path(self, path: Path, origin: Pos = None) -> str:
        path_set = set(path) | {origin or self.bounds.top_left}

        def char(pos: Pos) -> str:
            return str(self[pos]) if pos in path_set else '·'

        return '\n'.join(
            ''.join(char((x, y)) for x in self.bounds.range_x())
            for y in self.bounds.range_y()
        )

    def risk_values(self, path: Path) -> list[int]:
        return [self[pos] for pos in path]

    def extended(self, times: int) -> Self:
        width, height = self.bounds.shape

        def new_risk(original_risk: int, offset: int) -> int:
            # 1 -> 2, ..., 8 -> 9, 9 -> 1
            return 1 + (original_risk + offset - 1) % 9

        return type(self)(
            ((x + ex * width, y + ey * height), new_risk(risk, ex + ey))
            for (x, y), risk in self.values.items()
            for ex in range(times)
            for ey in range(times)
        )


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    risk_map = RiskMap.from_file(input_path)
    result_1 = part_1(risk_map)
    result_2 = part_2(risk_map)
    return result_1, result_2


if __name__ == '__main__':
    main()
