"""
Advent of Code 2020
Day 17: Conway Cubes
https://adventofcode.com/2020/day/17
"""

from collections import Counter
from itertools import product
from typing import Iterable

from common.rect import HyperCuboid
from common.utils import relative_path
from common.utils import single_value


def part_1(initial_state: set['Pos'], cycles: int = 6) -> int:
    """
    The pocket dimension contains an infinite 3-dimensional grid. At every integer 3-dimensional
    coordinate (`x,y,z`), there exists a single cube which is either *active* or *inactive*.

    In the initial state of the pocket dimension, almost all cubes start *inactive*. The only
    exception to this is a small flat region of cubes (your puzzle input); the cubes in this region
    start in the specified *active* (`#`) or inactive (`.`) state.

    The energy source then proceeds to boot up by executing six *cycles*.

    Each cube only ever considers its *neighbors*: any of the 26 other cubes where any of their
    coordinates differ by at most `1`. For example, given the cube at `x=1,y=2,z=3`, its neighbors
    include the cube at `x=2,y=2,z=2`, the cube at `x=0,y=2,z=3`, and so on.

        >>> ns = set(neighbors((1, 2, 3)))
        >>> len(ns)
        26
        >>> (2, 2, 2) in ns
        True
        >>> (0, 2, 3) in ns
        True
        >>> (1, 2, 3) in ns
        False

    During a cycle, *all* cubes *simultaneously* change their state according to the following
    rules:

        - If a cube is *active* and *exactly 2 or 3* of its neighbors are also active, the cube
          remains *active*. Otherwise, the cube becomes *inactive*.
        - If a cube is *inactive* but exactly *3 of its neighbors* are active, the cube becomes
          *active*. Otherwise, the cube remains *inactive*.

    The engineers responsible for this experimental energy source would like you to simulate the
    pocket dimension and determine what the configuration of cubes should be at the end of the
    six-cycle boot process.

    For example, consider the following initial state:

        >>> state_0 = state_from_text(dimensions=3, text='''
        ...
        ...     .#.
        ...     ..#
        ...     ###
        ...
        ... ''')
        >>> sorted(state_0)
        [(0, 2, 0), (1, 0, 0), (1, 2, 0), (2, 1, 0), (2, 2, 0)]

    Even though the pocket dimension is 3-dimensional, this initial state represents a small
    2-dimensional slice of it. (In particular, this initial state defines a 3x3x1 region of the
    3-dimensional space.)

    Simulating a few cycles from this initial state produces the following configurations, where
    the result of each cycle is shown layer-by-layer at each given `z` coordinate (and the frame of
    view follows the active cells in each cycle):

        >>> state_3 = simulate(state_0, cycles=3, print_progress=True)
        Before any cycles:
            z=0
                .#.
                ..#
                ###
        After 1 cycle:
            z=-1
                #..
                ..#
                .#.
            z=0
                #.#
                .##
                .#.
            z=1
                #..
                ..#
                .#.
        After 2 cycles:
            z=-2
                .....
                .....
                ..#..
                .....
                .....
            z=-1
                ..#..
                .#..#
                ....#
                .#...
                .....
            z=0
                ##...
                ##...
                #....
                ....#
                .###.
            z=1
                ..#..
                .#..#
                ....#
                .#...
                .....
            z=2
                .....
                .....
                ..#..
                .....
                .....
        After 3 cycles:
            z=-2
                .......
                .......
                ..##...
                ..###..
                .......
                .......
                .......
            z=-1
                ..#....
                ...#...
                #......
                .....##
                .#...#.
                ..#.#..
                ...#...
            z=0
                ...#...
                .......
                #......
                .......
                .....##
                .##.#..
                ...#...
            z=1
                ..#....
                ...#...
                #......
                .....##
                .#...#.
                ..#.#..
                ...#...
            z=2
                .......
                .......
                ..##...
                ..###..
                .......
                .......
                .......
        >>> len(state_3)
        38

    After the full six-cycle boot process completes, *`112`* cubes are left in the *active* state.

        >>> state_6 = simulate(state_3, cycles=3)
        >>> len(state_6)
        112

    Starting with your given initial configuration, simulate six cycles. *How many cubes are left
    in the active state after the sixth cycle?*

        >>> part_1(state_0, cycles=6)
        part 1: after 6 cycles, there will be 112 active cubes
        112
    """

    assert state_dimensions(initial_state) == 3
    result = len(simulate(initial_state, cycles))

    print(f"part 1: after {cycles} cycles, there will be {result} active cubes")
    return result


