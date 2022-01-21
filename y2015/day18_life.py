"""
Advent of Code 2015
Day 18: Like a GIF For Your Yard
https://adventofcode.com/2015/day/18
"""

from collections import Counter
from typing import Iterable

from tqdm import tqdm

from common.file import relative_path
from common.rect import Rect


def part_1(grid: 'Grid', steps: int = 100) -> int:
    """
    After the million lights incident, the fire code has gotten stricter: now, at most ten thousand
    lights are allowed. You arrange them in a 100x100 grid.

    Never one to let you down, Santa again mails you instructions on the ideal lighting
    configuration. With so few lights, he says, you'll have to resort to **animation**.

    Start by setting your lights to the included initial configuration (your puzzle input).
    A `#` means "on", and a `.` means "off".

    Then, animate your grid in steps, where each step decides the next configuration based on
    the current one. Each light's next state (either on or off) depends on its current state and
    the current states of the eight lights adjacent to it (including diagonals). Lights on the edge
    of the grid might have fewer than eight neighbors; the missing ones always count as "off".

    For example, in a simplified 6x6 grid, the light marked `A` has the neighbors numbered
    `1` through `8`, and the light marked `B`, which is on an edge, only has the neighbors marked
    `1` through `5`:

        1B5···
        234···
        ······
        ··123·
        ··8A4·
        ··765·

    The state a light should have next is based on its current state (on or off) plus the **number
    of neighbors that are on**:

      - A light which is **on** stays on when `2` or `3` neighbors are on, and turns off otherwise.
      - A light which is **off** turns on if exactly `3` neighbors are on, and stays off otherwise.

    All of the lights update simultaneously; they all consider the same current state before moving
    to the next.

    Here's a few steps from an example configuration of another 6x6 grid:

        >>> g = Grid.from_file('data/18-example.txt')
        >>> g.on_count
        15
        >>> g4 = animate(g, steps=4, log=True)
        Initial state:
        ·#·#·#
        ···##·
        #····#
        ··#···
        #·#··#
        ####··
        ------
        After 1 step:
        ··##··
        ··##·#
        ···##·
        ······
        #·····
        #·##··
        ------
        After 2 steps:
        ··###·
        ······
        ··###·
        ······
        ·#····
        ·#····
        ------
        After 3 steps:
        ···#··
        ······
        ···#··
        ··##··
        ······
        ······
        ------
        After 4 steps:
        ······
        ······
        ··##··
        ··##··
        ······
        ······

    After `4` steps, this example has four lights on:

        >>> g4.on_count
        4
        >>> g.on_count
        15

    In your grid of 100x100 lights, given your initial configuration, **how many lights are on after
    100 steps**?

        >>> part_1(Grid.from_file('data/18-example.txt'), steps=4)
        part 1: after 4 steps, there are 4 lights on
        4
    """

    result = animate(grid, steps).on_count
    print(f"part 1: after {steps} steps, there are {result} lights on")
    return result


def part_2(grid: 'Grid', steps: int = 100) -> int:
    """
    You flip the instructions over; Santa goes on to point out that this is all just an implementa-
    tion of Conway's Game of Life. At least, it was, until you notice that something's wrong with
    the grid of lights you bought: four lights, one in each corner, are **stuck on** and can't be
    turned off. The example above will actually run like this:

        >>> g = Grid.from_file('data/18-example.txt')
        >>> g5 = animate(with_corner_lights_stuck_on(g), steps=5, log=True)
        Initial state:
        ##·#·#
        ···##·
        #····#
        ··#···
        #·#··#
        ####·#
        ------
        After 1 step:
        #·##·#
        ####·#
        ···##·
        ······
        #···#·
        #·####
        ------
        After 2 steps:
        #··#·#
        #····#
        ·#·##·
        ···##·
        ·#··##
        ##·###
        ------
        After 3 steps:
        #···##
        ####·#
        ··##·#
        ······
        ##····
        ####·#
        ------
        After 4 steps:
        #·####
        #····#
        ···#··
        ·##···
        #·····
        #·#··#
        ------
        After 5 steps:
        ##·###
        ·##··#
        ·##···
        ·##···
        #·#···
        ##···#

    After 5 steps, this example now has 17 lights on:

        >>> g5.on_count
        17

    In your grid of 100x100 lights, given your initial configuration, but with the four corners
    always in the **on** state, **how many lights are on after 100 steps**?

        >>> part_2(g, steps=5)
        part 2: after 5 steps, there are 17 lights on
        17
    """
    result = animate(with_corner_lights_stuck_on(grid), steps).on_count
    print(f"part 2: after {steps} steps, there are {result} lights on")
    return result


