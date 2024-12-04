"""
Advent of Code 2023
Day 14: Parabolic Reflector Dish
https://adventofcode.com/2023/day/14
"""

from typing import Iterable, Self

from common.file import relative_path
from common.heading import Heading
from common.iteration import detect_cycle, dgroupby_pairs_set
from common.rect import Rect


def part_1(map_: 'Map') -> int:
    """
    You reach the place where all of the mirrors were pointing: a massive parabolic reflector dish
    attached to the side of another large mountain.

    The dish is made up of many small mirrors, but while the mirrors themselves are roughly in
    the shape of a parabolic reflector dish, each individual mirror seems to be pointing in slightly
    the wrong direction. If the dish is meant to focus light, all it's doing right now is sending it
    in a vague direction.

    This system must be what provides the energy for the lava! If you focus the reflector dish,
    maybe you can go where it's pointing and use the light to fix the lava production.

    Upon closer inspection, the individual mirrors each appear to be connected via an elaborate
    system of ropes and pulleys to a large metal platform below the dish. The platform is covered in
    large rocks of various shapes. Depending on their position, the weight of the rocks deforms
    the platform, and the shape of the platform controls which ropes move and ultimately the focus
    of the dish.

    In short: if you move the rocks, you can focus the dish. The platform even has a control panel
    on the side that lets you **tilt** it in one of four directions! The rounded rocks (`O`) will
    roll when the platform is tilted, while the cube-shaped rocks (`#`) will stay in place. You note
    the positions of all of the empty spaces (`.`) and rocks (your puzzle input). For example:

        >>> example = Map.from_text('''
        ...     O....#....
        ...     O.OO#....#
        ...     .....##...
        ...     OO.#O....O
        ...     .O.....O#.
        ...     O.#..O.#.#
        ...     ..O..#O..O
        ...     .......O..
        ...     #....###..
        ...     #OO..#....
        ... ''')

    Start by tilting the lever so all of the rocks will slide north as far as they will go:

        >>> print(example_tilted := example.tilted(Heading.NORTH))
        OOOO·#·O··
        OO··#····#
        OO··O##··O
        O··#·OO···
        ········#·
        ··#····#·#
        ··O··#·O·O
        ··O·······
        #····###··
        #····#····

    You notice that the support beams along the north side of the platform are **damaged**;
    to ensure the platform doesn't collapse, you should calculate the **total load** on the north
    support beams.

    The amount of load caused by a single rounded rock (`O`) is equal to the number of rows from the
    rock to the south edge of the platform, including the row the rock is on. (Cube-shaped rocks
    (`#`) don't contribute to load.) So, the amount of load caused by each rock in each row is as
    follows:

        >>> print(format(example_tilted, 'loads:N'))
        OOOO·#·O·· 10
        OO··#····#  9
        OO··O##··O  8
        O··#·OO···  7
        ········#·  6
        ··#····#·#  5
        ··O··#·O·O  4
        ··O·······  3
        #····###··  2
        #····#····  1

    The total load is the sum of the load caused by all of the **rounded rocks**. In this example,
    the total load is **`136`**:

        >>> example_tilted.total_load(Heading.NORTH)
        136

    Tilt the platform so that the rounded rocks all roll north.
    Afterward, **what is the total load on the north support beams?**

        >>> part_1(example)
        part 1: total load on the north support beams is 136
        136
    """

    result = map_.tilted(Heading.NORTH).total_load()

    print(f"part 1: total load on the north support beams is {result}")
    return result


def part_2(map_: 'Map', spins: int = 1_000_000_000) -> int:
    """
    The parabolic reflector dish deforms, but not in a way that focuses the beam. To do that, you'll
    need to move the rocks to the edges of the platform. Fortunately, a button on the side of the
    control panel labeled "**spin cycle**" attempts to do just that!

    Each **cycle** tilts the platform four times so that the rounded rocks roll **north**, then
    **west**, then **south**, then **east**:

        >>> SPIN_CYCLE_HEADINGS
        [Heading.NORTH, Heading.WEST, Heading.SOUTH, Heading.EAST]

    After each tilt, the rounded rocks roll as far as they can before the platform tilts in the next
    direction. After one cycle, the platform will have finished rolling the rounded rocks in those
    four directions in that order.

    Here's what happens in the example above after each of the first few cycles:

        >>> example = Map.from_file('data/14-example.txt')
        >>> print(after_1_cycle := example.spun())
        ·····#····
        ····#···O#
        ···OO##···
        ·OO#······
        ·····OOO#·
        ·O#···O#·#
        ····O#····
        ······OOOO
        #···O###··
        #··OO#····
        >>> print(after_2_cycles := after_1_cycle.spun())
        ·····#····
        ····#···O#
        ·····##···
        ··O#······
        ·····OOO#·
        ·O#···O#·#
        ····O#···O
        ·······OOO
        #··OO###··
        #·OOO#···O
        >>> print(after_3_cycles := after_2_cycles.spun())
        ·····#····
        ····#···O#
        ·····##···
        ··O#······
        ·····OOO#·
        ·O#···O#·#
        ····O#···O
        ·······OOO
        #···O###·O
        #·OOO#···O

    This process should work if you leave it running long enough, but you're still worried about
    the north support beams. To make sure they'll survive for a while, you need to calculate
    the **total load** on the north support beams after `1_000_000_000` cycles.

    In the above example, after `1e9` cycles, the total load on the north support beams is:

        >>> spun_optimized(example, spins=1_000_000_000).total_load()
        64

    Run the spin cycle for `1_000_000_000` cycles.
    Afterward, **what is the total load on the north support beams?**

        >>> part_2(example)
        part 2: after 1000000000 spin cycles, total load on the north support beams is 64
        64
    """

    result = spun_optimized(map_, spins).total_load()

    print(f"part 2: after {spins} spin cycles, total load on the north support beams is {result}")
    return result


