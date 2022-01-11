"""
Advent of Code 2020
Day 12: Rain Risk
https://adventofcode.com/2020/day/12
"""
from typing import Iterable

from common.heading import Heading
from common.utils import relative_path


def part_1(instructions: list['Instruction']) -> int:
    """
    The navigation instructions (your puzzle input) consists of a sequence of single-character
    actions paired with integer input values. After staring at them for a few minutes, you work out
    what they probably mean:

        - Action `N` means to move *north* by the given value.
        - Action `S` means to move *south* by the given value.
        - Action `E` means to move *east* by the given value.
        - Action `W` means to move *west* by the given value.
        - Action `L` means to turn *left* the given number of degrees.
        - Action `R` means to turn *right* the given number of degrees.
        - Action `F` means to move *forward* by the given value in the direction the ship is
          currently facing.

    The ship starts by facing *east*.

        >>> ship = Ship(heading=Heading.EAST)
        >>> ship
        Ship(pos=(0, 0), heading=Heading.EAST)

    Only the `L` and `R` actions change the direction the ship is
    facing. (That is, if the ship is facing east and the next instruction is `N10`, the ship would
    move north 10 units, but would still move east if the following action were `F`.)

    For example:

        >>> instrs = instructions_from_text('''
        ...     F10
        ...     N3
        ...     F7
        ...     R90
        ...     F11
        ... ''')
        >>> instrs
        [('F', 10), ('N', 3), ('F', 7), ('R', 90), ('F', 11)]

    These instructions would be handled as follows:

        - `F10` would move the ship 10 units east (because the ship starts by facing east).

            >>> ship.step(instrs[0])
            Ship(pos=(10, 0), heading=Heading.EAST)

        - `N3` would move the ship 3 units north.

            >>> ship.step(instrs[1])
            Ship(pos=(10, -3), heading=Heading.EAST)

        - `F7` would move the ship another 7 units east (because the ship is still facing east).

            >>> ship.step(instrs[2])
            Ship(pos=(17, -3), heading=Heading.EAST)

        - `R90` would cause the ship to turn right by 90 degrees and face south.

            >>> ship.step(instrs[3])
            Ship(pos=(17, -3), heading=Heading.SOUTH)

        - `F11` would move the ship 11 units south.

            >>> ship.step(instrs[4])
            Ship(pos=(17, 8), heading=Heading.SOUTH)

    At the end of these instructions, the ship's Manhattan distance (sum of the absolute values of
    its east/west position and its north/south position) from its starting position is 17 + 8 = 25.

        >>> ship.distance_from_start()
        25

    Figure out where the navigation instructions lead. *What is the Manhattan distance between that
    location and the ship's starting position?*

        >>> part_1(instrs)
        part 1: ship's final position is 25 units away from its start
        25
    """

    result = Ship(heading=Heading.EAST).follow(instructions).distance_from_start()

    print(f"part 1: ship's final position is {result} units away from its start")
    return result