def part_2(initial_state: set['Pos'], cycles: int = 6) -> int:
    """
    For some reason, your simulated results don't match what the experimental energy source
    engineers expected. Apparently, the pocket dimension actually has *four spatial dimensions*,
    not three.

    The pocket dimension contains an infinite 4-dimensional grid. At every integer 4-dimensional
    coordinate (`x,y,z,w`), there exists a single cube (really, a *hypercube*) which is still
    either *active* or *inactive*.

    Each cube only ever considers its *neighbors*: any of the 80 other cubes where any of their
    coordinates differ by at most 1. For example, given the cube at `x=1,y=2,z=3,w=4`, its
    neighbors include the cube at `x=2,y=2,z=3,w=3`, the cube at `x=0,y=2,z=3,w=4`, and so on.

        >>> ns = set(neighbors((1, 2, 3, 4)))
        >>> len(ns)
        80
        >>> (2, 2, 3, 3) in ns
        True
        >>> (0, 2, 3, 4) in ns
        True
        >>> (1, 2, 3, 4) in ns
        False

    The initial state of the pocket dimension still consists of a small flat region of cubes.
    Furthermore, the same rules for cycle updating still apply: during each cycle, consider the
    *number of active neighbors* of each cube.

    For example, consider the same initial state as in the example above. Even though the pocket
    dimension is 4-dimensional, this initial state represents a small 2-dimensional slice of it.
    (In particular, this initial state defines a 3x3x1x1 region of the 4-dimensional space.)

        >>> state_0 = state_from_text(dimensions=4, text='''
        ...
        ...     .#.
        ...     ..#
        ...     ###
        ...
        ... ''')
        >>> sorted(state_0)
        [(0, 2, 0, 0), (1, 0, 0, 0), (1, 2, 0, 0), (2, 1, 0, 0), (2, 2, 0, 0)]

    Simulating a few cycles from this initial state produces the following configurations, where
    the result of each cycle is shown layer-by-layer at each given `z` and `w` coordinate:

        >>> state_2 = simulate(state_0, cycles=2, print_progress=True)
        Before any cycles:
            z=0, w=0
                .#.
                ..#
                ###
        After 1 cycle:
            z=-1, w=-1
                #..
                ..#
                .#.
            z=0, w=-1
                #..
                ..#
                .#.
            z=1, w=-1
                #..
                ..#
                .#.
            z=-1, w=0
                #..
                ..#
                .#.
            z=0, w=0
                #.#
                .##
                .#.
            z=1, w=0
                #..
                ..#
                .#.
            z=-1, w=1
                #..
                ..#
                .#.
            z=0, w=1
                #..
                ..#
                .#.
            z=1, w=1
                #..
                ..#
                .#.
        After 2 cycles:
            z=-2, w=-2
                .....
                .....
                ..#..
                .....
                .....
            z=0, w=-2
                ###..
                ##.##
                #...#
                .#..#
                .###.
            z=2, w=-2
                .....
                .....
                ..#..
                .....
                .....
            z=-2, w=0
                ###..
                ##.##
                #...#
                .#..#
                .###.
            z=2, w=0
                ###..
                ##.##
                #...#
                .#..#
                .###.
            z=-2, w=2
                .....
                .....
                ..#..
                .....
                .....
            z=0, w=2
                ###..
                ##.##
                #...#
                .#..#
                .###.
            z=2, w=2
                .....
                .....
                ..#..
                .....
                .....

    After the full six-cycle boot process completes, *`848`* cubes are left in the *active* state.

        >>> state_6 = simulate(state_2, cycles=4)
        >>> len(state_6)
        848

    Starting with your given initial configuration, simulate six cycles in a 4-dimensional space.
    *How many cubes are left in the active state after the sixth cycle?*

        >>> part_2(state_0, cycles=6)
        part 2: after 6 cycles, there will be 848 active hypercubes
        848
    """

    assert state_dimensions(initial_state) == 4
    result = len(simulate(initial_state, cycles))

    print(f"part 2: after {cycles} cycles, there will be {result} active hypercubes")
    return result