Pos = tuple[int, int]


class Grid:
    def __init__(
        self,
        width: int,
        height: int,
        lights_on: Iterable[Pos],
        *,
        lights_stuck_on: Iterable[Pos] = ()
    ):
        assert width > 0
        assert height > 0

        self.bounds = Rect.at_origin(width, height)
        self.lights_stuck_on = set(lights_stuck_on)
        self.lights_on = set(lights_on) | self.lights_stuck_on

        assert all(pos in self.bounds for pos in self.lights_on)
        assert all(pos in self.bounds for pos in self.lights_stuck_on)

    def __repr__(self) -> str:
        tn = type(self).__name__
        stuck_repr = f', lights_stuck_on={self.lights_stuck_on!r}' if self.lights_stuck_on else ''
        return f'{tn}({self.width!r}, {self.height!r}, {self.lights_on!r}{stuck_repr})'

    def __str__(self) -> str:
        return '\n'.join(
            ''.join('#' if (x, y) in self.lights_on else '·' for x in self.bounds.range_x())
            for y in self.bounds.range_y()
        )

    @property
    def width(self) -> int:
        return self.bounds.width

    @property
    def height(self) -> int:
        return self.bounds.height

    @property
    def on_count(self):
        return len(self.lights_on)

    def neighbors(self, pos: Pos) -> Iterable[Pos]:
        x, y = pos
        return (
            npos
            for dx in (-1, 0, +1)
            for dy in (-1, 0, +1)
            if dx != 0 or dy != 0
            if (npos := (x + dx, y + dy)) in self.bounds
        )

    def step(self) -> None:
        def rule(lives: bool, adjc: int) -> bool:
            return adjc in (2, 3) if lives else adjc == 3
        adjs = Counter(neighbor for pos in self.lights_on for neighbor in self.neighbors(pos))
        self.lights_on = {pos for pos, count in adjs.items() if rule(pos in self.lights_on, count)}
        self.lights_on.update(self.lights_stuck_on)

    @classmethod
    def from_file(cls, fn: str) -> 'Grid':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Grid':
        width = None
        height = 0
        lights_on = []

        for y, line in enumerate(lines):
            line = line.strip()
            if width is None:
                width = len(line)
            else:
                assert width == len(line)
            height += 1
            lights_on.extend((x, y) for x, c in enumerate(line) if c == '#')

        return cls(width=width, height=height, lights_on=lights_on)


def animate(grid: Grid, steps: int, log: bool = False) -> 'Grid':
    new_grid = type(grid)(
        width=grid.width,
        height=grid.height,
        lights_on=grid.lights_on,
        lights_stuck_on=grid.lights_stuck_on
    )

    if log:
        print("Initial state:")
        print(new_grid)

    for step in tqdm(range(steps), unit="steps", delay=1.0):
        new_grid.step()

        if log:
            print("-" * new_grid.width)
            noun = "steps" if step > 0 else "step"
            print(f"After {step + 1} {noun}:")
            print(new_grid)

    return new_grid


def with_corner_lights_stuck_on(grid: Grid) -> Grid:
    assert not grid.lights_stuck_on
    return type(grid)(
        width=grid.width,
        height=grid.height,
        lights_on=grid.lights_on,
        lights_stuck_on=grid.bounds.corners()
    )


if __name__ == '__main__':
    grid_ = Grid.from_file('data/18-input.txt')
    part_1(grid_)
    part_2(grid_)
