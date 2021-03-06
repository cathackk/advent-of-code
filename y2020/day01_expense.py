"""
Advent of Code 2020
Day 1: Report Repair
https://adventofcode.com/2020/day/1
"""

from itertools import combinations
from typing import Iterable
from typing import List
from typing import Tuple

from utils import single_value


def part_1(numbers: List[int]) -> int:
    """
    ... they need you to find the two entries that sum to 2020 and then multiply those
    two numbers together.

    For example, suppose your expense report contained the following:

        >>> values = values_from_text('''
        ...
        ...     1721
        ...     979
        ...     366
        ...     299
        ...     675
        ...     1456
        ...
        ... ''')

    In this list, the two entries that sum to 2020 are 1721 and 299.

        >>> find_summation(values, total=2020, count=2)
        (1721, 299)
        >>> 1721 + 299
        2020

    Multiplying them together produces the answer:

        >>> 1721 * 299
        514579

    Of course, your expense report is much larger. Find the two entries that sum to 2020;
    what do you get if you multiply them together?

        >>> part_1(values)
        part 1: 1721 + 299 = 2020; 1721 * 299 = 514579
        514579
    """
    n1, n2 = find_summation(numbers, total=2020, count=2)
    result = n1 * n2
    print(f"part 1: {n1} + {n2} = {n1 + n2}; {n1} * {n2} = {result}")
    return result


def part_2(numbers: List[int]) -> int:
    """
    ... find *three* numbers in your expense report that meet the same criteria.

    Using the above example again, the three entries that sum to 2020 are 979, 366, and 675.

        >>> values = [1721, 979, 366, 299, 675, 1456]
        >>> find_summation(values, total=2020, count=3)
        (979, 366, 675)
        >>> 979 + 366 + 675
        2020

    Multiplying them together produces the answer:

        >>> 979 * 366 * 675
        241861950

    In your expense report, *what is the product of the three entries that sum to 2020?*

        >>> part_2([1721, 979, 366, 299, 675, 1456])
        part 2: 979 + 366 + 675 = 2020; 979 * 366 * 675 = 241861950
        241861950
    """
    n1, n2, n3 = find_summation(numbers, total=2020, count=3)
    result = n1 * n2 * n3
    print(f"part 2: {n1} + {n2} + {n3} = {n1 + n2 + n3}; {n1} * {n2} * {n3} = {result}")
    return result


def find_summation(numbers: List[int], *, total: int, count: int) -> Tuple[int, ...]:
    return single_value(
        comb
        for comb in combinations(numbers, count)
        if sum(comb) == total
    )


def values_from_file(fn: str) -> List[int]:
    return list(values_from_lines(open(fn)))


def values_from_text(text: str) -> List[int]:
    return list(values_from_lines(text.strip().split("\n")))


def values_from_lines(lines: Iterable[str]) -> Iterable[int]:
    return [int(line.strip()) for line in lines]


if __name__ == '__main__':
    numbers_ = values_from_file("data/01-input.txt")
    part_1(numbers_)
    part_2(numbers_)
