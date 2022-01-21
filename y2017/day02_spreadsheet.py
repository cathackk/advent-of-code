"""
Advent of Code 2017
Day 2: Corruption Checksum
https://adventofcode.com/2017/day/2
"""

from itertools import combinations
from typing import Iterable

from common.file import relative_path


def part_1(sheet: 'Spreadsheet') -> int:
    """
    As you walk through the door, a glowing humanoid shape yells in your direction. "You there! Your
    state appears to be idle. Come help us repair the corruption in this spreadsheet - if we take
    another millisecond, we'll have to display an hourglass cursor!"

    The spreadsheet consists of rows of apparently-random numbers. To make sure the recovery process
    is on the right track, they need you to calculate the spreadsheet's **checksum**. For each row,
    determine the difference between the largest value and the smallest value; the checksum is the
    sum of all of these differences.

    For example, given the following spreadsheet:

        >>> example = spreadsheet_from_text('''
        ...     5 1 9 5
        ...     7 5 3
        ...     2 4 6 8
        ... ''')
        >>> example
        [[5, 1, 9, 5], [7, 5, 3], [2, 4, 6, 8]]

      - The first row's largest and smallest values are `9` and `1`, and their difference is `8`.
      - The second row's largest and smallest values are `7` and `3`, and their difference is `4`.
      - The third row's difference is `6`.

    In this example, the spreadsheet's checksum would be `8 + 4 + 6 = 18`:

        >>> checksum(example)
        18

    **What is the checksum** for the spreadsheet in your puzzle input?

        >>> part_1(example)
        part 1: checksum is 18
        18
    """

    result = checksum(sheet)
    print(f"part 1: checksum is {result}")
    return result


def part_2(sheet: 'Spreadsheet') -> int:
    """
    "Great work; looks like we're on the right track after all. Here's a **star** for your effort."
    However, the program seems a little worried. Can programs **be** worried?

    "Based on what we're seeing, it looks like all the User wanted is some information about the
    **evenly divisible values** in the spreadsheet. Unfortunately, none of us are equipped for that
    kind of calculation - most of us specialize in bitwise operations."

    It sounds like the goal is to find the only two numbers in each row where one evenly divides the
    other - that is, where the result of the division operation is a whole number. They would like
    you to find those numbers on each line, divide them, and add up each line's result.

    For example, given the following spreadsheet:

        >>> example = spreadsheet_from_text('''
        ...     5 9 2 8
        ...     9 4 7 3
        ...     3 8 6 5
        ... ''')
        >>> example
        [[5, 9, 2, 8], [9, 4, 7, 3], [3, 8, 6, 5]]

      - In the first row, the only two numbers that evenly divide are `8` and `2`; the result of
        this division is `4`.
      - In the second row, the two numbers are `9` and `3`; the result is `3`.
      - In the third row, the result is `2`.

    In this example, the sum of the results would be `4 + 3 + 2 = 9`:

        >>> divsum(example)
        9

    What is the **sum of each row's result** in your puzzle input?

        >>> part_2(example)
        part 2: divsum is 9
        9
    """

    result = divsum(sheet)
    print(f"part 2: divsum is {result}")
    return result


Spreadsheet = list[list[int]]


def checksum(sheet: Spreadsheet) -> int:
    return sum(
        max(row) - min(row)
        for row in sheet
    )


def divisibles(sheet: Spreadsheet) -> Iterable[tuple[int, int]]:
    return (
        next(
            (a, b)
            for a, b in combinations(sorted(row, reverse=True), 2)
            if a % b == 0
        )
        for row in sheet
    )


def divsum(sheet: Spreadsheet) -> int:
    return sum(
        a // b
        for a, b in divisibles(sheet)
    )


def spreadsheet_from_text(text: str) -> Spreadsheet:
    return spreadsheet_from_lines(text.strip().splitlines())


def spreadsheet_from_file(fn: str) -> Spreadsheet:
    return spreadsheet_from_lines(open(relative_path(__file__, fn)))


def spreadsheet_from_lines(lines: Iterable[str]) -> Spreadsheet:
    return [
        [int(value) for value in line.strip().split()]
        for line in lines
    ]


if __name__ == '__main__':
    sheet_ = spreadsheet_from_file('data/02-input.txt')
    part_1(sheet_)
    part_2(sheet_)
