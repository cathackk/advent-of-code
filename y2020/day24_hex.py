"""
Advent of Code 2020
Day 24: Lobby Layout
https://adventofcode.com/2020/day/24
"""

from collections import Counter
from enum import Enum
from functools import cached_property
from typing import Iterable

from common.rect import Rect
from meta.aoc_tools import data_path


def part_1(walks: Iterable['Walk']) -> tuple[int, 'HexGrid']:
    r"""
    Your raft makes it to the tropical island; it turns out that the small crab was an excellent
    navigator. You make your way to the resort. As you enter the lobby, you discover a small
    problem: the floor is being renovated. You can't even reach the check-in desk until they've
    finished installing the *new tile floor*.

    The tiles are all *hexagonal*; they need to be arranged in a hex grid with a very specific
    color pattern. Not in the mood to wait, you offer to help figure out the pattern.

    The tiles are all *white* on one side and *black* on the other. They start with the white side
    facing up. The lobby is large enough to fit whatever pattern might need to appear there.

    A member of the renovation crew gives you a *list of the tiles that need to be flipped over*
    (your puzzle input). Each line in the list identifies a single tile that needs to be flipped by
    giving a series of steps starting from a *reference tile* in the very center of the room.
    (Every line starts from the same reference tile.)

    Because the tiles are hexagonal, every tile has *six neighbors*: east, southeast, southwest,
    west, northwest, and northeast. These directions are given in your list, respectively, as
    `e`, `se`, `sw`, `w`, `nw`, and `ne`.

       / \ / \
      | n | n |
      | w | e |
     / \ / \ / \
    | w |   | e |
    |   |   |   |
     \ / \ / \ /
      | s | s |
      | w | e |
       \ / \ /

    A tile is identified by a series of these directions with *no delimiters*; for example,
    `esenee` identifies the tile you land on if you start at the reference tile and then move one
    tile east, one tile southeast, one tile northeast, and one tile east.


     / \ / \ / \ / \
    | 0 | 1 | 3 | 4 |
    |   |   |   |   |
     \ / \ / \ / \ /
          | 2 |
          |   |
           \ /

    Each time a tile is identified, it flips from white to black or from black to white. Tiles
    might be flipped more than once. For example, a line like `esew` flips a tile immediately
    adjacent to the reference tile, and a line like `nwwswee` flips the reference tile itself.

    Here is a larger example:

        >>> ws = Walk.parse_text('''
        ...     sesenwnenenewseeswwswswwnenewsewsw
        ...     neeenesenwnwwswnenewnwwsewnenwseswesw
        ...     seswneswswsenwwnwse
        ...     nwnwneseeswswnenewneswwnewseswneseene
        ...     swweswneswnenwsewnwneneseenw
        ...     eesenwseswswnenwswnwnwsewwnwsene
        ...     sewnenenenesenwsewnenwwwse
        ...     wenwwweseeeweswwwnwwe
        ...     wsweesenenewnwwnwsenewsenwwsesesenwne
        ...     neeswseenwwswnwswswnw
        ...     nenwswwsewswnenenewsenwsenwnesesenew
        ...     enewnwewneswsewnwswenweswnenwsenwsw
        ...     sweneswneswneneenwnewenewwneswswnese
        ...     swwesenesewenwneswnwwneseswwne
        ...     enesenwswwswneneswsenwnewswseenwsese
        ...     wnwnesenesenenwwnenwsewesewsesesew
        ...     nenewswnwewswnenesenwnesewesw
        ...     eneswnwswnwsenenwnwnwwseeswneewsenese
        ...     neswnwewnwnwseenwseesewsenwsweewe
        ...     wseweeenwnesenwwwswnew
        ... ''')
        >>> len(ws)
        20

    In the above example, 10 tiles are flipped once (to black), and 5 more are flipped twice
    (to black, then back to white).

        >>> tiles = [w.final_pos for w in ws]
        >>> len(tiles)
        20
        >>> len(set(tiles))
        15

    After all of these instructions have been followed, a total of *10 tiles are black*.

        >>> hg = HexGrid()
        >>> len(hg)
        0
        >>> hg.flip_walks(ws)
        >>> len(hg)
        10
        >>> hg
        HexGrid({(-4,0), (-4,2), (-3,-1), (-3,1), (-3,3), (-1,-1), (0,0), (2,2), (3,-3), (4,0)})

    Go through the renovation crew's list and determine which tiles they need to flip. After all
    of the instructions have been followed, *how many tiles are left with the black side up?*

        >>> res, _ = part_1(ws)
        part 1: there are 10 black tiles
        >>> res
        10
    """

    hex_grid = HexGrid()
    hex_grid.flip_walks(walks)
    result = len(hex_grid)

    print(f"part 1: there are {result} black tiles")
    return result, hex_grid


