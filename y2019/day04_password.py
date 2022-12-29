"""
Advent of Code 2019
Day 4: Secure Container
https://adventofcode.com/2019/day/4
"""

from collections import Counter
from typing import Iterable

from common.file import relative_path
from common.iteration import zip1


def part_1(passwords: Iterable[int]) -> int:
    """
    You arrive at the Venus fuel depot only to discover it's protected by a password. The Elves had
    written the password on a sticky note, but someone threw it out.

    However, they do remember a few key facts about the password:

      - It is a six-digit number.
      - The value is within the range given in your puzzle input.
      - Two adjacent digits are the same (like `22` in `122345`).
      - Going from left to right, the digits **never decrease**; they only ever increase or stay the
        same (like `111123` or `135679`).

    Other than the range rule, the following are true:

      - `111111` meets these criteria (double `11`, never decreases):

        >>> is_valid_1(111111)
        True

      - `223450` does not meet these criteria (decreasing pair of digits `50`):

        >>> is_valid_1(223450)
        False

      - `123789` does not meet these criteria (no double):

        >>> is_valid_1(123789)
        False

    **How many different passwords** within the range given in your puzzle input meet these
    criteria?

        >>> part_1([111111, 223450, 123789])
        part 1: found 1 valid passwords
        1
    """

    result = sum(1 for password in passwords if is_valid_1(password))

    print(f"part 1: found {result} valid passwords")
    return result


def part_2(passwords: Iterable[int]) -> int:
    """
    An Elf just remembered one more important detail: the two adjacent matching digits **are not
    part of a larger group of matching digits**.

    Given this additional criterion, but still ignoring the range rule, the following are now true:

      - `112233` meets these criteria because the digits never decrease and all repeated digits are
        exactly two digits long:

        >>> is_valid_2(112233)
        True

      - `123444` no longer meets the criteria (the repeated `44` is part of larger group of `444`):

        >>> is_valid_2(123444)
        False

      - `111122` meets the criteria (even though `1` is repeated more than twice, it still contains
        a double `22`):

        >>> is_valid_2(111122)
        True

    **How many different passwords** within the range given in your puzzle input meet all of the
    criteria?

        >>> part_2([112233, 123444, 111122])
        part 2: actually found 2 valid passwords
        2
    """

    result = sum(1 for password in passwords if is_valid_2(password))

    print(f"part 2: actually found {result} valid passwords")
    return result


def is_valid_1(password_num: int) -> bool:
    return (
        len(password_str := str(password_num)) == 6 and
        all(char_1 <= char_2 for char_1, char_2 in zip1(password_str)) and
        len(set(password_str)) < 6
    )


def is_valid_2(password_num: int) -> bool:
    return (
        is_valid_1(password_num) and
        Counter(Counter(str(password_num)).values())[2] >= 1
    )


def range_from_file(fn: str) -> range:
    return range_from_line(open(relative_path(__file__, fn)).readline())


def range_from_line(line: str) -> range:
    start, end = line.strip().split('-')
    return range(int(start), int(end) + 1)


def main(fn: str = 'data/04-input.txt') -> tuple[int, int]:
    password_range = range_from_file(fn)
    result_1 = part_1(password_range)
    result_2 = part_2(password_range)
    return result_1, result_2


if __name__ == '__main__':
    main()
