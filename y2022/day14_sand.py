"""
Advent of Code 2022
Day 14: Regolith Reservoir
https://adventofcode.com/2022/day/14
"""

from itertools import chain
from typing import Iterable

from common.file import relative_path
from common.iteration import zip1
from common.math import sgn
from common.rect import Rect
from common.utils import some


def part_1(walls: Iterable['Pos']) -> int:
    """
    The distress signal leads you to a giant waterfall! Actually, hang on - the signal seems like
    it's coming from the waterfall itself, and that doesn't make any sense. However, you do notice
    a little path that leads **behind** the waterfall.

    Correction: the distress signal leads you behind a giant waterfall! There seems to be a large
    cave system here, and the signal definitely leads further inside.

    As you begin to make your way deeper underground, you feel the ground rumble for a moment. Sand
    begins pouring into the cave! If you don't quickly figure out where the sand is going, you could
    quickly become trapped!

    Fortunately, your familiarity with analyzing the path of falling material will come in handy
    here. You scan a two-dimensional vertical slice of the cave above you (your puzzle input) and
    discover that it is mostly air with structures made of **rock**.

    Your scan traces the path of each solid rock structure and reports the `x,y` coordinates that
    form the shape of the path, where `x` represents distance to the right and `y` represents
    distance down. Each path appears as a single line of text in your scan. After the first point of
    each path, each point indicates the end of a straight horizontal or vertical line to be drawn
    from the previous point. For example:

        >>> rock = walls_from_text('''
        ...     498,4 -> 498,6 -> 496,6
        ...     503,4 -> 502,4 -> 502,9 -> 494,9
        ... ''')
        >>> len(rock)
        20

    This scan means that there are two paths of rock; the first path consists of two straight lines,
    and the second path consists of three straight lines. (Specifically, the first path consists of
    a line of rock from `498,4` through `498,6` and another line of rock from `498,6` through
    `496,6`.)

        >>> rock  # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
        [(498, 4), (498, 5), (498, 6), (497, 6), (496, 6),
         (503, 4), (502, 4), (502, 5), (502, 6), ..., (495, 9), (494, 9)]

    The sand is pouring into the cave from point `500,0`.

        >>> sand_source = (500, 0)

    Drawing rock as `#`, air as `·`, and the source of the sand as `+`, this becomes:

        >>> print(state_0 := State(set(rock), sand_source))
        ······+···
        ··········
        ··········
        ··········
        ····#···##
        ····#···#·
        ··###···#·
        ········#·
        ········#·
        #########·

    Sand is produced **one unit at a time**, and the next unit of sand is not produced until the
    previous unit of sand **comes to rest**. A unit of sand is large enough to fill one tile of air
    in your scan.

    A unit of sand always falls **down one step** if possible. If the tile immediately below is
    blocked (by rock or sand), the unit of sand attempts to instead move diagonally **one step down
    and to the left**. If that tile is blocked, the unit of sand attempts to instead move diagonally
    **one step down and to the right**. Sand keeps moving as long as it is able to do so, at each
    step trying to move down, then down-left, then down-right. If all three possible destinations
    are blocked, the unit of sand **comes to rest** and no longer moves, at which point the next
    unit of sand is created back at the source.

    So, drawing sand that has come to rest as `o`, the first unit of sand simply falls straight down
    and then stops:

        >>> print(state_1 := state_0.next_state())
        ······+···
        ··········
        ··········
        ··········
        ····#···##
        ····#···#·
        ··###···#·
        ········#·
        ······o·#·
        #########·

    The second unit of sand then falls straight down, lands on the first one, and then comes to rest
    to its left:

        >>> print(state_2 := state_1.next_state())
        ······+···
        ··········
        ··········
        ··········
        ····#···##
        ····#···#·
        ··###···#·
        ········#·
        ·····oo·#·
        #########·

    After a total of five units of sand have come to rest, they form this pattern:

        >>> print(state_5 := state_2.run(until_sand_amount=5))
        ······+···
        ··········
        ··········
        ··········
        ····#···##
        ····#···#·
        ··###···#·
        ······o·#·
        ····oooo#·
        #########·

    After a total of 22 units of sand:

        >>> print(state_22 := state_5.run(until_sand_amount=22))
        ······+···
        ··········
        ······o···
        ·····ooo··
        ····#ooo##
        ····#ooo#·
        ··###ooo#·
        ····oooo#·
        ···ooooo#·
        #########·

    Finally, only two more units of sand can possibly come to rest:

        >>> print(state_final := state_22.run())
        ······+···
        ··········
        ······o···
        ·····ooo··
        ····#ooo##
        ···o#ooo#·
        ··###ooo#·
        ····oooo#·
        ·o·ooooo#·
        #########·
        >>> len(state_final.sand)
        24

    Once all **24** units of sand shown above have come to rest, all further sand flows out the
    bottom, falling into the endless void.

    Using your scan, simulate the falling sand. **How many units of sand come to rest before sand
    starts flowing into the abyss below?**

        >>> part_1(rock)
        part 1: the cave contains 24 units of sand
        24
    """

    final_state = State(set(walls)).run()
    result = len(final_state.sand)

    print(f"part 1: the cave contains {result} units of sand")
    return result


