"""
Advent of Code 2016
Day 24: Air Duct Spelunking
https://adventofcode.com/2016/day/24
"""

from itertools import permutations
from typing import Iterable

from common.rect import Rect
from common.iteration import mink
from common.file import relative_path
from common.iteration import slidingw


def part_1(maze: 'Maze') -> int:
    """
    You've finally met your match; the doors that provide access to the roof are locked tight, and
    all of the controls and related electronics are inaccessible. You simply can't reach them.

    The robot that cleans the air ducts, however, **can**.

    It's not a very fast little robot, but you reconfigure it to be able to interface with some of
    the exposed wires that have been routed through the HVAC system. If you can direct it to each of
    those locations, you should be able to bypass the security controls.

    You extract the duct layout for this area from some blueprints you acquired and create a map
    with the relevant locations marked (your puzzle input). `0` is your current location, from which
    the cleaning robot embarks; the other numbers are (in **no particular order**) the locations
    the robot needs to visit at least once each. Walls are marked as `#`, and open passages are
    marked as `.`. Numbers behave like open passages.

    For example, suppose you have a map like the following:

        >>> example_maze = Maze.from_text('''
        ...
        ...     ###########
        ...     #0.1.....2#
        ...     #.#######.#
        ...     #4.......3#
        ...     ###########
        ...
        ... ''')
        >>> len(example_maze.passages)
        20
        >>> example_maze.targets
        {(1, 1): '0', (3, 1): '1', (9, 1): '2', (1, 3): '4', (9, 3): '3'}

    To reach all of the points of interest as quickly as possible, you would have the robot take
    the following path:

      - `0` to `4` (`2` steps)
      - `4` to `1` (`4` steps; it can't move diagonally)
      - `1` to `2` (`6` steps)
      - `2` to `3` (`2` steps)

        >>> example_maze.shortest_path(start_at='0')
        (14, ('0', '4', '1', '2', '3'))

    Since the robot isn't very fast, you need to find it the **shortest route**. This path is the
    fewest steps (in the above example, a total of `14`) required to start at `0` and then visit
    every other location at least once.

    Given your actual map, and starting from location `0`, what is the **fewest number of steps**
    required to visit every non-`0` number marked on the map at least once?

        >>> part_1(example_maze)
        part 1: shortest path is 14 steps long (0-4-1-2-3)
        14
    """

    dist, path = maze.shortest_path(start_at='0')
    print(f"part 1: shortest path is {dist} steps long ({'-'.join(path)})")
    return dist


def part_2(maze: 'Maze') -> int:
    """
    Of course, if you leave the cleaning robot somewhere weird, someone is bound to notice.

    What is the fewest number of steps required to start at `0`, visit every non-`0` number marked
    on the map at least once, and then **return to `0`**?

        >>> example_maze = Maze.from_file('data/24-example.txt')
        >>> part_2(example_maze)
        part 2: shortest closed path is 20 steps long (0-1-2-3-4-0)
        20
    """

    dist, path = maze.shortest_closed_path(start_at='0')
    print(f"part 2: shortest closed path is {dist} steps long ({'-'.join(path)})")
    return dist


Pos = tuple[int, int]
Target = tuple[Pos, str]
Path = tuple[str, ...]


class Maze:
    def __init__(self, passages: Iterable[Pos], targets: Iterable[Target] | dict[Pos, str]):
        self.passages = set(passages)
        self.targets = dict(targets)

        self.bounds = Rect.with_all(self.passages).grow_by(+1, +1)

        assert self.passages
        assert self.targets
        for target_pos, target_code in self.targets.items():
            assert target_pos in self.passages  # target is not in a wall
            assert len(target_code) == 1

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.passages!r}, targets={self.targets!r})'

    def paths(self, start_code: str = '0') -> Iterable[Path]:
        other_codes = set(self.targets.values()) - {start_code}
        return (
            (start_code,) + path
            for path in permutations(other_codes)
        )

    def closed_paths(self, start_code: str == '0') -> Iterable[Path]:
        other_codes = set(self.targets.values()) - {start_code}
        return (
            (start_code,) + path + (start_code,)
            for path in permutations(other_codes)
        )

    def shortest_path(self, start_at: str = '0') -> tuple[int, Path]:
        distances = self.calculate_distances()
        result_path, distance = mink(
            self.paths(start_at),
            key=lambda path: sum(distances[(a, b)] for a, b in slidingw(path, 2))
        )
        return distance, result_path

    def shortest_closed_path(self, start_at: str = '0') -> tuple[int, Path]:
        distances = self.calculate_distances()
        result_path, (distance, _) = mink(
            self.closed_paths(start_at),
            # path is included in key in order to make the calculation deterministic
            # because closed path can be reversed (0-1-2-0 and 0-2-1-0)
            key=lambda path: (sum(distances[(a, b)] for a, b in slidingw(path, 2)), path)
        )
        return distance, result_path

    def neighbors(self, pos: Pos) -> Iterable[Pos]:
        x, y = pos
        return (
            (x + dx, y + dy)
            for (dx, dy) in [(+1, 0), (-1, 0), (0, +1), (0, -1)]
            if (x + dx, y + dy) in self.passages
        )

    def calculate_distances(self) -> dict[tuple[str, str], int]:
        return dict(
            ccd
            for target in self.targets.items()
            for ccd in self._calculate_distances_from(target)
        )

    def _calculate_distances_from(self, target: Target) -> Iterable[tuple[tuple[str, str], int]]:
        pos1, code1 = target

        visited: set[Pos] = {pos1}
        current_layer: set[Pos] = {pos1}
        current_distance: int = 0
        codes_left: set[str] = set(self.targets.values()) - {code1}

        while current_layer and codes_left:
            next_layer: set[Pos] = set()

            for pos in current_layer:
                for npos in self.neighbors(pos):
                    if npos in visited:
                        continue

                    visited.add(npos)
                    next_layer.add(npos)

                    if npos in self.targets:
                        code2 = self.targets[npos]
                        codes_left.remove(code2)
                        yield (code1, code2), current_distance + 1

            current_layer = next_layer
            current_distance += 1

    def __str__(self) -> str:
        def char(pos: Pos) -> str:
            if pos in self.targets:
                return self.targets[pos]
            elif pos in self.passages:
                return '.'
            else:
                return '#'

        return "\n".join(
            "".join(char((x, y)) for x in self.bounds.range_x())
            for y in self.bounds.range_y()
        )

    @classmethod
    def from_text(cls, text: str) -> 'Maze':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_file(cls, fn: str) -> 'Maze':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Maze':
        passages: list[Pos] = []
        targets: list[Target] = []

        for y, line in enumerate(lines):
            for x, c in enumerate(line.strip()):
                if c != "#":
                    pos = (x, y)
                    passages.append(pos)
                    if c.isdigit():
                        targets.append((pos, c))

        return cls(passages, targets)


if __name__ == '__main__':
    maze_ = Maze.from_file('data/24-input.txt')
    part_1(maze_)
    part_2(maze_)
