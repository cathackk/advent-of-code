"""
Advent of Code 2018
Day 17: Reservoir Research
https://adventofcode.com/2018/day/17
"""

from itertools import count
from typing import Iterable
from typing import Optional

from common.rect import Rect
from common.text import parse_line


def part_1() -> int:
    """
    You arrive in the year 18. If it weren't for the coat you got in 1018, you would be very cold:
    the North Pole base hasn't even been constructed.

    Rather, it hasn't been constructed **yet**. The Elves are making a little progress, but there's
    not a lot of liquid water in this climate, so they're getting very dehydrated. Maybe there's
    more underground?

    You scan a two-dimensional vertical slice of the ground nearby and discover that it is mostly
    **sand** with veins of **clay**. The scan only provides data with a granularity of **square
    meters**, but it should be good enough to determine how much water is trapped there. In the
    scan, `x` represents the distance to the right, and `y` represents the distance down. There is
    also a **spring of water** near the surface at `x=500, y=0`. The scan identifies **which square
    meters are clay** (your puzzle input).

    For example, suppose your scan shows the following veins of clay:

        >>> example_walls = walls_from_text('''
        ...     x=495, y=2..7
        ...     y=7, x=495..501
        ...     x=501, y=3..7
        ...     x=498, y=2..4
        ...     x=506, y=1..2
        ...     x=498, y=10..13
        ...     x=504, y=10..13
        ...     y=13, x=498..504
        ... ''')
        >>> len(example_walls)
        55
        >>> example_walls[:9]
        [(495, 2), (495, 3), (495, 4), (495, 5), (495, 6), (495, 7), (495, 7), (496, 7), (497, 7)]

    Rendering clay as `#`, sand as `·`, and the water spring as `+`, and with x increasing to the
    right and y increasing downward, this becomes:

        >>> example_state = State.from_walls(example_walls)
        >>> print(format(example_state), 'coors')
           44444455555555
           99999900000000
           45678901234567
         0 ······+·······
         1 ············#·
         2 ·#··#·······#·
         3 ·#··#··#······
         4 ·#··#··#······
         5 ·#·····#······
         6 ·#·····#······
         7 ·#######······
         8 ··············
         9 ··············
        10 ····#·····#···
        11 ····#·····#···
        12 ····#·····#···
        13 ····#######···

    The spring of water will produce water **forever**. Water can move through sand, but is blocked
    by clay. Water **always moves down** when possible, and spreads to the left and right otherwise,
    filling space that has clay on both sides and falling out otherwise.

    For example, if five squares of water are created, they will flow downward until they reach the
    clay and settle there. Water that has come to rest is shown here as `~`, while sand through
    which water has passed (but which is now dry again) is shown as `|`:

        >>> example_state.step()
        >>> print(example_state)
        ······+·······
        ······|·····#·
        ·#··#·|·····#·
        ·#··#·|#······
        ·#··#·|#······
        ·#····|#······
        ·#~~~~~#······
        ·#######······
        ··············
        ··············
        ····#·····#···
        ····#·····#···
        ····#·····#···
        ····#######···

    Two squares of water can't occupy the same location. If another five squares of water are
    created, they will settle on the first five, filling the clay reservoir a little more:

    ......+.......
    ......|.....#.
    .#..#.|.....#.
    .#..#.|#......
    .#..#.|#......
    .#~~~~~#......
    .#~~~~~#......
    .#######......
    ..............
    ..............
    ....#.....#...
    ....#.....#...
    ....#.....#...
    ....#######...
    Water pressure does not apply in this scenario. If another four squares of water are created, they will stay on the right side of the barrier, and no water will reach the left side:

    ......+.......
    ......|.....#.
    .#..#.|.....#.
    .#..#~~#......
    .#..#~~#......
    .#~~~~~#......
    .#~~~~~#......
    .#######......
    ..............
    ..............
    ....#.....#...
    ....#.....#...
    ....#.....#...
    ....#######...
    At this point, the top reservoir overflows. While water can reach the tiles above the surface of the water, it cannot settle there, and so the next five squares of water settle like this:

    ......+.......
    ......|.....#.
    .#..#||||...#.
    .#..#~~#|.....
    .#..#~~#|.....
    .#~~~~~#|.....
    .#~~~~~#|.....
    .#######|.....
    ........|.....
    ........|.....
    ....#...|.#...
    ....#...|.#...
    ....#~~~~~#...
    ....#######...
    Note especially the leftmost |: the new squares of water can reach this tile, but cannot stop there. Instead, eventually, they all fall to the right and settle in the reservoir below.

    After 10 more squares of water, the bottom reservoir is also full:

    ......+.......
    ......|.....#.
    .#..#||||...#.
    .#..#~~#|.....
    .#..#~~#|.....
    .#~~~~~#|.....
    .#~~~~~#|.....
    .#######|.....
    ........|.....
    ........|.....
    ....#~~~~~#...
    ....#~~~~~#...
    ....#~~~~~#...
    ....#######...
    Finally, while there is nowhere left for the water to settle, it can reach a few more tiles before overflowing beyond the bottom of the scanned data:

    ......+.......    (line not counted: above minimum y value)
    ......|.....#.
    .#..#||||...#.
    .#..#~~#|.....
    .#..#~~#|.....
    .#~~~~~#|.....
    .#~~~~~#|.....
    .#######|.....
    ........|.....
    ...|||||||||..
    ...|#~~~~~#|..
    ...|#~~~~~#|..
    ...|#~~~~~#|..
    ...|#######|..
    ...|.......|..    (line not counted: below maximum y value)
    ...|.......|..    (line not counted: below maximum y value)
    ...|.......|..    (line not counted: below maximum y value)
    How many tiles can be reached by the water? To prevent counting forever, ignore tiles with a y coordinate smaller than the smallest y coordinate in your scan data or larger than the largest one. Any x coordinate is valid. In this example, the lowest y coordinate given is 1, and the highest is 13, causing the water spring (in row 0) and the water falling off the bottom of the render (in rows 14 through infinity) to be ignored.

    So, in the example above, counting both water at rest (~) and other sand tiles the water can hypothetically reach (|), the total number of tiles the water can reach is 57.

    How many tiles can the water reach within the range of y values in your scan?


    """

    return 1