def part_2(walls: Iterable['Pos']) -> int:
    """
    You realize you misread the scan. There isn't an endless void at the bottom of the scan -
    there's floor, and you're standing on it!

    You don't have time to scan the floor, so assume the floor is an infinite horizontal line with
    a `y` coordinate equal to **two plus the highest `y` coordinate** of any point in your scan.

    In the example above, the highest `y` coordinate of any point is `9`, and so the floor is at
    `y=11`. (This is as if your scan contained one extra rock path like `-inf,11 -> +inf,11`.)
    With the added floor, the example above now looks like this:

        >>> rock = walls_from_file('data/14-example.txt')
        >>> print(state_0 := State(set(rock), bottom_floor=True))
        ········+·····
        ··············
        ··············
        ··············
        ······#···##··
        ······#···#···
        ····###···#···
        ··········#···
        ··········#···
        ··#########···
        ··············
        ##############

    To find somewhere safe to stand, you'll need to simulate falling sand until a unit of sand comes
    to rest at 500,0, blocking the source entirely and stopping the flow of sand into the cave. In
    the example above, the situation finally looks like this after **93** units of sand come to
    rest:

        >>> state_final = state_0.run()
        >>> len(state_final.sand)
        93
        >>> print(state_final)
        ············o············
        ···········ooo···········
        ··········ooooo··········
        ·········ooooooo·········
        ········oo#ooo##o········
        ·······ooo#ooo#ooo·······
        ······oo###ooo#oooo······
        ·····oooo·oooo#ooooo·····
        ····oooooooooo#oooooo····
        ···ooo#########ooooooo···
        ··ooooo·······ooooooooo··
        #########################

    Using your scan, simulate the falling sand until the source of the sand becomes blocked.
    **How many units of sand come to rest?**

        >>> part_2(rock)
        part 2: cave contains 93 units of sand
        93
    """

    final_state = State(set(walls), bottom_floor=True).run()
    result = len(final_state.sand)

    print(f"part 2: cave contains {result} units of sand")
    return result


Pos = tuple[int, int]


class NoMoreSandException(Exception):
    pass


