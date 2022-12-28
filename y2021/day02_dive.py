"""
Advent of Code 2021
Day 2: Dive!
https://adventofcode.com/2021/day/2
"""

from dataclasses import dataclass
from typing import Iterable

from common.file import relative_path


def part_1(commands: Iterable['Command']) -> int:
    """
    The submarine can take a series of commands like `forward 1`, `down 2`, or `up 3`:

      - `forward X` increases the horizontal position by `X` units.
      - `down X` **increases** the depth by `X` units.
      - `up X` **decreases** the depth by `X` units.

    Note that since you're on a submarine, `down` and `up` affect your **depth**, and so they have
    the opposite result of what you might expect.

    The submarine seems to already have a planned course (your puzzle input). You should probably
    figure out where it's going. For example:

        >>> cmds = commands_from_text('''
        ...     forward 5
        ...     down 5
        ...     forward 8
        ...     up 3
        ...     down 8
        ...     forward 2
        ... ''')

    Your horizontal position and depth both start at `0`.

        >>> sub = Submarine()
        >>> sub
        Submarine(horizontal=0, depth=0)

    The steps above would then modify them as follows:

        >>> cmds[0]
        ('forward', 5)
        >>> sub.move(_)
        Submarine(horizontal=5, depth=0)

        >>> cmds[1]
        ('down', 5)
        >>> sub.move(_)
        Submarine(horizontal=5, depth=5)

        >>> cmds[2:4]
        [('forward', 8), ('up', 3)]
        >>> sub.move(*_)
        Submarine(horizontal=13, depth=2)

        >>> cmds[4:]
        [('down', 8), ('forward', 2)]
        >>> sub.move(*_)
        Submarine(horizontal=15, depth=10)

    After following these instructions, you would have a horizontal position of `15` and a depth
    of `10`. Multiplying these together produces **`150`**.

    Calculate the horizontal position and depth you would have after following the planned course.
    **What do you get if you multiply your final horizontal position by your final depth?**

        >>> part_1(cmds)
        part 1: final position is 15 * 10 = 150
        150
    """

    submarine = Submarine()
    submarine.move(*commands)
    result = submarine.horizontal * submarine.depth

    print(f"part 1: final position is {submarine.horizontal} * {submarine.depth} = {result}")
    return result


def part_2(commands: Iterable['Command']) -> int:
    """
    Based on your calculations, the planned course doesn't seem to make any sense. You find
    the submarine manual and discover that the process is actually slightly more complicated.

    In addition to horizontal position and depth, you'll also need to track a third value, **aim**,
    which also starts at `0`.

        >>> sub = Submarine2()
        >>> sub
        Submarine2(horizontal=0, depth=0, aim=0)

    The commands also mean something entirely different than you first thought:

      - `down X` **increases** your aim by `X` units.
      - `up X` **decreases** your aim by `X` units.
      - forward X does two things:
        - It increases your horizontal position by `X` units.
        - It increases your depth by your aim **multiplied by `X`**.

    Again note that since you're on a submarine, `down` and `up` do the opposite of what you might
    expect: "down" means aiming in the positive direction.

    Now, the above example does something different:

        >>> sub.move(('forward', 5))
        Submarine2(horizontal=5, depth=0, aim=0)
        >>> sub.move(('down', 5))
        Submarine2(horizontal=5, depth=0, aim=5)
        >>> sub.move(('forward', 8))
        Submarine2(horizontal=13, depth=40, aim=5)
        >>> sub.move(('up', 3))
        Submarine2(horizontal=13, depth=40, aim=2)
        >>> sub.move(('down', 8))
        Submarine2(horizontal=13, depth=40, aim=10)
        >>> sub.move(('forward', 2))
        Submarine2(horizontal=15, depth=60, aim=10)

    After following these new instructions, you would have a horizontal position of `15` and
    a depth of `60`. Multiplying these produces **`900`**.

    Using this new interpretation of the commands, calculate the horizontal position and depth you
    would have after following the planned course. **What do you get if you multiply your final
    horizontal position by your final depth?**

        >>> part_2([('forward',5), ('down',5), ('forward',8), ('up',3), ('down',8), ('forward',2)])
        part 2: final position is 15 * 60 = 900
        900
    """

    submarine = Submarine2()
    submarine.move(*commands)
    result = submarine.horizontal * submarine.depth

    print(f"part 2: final position is {submarine.horizontal} * {submarine.depth} = {result}")
    return result


Command = tuple[str, int]


def commands_from_file(fn: str) -> list[Command]:
    return list(commands_from_lines(open(relative_path(__file__, fn))))


def commands_from_text(text: str) -> list[Command]:
    return list(commands_from_lines(text.strip().splitlines()))


def commands_from_lines(lines: Iterable[str]) -> Iterable[Command]:
    def parse_command(line: str) -> Command:
        direction, distance = line.strip().split(' ')
        return direction, int(distance)

    return (parse_command(line) for line in lines)


@dataclass()
class Submarine:
    horizontal: int = 0
    depth: int = 0

    def move(self, *commands: Command) -> 'Submarine':
        for command in commands:
            match command:
                case 'forward', distance:
                    self.horizontal += distance
                case 'down', distance:
                    self.depth += distance
                case 'up', distance:
                    self.depth -= distance
                case direction, _:
                    raise ValueError(direction)

        return self


@dataclass()
class Submarine2:
    horizontal: int = 0
    depth: int = 0
    aim: int = 0

    def move(self, *commands: Command) -> 'Submarine2':
        for command in commands:
            match command:
                case 'forward', units:
                    self.horizontal += units
                    self.depth += units * self.aim
                case 'down', units:
                    self.aim += units
                case 'up', units:
                    self.aim -= units
                case direction, _:
                    raise ValueError(direction)

        return self


def main(fn: str = 'data/02-input.txt') -> tuple[int, int]:
    commands = commands_from_file(fn)
    result_1 = part_1(commands)
    result_2 = part_2(commands)
    return result_1, result_2


if __name__ == '__main__':
    main()