Pos = tuple[int, int]
SPIN_CYCLE_HEADINGS = [Heading.NORTH, Heading.WEST, Heading.SOUTH, Heading.EAST]


class Map:
    def __init__(self, rocks: Iterable[Pos], walls: Iterable[Pos]):
        self.rocks = set(rocks)
        self.walls = set(walls)
        self.bounds = Rect.with_all(self.rocks | self.walls)

    def tilted(self, heading: Heading) -> Self:
        def tilt_key(pos: Pos):
            x, y = pos
            match heading:
                case Heading.NORTH:
                    # y ASC
                    return y, x
                case Heading.SOUTH:
                    # y DESC
                    return -y, x
                case Heading.WEST:
                    # x ASC
                    return x, y
                case Heading.EAST:
                    # x DESC
                    return -x, y
                case _:
                    raise ValueError(heading)

        def tilt_positions(init_pos: Pos) -> Iterable[Pos]:
            pos = init_pos
            while True:
                yield pos
                pos = heading.move(pos)

        new_rocks: set[Pos] = set()
        for rock in sorted(self.rocks, key=tilt_key):
            new_pos = next(
                heading.move(pos, -1)
                for pos in tilt_positions(rock)
                if pos in self.walls
                or pos in new_rocks
                or pos not in self.bounds
            )
            new_rocks.add(new_pos)

        return type(self)(rocks=new_rocks, walls=self.walls)

    def spun(self) -> Self:
        map_ = self
        for heading in SPIN_CYCLE_HEADINGS:
            map_ = map_.tilted(heading)
        return map_

    def total_load(self, heading: Heading = Heading.NORTH) -> int:
        def single_load(pos: Pos) -> int:
            x, y = pos
            match heading:
                case Heading.NORTH:
                    return self.bounds.height - y
                case Heading.SOUTH:
                    return y + 1
                case Heading.WEST:
                    return self.bounds.width - x
                case Heading.EAST:
                    return x + 1
                case _:
                    raise ValueError(heading)

        return sum(single_load(rock) for rock in self.rocks)

    def __str__(self) -> str:
        return format(self)

    def __format__(self, format_spec: str) -> str:
        def char(pos: Pos) -> str:
            if pos in self.rocks:
                return 'O'
            elif pos in self.walls:
                return '#'
            else:
                return '·'

        bounds = self.bounds
        canvas = {pos: char(pos) for pos in bounds}

        if not format_spec:
            pass
        elif format_spec == 'loads:N':
            bounds = bounds.grow_by(right_x=2)
            canvas.update(
                ((bounds.right_x, y), format(self.bounds.height - y, "2"))
                for y in bounds.range_y()
            )
        else:
            raise ValueError("unsupported format specifier")

        return '\n'.join(
            ''.join(canvas.get((x, y), ' ') for x in bounds.range_x())
            for y in bounds.range_y()
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False

        return self.rocks == other.rocks and self.walls == other.walls

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.rocks)))

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        tile_positions = dgroupby_pairs_set(
            (tile, (x, y))
            for y, line in enumerate(lines)
            for x, tile in enumerate(line.strip())
        )
        return cls(rocks=tile_positions['O'], walls=tile_positions['#'])


def spun_optimized(map_: Map, spins: int) -> 'Map':
    pre_cycle, cycle = detect_cycle(map_, Map.spun)
    spins_remaining = (spins - len(pre_cycle)) % len(cycle)
    return cycle[spins_remaining]


def main(input_fn: str = 'data/14-input.txt') -> tuple[int, int]:
    map_ = Map.from_file(input_fn)
    result_1 = part_1(map_)
    result_2 = part_2(map_)
    return result_1, result_2


if __name__ == '__main__':
    main()