Pos = tuple[int, int]
Tiles = dict[Pos, str]

WALL = '#'
STILL = '='
FALLING = '|'
RUNNING = '~'
SOURCE = '+'
SPACE = ' '


def load_walls(fn: str) -> Iterable[Pos]:
    with open(fn) as file:
        for line in file:
            if line.startswith('x='):
                # x=651, y=334..355
                x, y1, y2 = (int(v) for v in parse_line(line, 'x=$, y=$..$\n'))
                assert y1 <= y2
                yield from ((x, y) for y in range(y1, y2 + 1))
            elif line.startswith('y='):
                # y=1708, x=505..523
                y, x1, x2 = (int(v) for v in parse_line(line, 'y=$, x=$..$\n'))
                assert x1 <= x2
                yield from ((x, y) for x in range(x1, x2 + 1))
            else:
                raise ValueError(line)


class State:
    # @classmethod
    # def load(cls, fn: str, sources=((500, 0),)):
    #     return cls(
    #         board={pos: WALL for pos in load_walls(fn)},
    #         sources=sources
    #     )

    def __init__(self, tiles: Tiles, sources: Iterable[Pos]):
        self.tiles = tiles
        self.sources = list(sources)
        self.scoring_bounds = Rect.with_all(self.board.keys())
        self.drawing_bounds = self.scoring_bounds.grow_to_fit(self.sources).grow_by(dx=2)
        self.ticks = 0

    def run(self):
        while self.sources:
            self.step()
        return self

    def step(self):
        assert bool(self.sources), "no more sources to flow!"
        self.ticks += 1

        current_source = self.sources.pop()
        # pour water (down or left/right)
        poured, new_sources = self._pour(current_source)
        # draw poured
        self.tiles.update(poured)
        # push new overflows
        self.sources.extend(new_sources)

        return self

    def _pour(self, pos: Pos) -> tuple[Tiles, Iterable[Pos]]:
        floor = self._scan_floor(pos)

        #   ...+...   ->   ...|...
        if floor is None:
            return {pos: FALLING}, []

        (tile_left, x_left), (tile_right, x_right) = floor
        p_x, p_y = pos

        #   ...+...        ...+...
        #   .......   ->   ...+...
        if x_left == x_right and tile_left == tile_right == '.':
            return {}, [(p_x, p_y), (p_x, p_y + 1)]

        #   ...+...        ...|...
        #   ...|...   ->   ...|...

        #   #  +           #  |
        #   #-----|   ->   #-----|
        if FALLING in (tile_left, tile_right):
            return {pos: FALLING}, []

        #   #  +  #        #~~~~~#
        #   #######   ->   #######

        #      +  #        +-----#
        #   .#~~~~#   ->   .#~~~~#

        #   #  +           #-----+
        #   ######.   ->   ######.

        #      +           +-----+
        #   .#~~~#.   ->   .#~~~#.

        overflows = []
        if tile_left == '.':
            overflows.append((x_left, p_y))
        if tile_right == '.':
            overflows.append((x_right, p_y))

        water_tile = RUNNING if overflows else STILL
        return {(x, p_y): water_tile for x in range(x_left + 1, x_right)}, overflows

    def _scan_floor(self, pos: Pos) -> Optional[tuple[tuple[str, int], tuple[str, int]]]:
        p_x, p_y = pos
        if p_y >= self.drawing_bounds.bottom_y:
            return None

        def walk(dx) -> tuple[str, int]:
            for x in count(p_x, dx):
                tile_current = self.tiles.get((x, p_y))
                if tile_current == WALL:
                    # wall on current level
                    return WALL, x
                tile_below = self.tiles.get((x, p_y + 1))
                if tile_below is None:
                    # empty space below
                    return '.', x
                elif tile_below in (FALLING, RUNNING):
                    # falling or running water below
                    return FALLING, x
                # otherwise continue ...

            # unreachable
            assert False

        return walk(-1), walk(+1)

    def water_score(self, include_running=True):
        scored_tiles = (STILL, FALLING, RUNNING) if include_running else (STILL,)
        return sum(
            1
            for (x, y), tile in self.board.items()
            if y in self.scoring_bounds.range_y() and tile in scored_tiles
        )

    def draw(self):
        print(f"======[{self.ticks}]======")

        def c(pos):
            if pos in self.sources:
                return SOURCE
            elif pos in self.tiles:
                return self.tiles[pos]
            else:
                return SPACE

        for y in self.drawing_bounds.range_y():
            print(''.join(c((x, y)) for x in self.drawing_bounds.range_x()))

        print()


def both_parts(fn: str) -> tuple[int, int]:
    state = State.load(fn).run()
    state.draw()

    score_1 = state.water_score(include_running=True)
    print(f"part 1: water reaches {score_1} tiles")

    score_2 = state.water_score(include_running=False)
    print(f"part 2: water remains at {score_2} tiles")

    return score_1, score_2


if __name__ == '__main__':
    both_parts("data/17-input.txt")