def life_rule(active: bool, active_neighbors_count: int) -> bool:
    if active:
        return active_neighbors_count in (2, 3)
    else:
        return active_neighbors_count == 3


# position with arbitrary number of dimensions
Pos = tuple[int, ...]


def simulate(state: set[Pos], cycles: int, print_progress: bool = False):
    if print_progress:
        print_state(state, 0)

    for cycle in range(cycles):
        active_neighbors = Counter(
            npos
            for pos in state
            for npos in neighbors(pos)
        )
        state = {
            pos
            for pos, ns in active_neighbors.items()
            if life_rule(pos in state, ns)
        }

        if print_progress:
            print_state(state, cycle + 1)

    return state


def neighbors(pos: Pos) -> Iterable[Pos]:
    return (
        tuple(p + d for p, d in zip(pos, delta))
        for delta in product((-1, 0, +1), repeat=len(pos))
        if any(d != 0 for d in delta)
    )


def state_dimensions(state: set[Pos]) -> int:
    return single_value(set(len(pos) for pos in state))


def state_from_text(dimensions: int, text: str) -> set[Pos]:
    return set(active_positions_from_lines(dimensions, text.strip().split("\n")))


def state_from_file(dimensions: int, fn: str) -> set[Pos]:
    return set(active_positions_from_lines(dimensions, relative_path(__file__, fn)))


def active_positions_from_lines(dimensions: int, lines: Iterable[str]) -> Iterable[Pos]:
    assert dimensions >= 2
    padding = tuple(0 for _ in range(dimensions - 2))
    return (
        (x, y) + padding
        for y, line in enumerate(lines)
        for x, ch in enumerate(line.strip())
        if ch == '#'
    )


def print_state(state: set[Pos], cycle: int):
    pad_1 = " " * 4
    pad_2 = " " * 8

    match cycle:
        case None:
            pad_1 = ""
            pad_2 = " " * 4
        case 0:
            print("Before any cycles:")
        case 1:
            print("After 1 cycle:")
        case _:
            print(f"After {cycle} cycles:")

    # find the min/max corner of the multi-dimensional space to be printed
    bounds = HyperCuboid.with_all(state)
    assert 2 <= len(bounds) <= 8

    # iterate over 3rd and higher dimensions
    for hyperpos in bounds[2:]:
        # the remaining two dimensions (x, y) form a printable 2D plane
        plane_lines = []
        for y in bounds[1]:
            plane_lines.append(''.join(
                '#' if (x, y) + hyperpos in state else '.'
                for x in bounds[0]
            ))

        # print the plane only if it contains any active position
        if any('#' in line for line in plane_lines):
            print(pad_1 + ', '.join(
                f'{c}={v}'
                for c, v in zip('zwvuts', reversed(hyperpos))
            ))
            for line in plane_lines:
                print(pad_2 + line)


if __name__ == '__main__':
    FILENAME = 'data/17-input.txt'
    part_1(state_from_file(3, FILENAME))
    part_2(state_from_file(4, FILENAME))