def part_2(hex_grid: 'HexGrid', days: int = 100) -> tuple[int, 'HexGrid']:
    r"""
    The tile floor in the lobby is meant to be a living art exhibit. Every day, the tiles are all
    flipped according to the following rules:

    - Any *black* tile with *zero* or *more than 2* black tiles immediately adjacent to it is
      flipped to *white*.
    - Any *white* tile with *exactly 2* black tiles immediately adjacent to it is
      flipped to *black*.

    Here, *tiles immediately adjacent* means the six tiles directly touching the tile in question.

    The rules are applied *simultaneously* to every tile; put another way, it is first determined
    which tiles need to be flipped, then they are all flipped at the same time.

    In the above example, the number of black tiles that are facing up after the given number of
    days has passed is as follows:

        >>> hg = HexGrid({(-4,0),(-4,2),(-3,-1),(-3,1),(-3,3),(-1,-1),(0,0),(2,2),(3,-3),(4,0)})
        >>> len(hg)
        10
        >>> history = HexGrid(hg).simulate(days=100)
        >>> len(history)
        100
        >>> print("\n".join(f"Day {day+1}: {ac}" for day, ac in enumerate(history[:9])))
        Day 1: 15
        Day 2: 12
        Day 3: 25
        Day 4: 14
        Day 5: 23
        Day 6: 28
        Day 7: 41
        Day 8: 37
        Day 9: 49
        >>> print("\n".join(f"Day {(day+1)*10}: {ac}" for day, ac in enumerate(history[9::10])))
        Day 10: 37
        Day 20: 132
        Day 30: 259
        Day 40: 406
        Day 50: 566
        Day 60: 788
        Day 70: 1106
        Day 80: 1373
        Day 90: 1844
        Day 100: 2208

    After executing this process a total of 100 times, there would be *2208* black tiles facing up.

    *How many tiles will be black after 100 days?*

        >>> res, _ = part_2(hg)
        part 2: after 100 days, there will be 2208 black tiles
        >>> res
        2208
    """

    hex_grid = HexGrid(hex_grid)
    hex_grid.simulate(days)
    result = len(hex_grid)

    print(f"part 2: after {days} days, there will be {result} black tiles")
    return result, hex_grid


