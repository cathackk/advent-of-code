"""
Advent of Code 2020
Day 1: Report Repair
https://adventofcode.com/2020/day/1
"""

from itertools import combinations
from typing import List
from typing import Tuple

from utils import single_value


def part_1(numbers: List[int]) -> int:
    """
    ... they need you to find the two entries that sum to 2020 and then multiply those
    two numbers together.

    For example, suppose your expense report contained the following:

        1721
        979
        366
        299
        675
        1456

    In this list, the two entries that sum to 2020 are 1721 and 299. Multiplying them together
    produces 1721 * 299 = 514579, so the correct answer is 514579.

    >>> part_1([1721, 979, 366, 299, 675, 1456])
    part 1: 1721 + 299 = 2020; 1721 * 299 = 514579
    514579

    Of course, your expense report is much larger. Find the two entries that sum to 2020;
    what do you get if you multiply them together?
    """
    n1, n2 = find_summation(numbers, total=2020, count=2)
    result = n1 * n2
    print(f"part 1: {n1} + {n2} = {n1 + n2}; {n1} * {n2} = {result}")
    return result


def part_2(numbers: List[int]) -> int:
    """
    ... find *three* numbers in your expense report that meet the same criteria.

    Using the above example again, the three entries that sum to 2020 are 979, 366, and 675.
    Multiplying them together produces the answer, 241861950.

    >>> part_2([1721, 979, 366, 299, 675, 1456])
    part 2: 979 + 366 + 675 = 2020; 979 * 366 * 675 = 241861950
    241861950

    In your expense report, what is the product of the three entries that sum to 2020?
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


def load_data(fn) -> List[int]:
    with open(fn) as f:
        return [int(line) for line in f]


if __name__ == '__main__':
    numbers_ = load_data("data/01-input.txt")
    part_1(numbers_)
    part_2(numbers_)
