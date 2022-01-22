"""
Advent of Code 2016
Day 1: No Time for a Taxicab
https://adventofcode.com/2016/day/1
"""

from typing import Iterable

from common.file import relative_path
from common.heading import Heading
from common.iteration import first_repeat
from common.iteration import last
from common.utils import some


def part_1(instructions: Iterable['Instr'] | str) -> int:
    """
    You're airdropped near **Easter Bunny Headquarters** in a city somewhere. "Near", unfortunately,
    is as close as you can get - the instructions on the Easter Bunny Recruiting Document the Elves
    intercepted start here, and nobody had time to work them out further.

    The Document indicates that you should start at the given coordinates (where you just landed)
    and face North. Then, follow the provided sequence: either turn left (`L`) or right (`R`)
    90 degrees, then walk forward the given number of blocks, ending at a new intersection.

    There's no time to follow such ridiculous instructions on foot, though, so you take a moment and
    work out the destination. Given that you can only walk on the street grid of the city, how far
    is the shortest path to the destination?

    For example:

      - Following `R2, L3` leaves you `2` blocks East and `3` blocks North, or `5` blocks away:

        >>> last(walk('R2, L3'))
        (2, -3)
        >>> distance_from_origin(_)
        5

      - `R2, R2, R2` leaves you `2` blocks due South of your starting position, or `2` blocks away:

        >>> last(walk('R2, R2, R2'))
        (0, 2)

    **How many blocks away is Easter Bunny HQ?**

        >>> part_1('R5, L5, R5, R3')
        part 1: HQ is 12 blocks away at (10, -2)
        12
    """
    hq_pos = some(last(walk(instructions)))
    distance = distance_from_origin(hq_pos)
    print(f"part 1: HQ is {distance} blocks away at {hq_pos}")
    return distance


def part_2(instructions: Iterable['Instr'] | str) -> int:
    """
    Then, you notice the instructions continue on the back of the Recruiting Document. Easter Bunny
    HQ is actually at the first location you visit twice.

    For example, if your instructions are `R8, R4, R4, R8`, the first location you visit twice is
    `4` blocks away, due East.

        >>> first_repeat(walk('R8, R4, R4, R8'))
        (4, 0)

    **How many blocks away** is the first location you visit twice?

        >>> part_2('R8, R4, R4, R8')
        part 2: HQ is 4 blocks away at (4, 0)
        4
    """
    hq_pos = some(first_repeat(walk(instructions)))
    distance = distance_from_origin(hq_pos)
    print(f"part 2: HQ is {distance} blocks away at {hq_pos}")
    return distance


Instr = tuple[str, int]
Pos = tuple[int, int]


def walk(
    instrs: str | Iterable[Instr],
    start: Pos = (0, 0),
    heading: Heading = Heading.NORTH
) -> Iterable[Pos]:
    if isinstance(instrs, str):
        instrs = instructions_from_line(instrs)

    pos = start
    yield pos

    for direction, distance in instrs:
        heading = turn(direction, heading)
        for _ in range(distance):
            pos = heading.move(pos)
            yield pos


def turn(direction: str, heading: Heading):
    match direction:
        case 'R':
            return heading.right()
        case 'L':
            return heading.left()
        case _:
            raise ValueError(direction)


def distance_from_origin(pos: Pos) -> int:
    x, y = pos
    return abs(x) + abs(y)


def instructions_from_file(fn: str) -> list[Instr]:
    return list(instructions_from_line(open(relative_path(__file__, fn)).readline().strip()))


def instructions_from_line(line: str) -> Iterable[Instr]:
    return (
        (part[0], int(part[1:]))
        for part in line.strip().split(', ')
    )


if __name__ == '__main__':
    instructions_ = instructions_from_file('data/01-input.txt')
    part_1(instructions_)
    part_2(instructions_)