class Step(Enum):
    r"""```
     / \
    | x |
    | y |
     \ /

     / \ / \ / \ / \ / \
    |-4 |-2 | 0 | 2 | 4 |
    |-2 |-2 |-2 |-2 |-2 |
     \ / \ / \ / \ / \ /
      |-3 |-1 | 1 | 3 |
      |-1 |-1 |-1 |-1 |
     / \ / \ / \ / \ / \
    |-4 |-2 | 0 | 2 | 4 |
    | 0 | 0 | 0 | 0 | 0 |
     \ / \ / \ / \ / \ /
      |-3 |-1 | 1 | 3 |
      | 1 | 1 | 1 | 1 |
     / \ / \ / \ / \ / \
    |-4 |-2 | 0 | 2 | 4 |
    | 2 | 2 | 2 | 2 | 2 |
     \ / \ / \ / \ / \ /
    ```"""

    E  = (+2,  0)
    SE = (+1, +1)
    SW = (-1, +1)
    W  = (-2,  0)
    NW = (-1, -1)
    NE = (+1, -1)

    def __repr__(self):
        return f'{type(self).__name__}.{self.name}'

    @property
    def dx(self) -> int:
        return self.value[0]

    @property
    def dy(self) -> int:
        return self.value[1]

    def __iter__(self):
        return iter(self.value)

    @classmethod
    def parse_line(cls, line: str) -> Iterable['Step']:
        """
            >>> list(Step.parse_line("eseswwnenw"))
            [Step.E, Step.SE, Step.SW, Step.W, Step.NE, Step.NW]
        """
        line_upper = line.upper()
        head = 0

        try:
            while head < len(line_upper):
                step = next(s for s in cls if line_upper[head:].startswith(s.name))
                yield step
                head += len(step.name)

        except StopIteration as stop:
            raise ValueError(line) from stop


Pos = tuple[int, int]


class Walk:
    def __init__(self, steps: Iterable[Step]):
        self.steps = list(steps)

    @classmethod
    def parse_file(cls, fn: str) -> list['Walk']:
        return list(cls.parse_lines(open(fn)))

    @classmethod
    def parse_text(cls, text: str) -> list['Walk']:
        return list(cls.parse_lines(text.strip().splitlines()))

    @classmethod
    def parse_lines(cls, lines: Iterable[str]) -> Iterable['Walk']:
        return (
            cls(Step.parse_line(line.strip()))
            for line in lines
        )

    @cached_property
    def final_pos(self) -> Pos:
        x, y = 0, 0
        for dx, dy in self.steps:
            x, y = x + dx, y + dy
        return x, y


class HexGrid:
    def __init__(self, active_tiles: Iterable[Pos] = ()):
        self.active_tiles = set(active_tiles)

    def flip_walks(self, walks: Iterable[Walk]):
        for walk in walks:
            if walk.final_pos not in self.active_tiles:
                self.active_tiles.add(walk.final_pos)
            else:
                self.active_tiles.remove(walk.final_pos)

    @staticmethod
    def should_become_active(is_currently_active: bool, active_neighbors_count: int) -> bool:
        if is_currently_active:
            return active_neighbors_count in (1, 2)
        else:
            return active_neighbors_count == 2

    def simulate_single_day(self) -> int:
        def neighbors(pos: Pos) -> Iterable[Pos]:
            x, y = pos
            return (
                (x + dx, y + dy)
                for dx, dy in Step
            )
        active_neighbors = Counter(
            npos
            for pos in self.active_tiles
            for npos in neighbors(pos)
        )
        self.active_tiles = {
            pos
            for pos, ncount in active_neighbors.items()
            if self.should_become_active(
                is_currently_active=pos in self.active_tiles,
                active_neighbors_count=ncount
            )
        }
        return len(self.active_tiles)

    def simulate(self, days: int) -> list[int]:
        return [
            self.simulate_single_day()
            for _ in range(days)
        ]

    def __len__(self):
        return len(self.active_tiles)

    def __iter__(self):
        return iter(self.active_tiles)

    def __repr__(self):
        active_repr = ', '.join(f'({x},{y})' for x, y in sorted(self.active_tiles))
        return f'{type(self).__name__}({{{active_repr}}})'

    def __str__(self):
        def char(pos: Pos) -> str:
            x, y = pos
            if (x + y) % 2 == 1:
                return ' '
            elif pos in self.active_tiles:
                return '#'
            else:
                return '.'

        bounds = Rect.with_all(self.active_tiles)
        return "\n".join(
            "".join(char((x, y)) for x in bounds.range_x())
            for y in bounds.range_y()
        )


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    walks = Walk.parse_file(input_path)
    result_1, hex_grid_1 = part_1(walks)
    result_2, _ = part_2(hex_grid_1)
    return result_1, result_2


if __name__ == '__main__':
    main()
