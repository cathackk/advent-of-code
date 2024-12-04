"""
Advent of Code 2022
Day 12: Hill Climbing Algorithm
https://adventofcode.com/2022/day/12
"""

import functools
import string
from typing import Callable, Iterable, Self

from common.graph import shortest_path
from common.heading import Heading
from common.rect import Rect
from meta.aoc_tools import data_path


def part_1(heightmap: 'HeightMap') -> int:
    """
    You try contacting the Elves using your handheld device, but the river you're following must be
    too low to get a decent signal.

    You ask the device for a heightmap of the surrounding area (your puzzle input). The heightmap
    shows the local area from above broken into a grid; the elevation of each square of the grid is
    given by a single lowercase letter, where `a` is the lowest elevation, `b` is the next-lowest,
    and so on up to the highest elevation, `z`.

    Also included on the heightmap are marks for your current position (`S`) and the location that
    should get the best signal (`E`). Your current position (`S`) has elevation `a`, and the
    location that should get the best signal (`E`) has elevation `z`.

    You'd like to reach `E`, but to save energy, you should do it in **as few steps as possible**.
    During each step, you can move exactly one square up, down, left, or right. To avoid needing to
    get out your climbing gear, the elevation of the destination square can be **at most one
    higher** than the elevation of your current square; that is, if your current elevation is `m`,
    you could step to elevation `n`, but not to elevation `o`. (This also means that the elevation
    of the destination square can be much lower than the elevation of your current square.)

    For example:

        >>> hm = HeightMap.from_text('''
        ...     Sabqponm
        ...     abcryxxl
        ...     accszExk
        ...     acctuvwj
        ...     abdefghi
        ... ''')
        >>> hm.rect.shape
        (8, 5)
        >>> hm.start
        (0, 0)
        >>> hm.target
        (5, 2)
        >>> [hm.elevations[x, 1] for x in hm.rect.range_x()]  # abcryxxl
        [0, 1, 2, 17, 24, 23, 23, 11]
        >>> [hm.elevations[3, y] for y in hm.rect.range_y()]  # qrste
        [16, 17, 18, 19, 4]
        >>> hm.elevations[hm.start]
        0
        >>> hm.elevations[hm.target]
        25

    Here, you start in the top-left corner; your goal is near the middle. You could start by moving
    down or right, but eventually you'll need to head toward the `e` at the bottom. From there, you
    can spiral around to the goal:

        >>> path = hm.find_shortest_path_to_top()
        >>> path  # doctest: +ELLIPSIS
        [Heading.EAST, Heading.SOUTH, Heading.SOUTH, Heading.EAST, Heading.SOUTH, ...]
        >>> hm.draw_path(path)
        →↓·↓←←←←
        ·↓·↓↓←←↑
        ·→↓↓→E↑↑
        ··↓→→→↑↑
        ··→→→→→↑

    In the above diagram, the symbols indicate whether the path exits each square moving up (`↑`),
    down (`↓`), left (`←`), or right (`→`). The location that should get the best signal is still
    `E`, and `·` marks unvisited squares.

    This path reaches the goal in **31** steps, the fewest possible.

        >>> len(path)
        31

    **What is the fewest steps required to move from your current position to the location that
    should get the best signal?**

        >>> part_1(hm)
        part 1: target can be reached in 31 steps
        31
    """

    result = len(heightmap.find_shortest_path_to_top())

    print(f"part 1: target can be reached in {result} steps")
    return result


def part_2(heightmap: 'HeightMap') -> int:
    """
    As you walk up the hill, you suspect that the Elves will want to turn this into a hiking trail.
    The beginning isn't very scenic, though; perhaps you can find a better starting point.

    To maximize exercise while hiking, the trail should start as low as possible: elevation `a`.
    The goal is still the square marked `E`. However, the trail should still be direct, taking the
    fewest steps to reach its goal. So, you'll need to find the shortest path from **any square at
    elevation `a`** to the square marked `E`.

    Again consider the example from above:

        >>> hm = HeightMap.from_file(data_path(__file__, 'example.txt'))

    Now, there are six choices for starting position (five marked `a`, plus the square marked `S`
    that counts as being at elevation `a`). If you start at the bottom-left square, you can reach
    the goal most quickly:

        >>> path = hm.find_shortest_path_down()
        >>> path_reversed = [step.opposite() for step in reversed(path)]
        >>> hm.draw_path(path_reversed, start=(0, 4))
        ···↓←←←←
        ···↓↓←←↑
        ···↓→E↑↑
        ·→↓→→→↑↑
        →↑→→→→→↑

    This path reaches the goal in only 29 steps, the fewest possible.

        >>> len(path)
        29

    **What is the fewest steps required to move starting from any square with elevation `a` to the
    location that should get the best signal?**

        >>> part_2(hm)
        part 2: lowest elevation can be reached in 29 steps
        29
    """

    result = len(heightmap.find_shortest_path_down())

    print(f"part 2: lowest elevation can be reached in {result} steps")
    return result


Pos = tuple[int, int]
Path = list[Heading]


class HeightMap:

    def __init__(self, elevations: dict[Pos, int], start: Pos, target: Pos):
        self.elevations = dict(elevations)
        self.start = start
        self.target = target

        self.rect = Rect.with_all(self.elevations)

    def neighbors(
        self,
        pos: Pos,
        can_climb: Callable[[int, int], bool],
    ) -> Iterable[tuple[Pos, Heading, int]]:
        x, y = pos
        elevation = self.elevations[pos]

        for heading in Heading:
            npos = x + heading.dx, y + heading.dy
            if npos not in self.elevations:
                continue
            if can_climb(elevation, self.elevations[npos]):
                yield npos, heading, 1

    def find_shortest_path_to_top(self, start: Pos = None) -> Path:
        _, path = shortest_path(
            start=start or self.start,
            target=self.target,
            edges=functools.partial(self.neighbors, can_climb=lambda old, new: new - old <= 1),
            nodes_count=self.rect.area,
        )
        return path

    def find_shortest_path_down(self, start: Pos = None) -> Path:
        _, path = shortest_path(
            start=start or self.target,
            target=lambda pos: self.elevations[pos] == 0,
            edges=functools.partial(self.neighbors, can_climb=lambda old, new: old - new <= 1),
            nodes_count=self.rect.area,
        )
        return path

    def draw_path(self, path: Path, start: Pos = None) -> None:
        chars: dict[Pos, str] = {self.target: 'E'}
        x, y = start or self.start

        for heading in path:
            chars[x, y] = heading.arrow
            x, y = x + heading.dx, y + heading.dy

        lines = (
            ''.join(chars.get((x, y), '·') for x in self.rect.range_x())
            for y in self.rect.range_y()
        )
        print('\n'.join(lines))

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(fn))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        char_to_elevation = dict(zip(string.ascii_lowercase, range(26))) | {'S': 0, 'E': 25}

        elevations: dict[Pos, int] = {}
        start: Pos | None = None
        target: Pos | None = None

        pos_chars = (
            ((x, y), char)
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
        )

        for pos, char in pos_chars:
            elevations[pos] = char_to_elevation[char]
            if char == 'S':
                start = pos
            elif char == 'E':
                target = pos

        if not start:
            raise ValueError("starting position 'S' not found")
        if not target:
            raise ValueError("target position 'E' not found")

        return cls(elevations, start, target)



def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    heightmap = HeightMap.from_file(input_path)
    result_1 = part_1(heightmap)
    result_2 = part_2(heightmap)
    return result_1, result_2


if __name__ == '__main__':
    main()