class State:
    def __init__(
        self,
        walls: set[Pos],
        sand_source: Pos = (500, 0),
        sand: set[Pos] = None,
        bottom_floor: bool = False,
    ):
        self.walls = walls
        self.sand_source = sand_source
        self.sand = sand or set()
        self.bottom_floor_y = (max(y for _, y in self.walls) + 2) if bottom_floor else None

    def __str__(self) -> str:
        bounds = Rect.with_all(chain(self.walls, [self.sand_source], self.sand))

        if self.bottom_floor:
            left_x, right_x = bounds.left_x - 2, bounds.right_x + 2
            floor_y = self.bottom_floor_y
            bounds = bounds.grow_to_fit([(left_x, floor_y), (right_x, floor_y)])

        def char(pos: Pos) -> str:
            if pos in self.walls:
                return '#'
            elif pos[1] == self.bottom_floor_y:
                return '#'
            elif pos in self.sand:
                return 'o'
            elif pos == self.sand_source:
                return '+'
            else:
                return '·'

        return '\n'.join(
            ''.join(char((x, y)) for x in bounds.range_x())
            for y in bounds.range_y()
        )

    @property
    def bottom_floor(self) -> bool:
        return bool(self.bottom_floor_y)

    def is_blocked(self, pos: Pos) -> bool:
        return pos in self.walls or pos in self.sand

    def next_sand_pos(self) -> Pos:
        max_y = max(y for _, y in self.walls) + 2
        x, y = self.sand_source

        if self.is_blocked((x, y)):
            # source is blocked
            raise NoMoreSandException()

        while y < max_y:
            try:
                y1 = y + 1
                x, y = next(
                    (x1, y1)
                    for x1 in [x, x - 1, x + 1]
                    if not self.is_blocked((x1, y1))
                )
            except StopIteration:
                return x, y

        # y >= max_y -> falling out of bounds
        raise NoMoreSandException()

    def next_state(self) -> 'State':
        return State(
            walls=self.walls,
            sand_source=self.sand_source,
            sand=self.sand | {self.next_sand_pos()},
            bottom_floor=self.bottom_floor,
        )

    def run(self, until_sand_amount: int = 0) -> 'State':
        state = self

        if not until_sand_amount and self.bottom_floor:
            # don't run the sim, instead find all sand-reachable positions and fill them at once
            return self.filled()

        while True:
            if until_sand_amount and len(state.sand) >= until_sand_amount:
                return state

            try:
                state = state.next_state()
            except NoMoreSandException:
                return state

    def filled(self) -> 'State':
        _, source_y = self.sand_source
        floor_y = some(self.bottom_floor_y)

        def all_sand_positions() -> Iterable[Pos]:
            yield self.sand_source
            last_line = {self.sand_source}

            for y in range(source_y + 1, floor_y):
                line = {
                    pos
                    for x0, _ in last_line
                    for dx in (-1, 0, +1)
                    if (pos := (x0 + dx, y)) not in self.walls
                }
                yield from line
                last_line = line

        return State(
            walls=self.walls,
            sand_source=self.sand_source,
            sand=set(all_sand_positions()),
            bottom_floor=True,
        )


def walls_from_file(fn: str) -> list[Pos]:
    return list(walls_from_lines(open(relative_path(__file__, fn))))


def walls_from_text(text: str) -> list[Pos]:
    return list(walls_from_lines(text.strip().splitlines()))


def walls_from_lines(lines: Iterable[str]) -> Iterable[Pos]:
    # 498,4 -> 498,6 -> 496,6
    # 503,4 -> 502,4 -> 502,9 -> 494,9

    def to_pos(text: str) -> Pos:
        x, y = text.split(',')
        return int(x), int(y)

    for line in lines:
        points = [to_pos(point) for point in line.strip().split(' -> ')]
        for (x1, y1), (x2, y2) in zip1(points):
            if x1 == x2 and y1 != y2:
                yield from ((x1, y) for y in range(y1, y2, sgn(y2 - y1)))
            elif y1 == y2 and x1 != x2:
                yield from ((x, y1) for x in range(x1, x2, sgn(x2 - x1)))
            else:
                raise ValueError((x1, y1), (x2, y2))

        yield points[-1]


def main(input_fn: str = 'data/14-input.txt') -> tuple[int, int]:
    walls = walls_from_file(input_fn)
    result_1 = part_1(walls)
    result_2 = part_2(walls)
    return result_1, result_2


if __name__ == '__main__':
    main()