def part_2(instructions: list['Instruction']) -> int:
    """
    Before you can give the destination to the captain, you realize that the actual action meanings
    were printed on the back of the instructions the whole time.

    Almost all of the actions indicate how to move a *waypoint* which is relative to the ship's
    position:

    - Action `N` means to move the waypoint *north* by the given value.
    - Action `S` means to move the waypoint *south* by the given value.
    - Action `E` means to move the waypoint *east* by the given value.
    - Action `W` means to move the waypoint *west* by the given value.
    - Action `L` means to rotate the waypoint around the ship *left* (*counter-clockwise*)
      the given number of degrees.
    - Action `R` means to rotate the waypoint around the ship *right* (*clockwise*) the given
      number of degrees.
    - Action `F` means to move *forward* to the waypoint a number of times equal to the given
      value.

    The waypoint starts *10 units east and 1 unit north* relative to the ship. The waypoint is
    relative to the ship; that is, if the ship moves, the waypoint moves with it.

        >>> ship = Ship(waypoint=(10, -1))
        >>> ship
        Ship(pos=(0, 0), waypoint=(10, -1))

    For example, using the same instructions as above:

        - `F10` moves the ship to the waypoint 10 times (a total of 100 units E and 10 units N).

            >>> ship.step(('F', 10))
            Ship(pos=(100, -10), waypoint=(10, -1))

        - `N3` moves the waypoint 3 units north.

            >>> ship.step(('N', 3))
            Ship(pos=(100, -10), waypoint=(10, -4))

        - `F7` moves the ship to the waypoint 7 times (a total of 70 units E and 28 units N).

            >>> ship.step(('F', 7))
            Ship(pos=(170, -38), waypoint=(10, -4))

        - `R90` rotates the waypoint around the ship clockwise 90 degrees.

            >>> ship.step(('R', 90))
            Ship(pos=(170, -38), waypoint=(4, 10))

        - `F11` moves the ship to the waypoint 11 times (a total of 44 units E and 110 units S)

            >>> ship.step(('F', 11))
            Ship(pos=(214, 72), waypoint=(4, 10))

    After these operations, the ship's Manhattan distance from its starting position is
    214 + 72 = 286.

    Figure out where the navigation instructions actually lead. *What is the Manhattan distance
    between that location and the ship's starting position?*

        >>> part_2([('F', 10), ('N', 3), ('F', 7), ('R', 90), ('F', 11)])
        part 2: ship's final position is 286 units away from its start
        286
    """

    result = Ship(waypoint=(10, -1)).follow(instructions).distance_from_start()

    print(f"part 2: ship's final position is {result} units away from its start")
    return result


Instruction = tuple[str, int]


def instructions_from_text(text: str) -> list[Instruction]:
    return list(instructions_from_lines(text.strip().split("\n")))


def instructions_from_file(fn: str) -> list[Instruction]:
    return list(instructions_from_lines(relative_path(__file__, fn)))


def instructions_from_lines(lines: Iterable[str]) -> Iterable[Instruction]:
    return (
        (line_stripped[0], int(line_stripped[1:]))
        for line in lines
        if (line_stripped := line.strip())
    )


Pos = tuple[int, int]


class Ship:
    def __init__(self, pos: Pos = (0, 0), heading: Heading = None, waypoint: Pos = None):
        assert (heading is None) != (waypoint is None),\
            "exactly one of (heading, waypoint) must be given"

        self.pos = pos
        self.heading = heading
        self.waypoint = waypoint

    def __repr__(self):
        if self.heading:
            return f'{type(self).__name__}(pos={self.pos}, heading={self.heading})'
        else:
            return f'{type(self).__name__}(pos={self.pos}, waypoint={self.waypoint})'

    def step(self, instruction: Instruction) -> 'Ship':
        match instruction:
            case ('N' | 'E' | 'S' | 'W' as heading), value:
                absolute_heading = Heading.from_letter(heading)
                if self.waypoint:
                    self.waypoint = absolute_heading.move(self.waypoint, distance=value)
                else:
                    self.pos = absolute_heading.move(self.pos, distance=value)

            case 'F', value:
                if self.waypoint:
                    x, y = self.pos
                    dx, dy = self.waypoint
                    self.pos = (x + value * dx, y + value * dy)
                else:
                    self.pos = self.heading.move(self.pos, distance=value)

            case ('L' | 'R' as action), (90 | 180 | 270 as angle):
                right_turns = (angle if action == 'R' else (-angle % 360)) // 90

                if self.waypoint:
                    for _ in range(right_turns):
                        wpx, wpy = self.waypoint
                        self.waypoint = (-wpy, wpx)
                else:
                    for _ in range(right_turns):
                        self.heading = self.heading.right()

            case ('L' | 'R'), angle:
                raise ValueError(f"unsupported turn value: {angle}")

            case action, value:
                raise ValueError(f"unsupported action: {action}, {value}")

        return self

    def follow(self, instructions: Iterable[Instruction]) -> 'Ship':
        for instr in instructions:
            self.step(instr)

        return self

    def distance_from_start(self) -> int:
        x, y = self.pos
        return abs(x) + abs(y)


if __name__ == '__main__':
    instructions_ = instructions_from_file('data/12-input.txt')
    assert len(instructions_) == 747

    part_1(instructions_)
    part_2(instructions_)
