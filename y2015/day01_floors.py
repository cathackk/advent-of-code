"""
Advent of Code 2015
Day 1: Not Quite Lisp
https://adventofcode.com/2015/day/1
"""

from typing import Iterable

from common.utils import last
from common.utils import relative_path


def part_1(instructions: str) -> int:
    """
    Santa is trying to deliver presents in a large apartment building, but he can't find the right
    floor - the directions he got are a little confusing. He starts on the ground floor (floor `0`)
    and then follows the instructions one character at a time.

    An opening parenthesis, `(`, means he should go up one floor, and a closing parenthesis, `)`,
    means he should go down one floor.

    The apartment building is very tall, and the basement is very deep; he will never find the top
    or bottom floors.

    For example:

        >>> floor_number('(())'), floor_number('()()')
        (0, 0)
        >>> floor_number('((('), floor_number('(()(()('), floor_number('))(((((')
        (3, 3, 3)
        >>> floor_number('())'), floor_number('))(')
        (-1, -1)
        >>> floor_number(')))'), floor_number(')())())')
        (-3, -3)

    To **what floor** do the instructions take Santa?

        >>> part_1('(((()))))(((((')
        part 1: Santa goes to floor 4
        4
    """

    result = floor_number(instructions)
    print(f"part 1: Santa goes to floor {result}")
    return result


def part_2(instructions: str) -> int:
    """
    Now, given the same instructions, find the **position** of the first character that causes him
    to enter the basement (floor `-1`). The first character in the instructions has position `1`,
    the second character has position `2`, and so on.

    For example:

        >>> basement_at(')')
        1
        >>> basement_at('()())')
        5

    What is the **position** of the character that causes Santa to first enter the basement?

        >>> part_2('(((()))))(((((')
        part 2: Santa enters the basement at position 9
        9
    """

    result = basement_at(instructions)
    print(f"part 2: Santa enters the basement at position {result}")
    return result


def floor_number(line: str) -> int:
    return last(floors_from_str(line))


def basement_at(line: str) -> int:
    return next(pos for pos, floor in enumerate(floors_from_str(line)) if floor < 0)


def floors_from_str(line: str) -> Iterable[int]:
    current = 0
    yield current
    for char in line:
        current += {'(': +1, ')': -1}[char]
        yield current


def instructions_from_file(fn: str) -> str:
    return open(relative_path(__file__, fn)).readline().strip()


if __name__ == '__main__':
    instructions_ = instructions_from_file('data/01-input.txt')
    part_1(instructions_)
    part_2(instructions_)
