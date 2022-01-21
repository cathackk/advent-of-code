"""
Advent of Code 2021
Day 1: Sonar Sweep
https://adventofcode.com/2021/day/1
"""

from typing import Iterable

from common.file import relative_path
from common.iteration import slidingw


def part_1(values: Iterable[int]) -> int:
    """
    On a small screen, the sonar sweep report (your puzzle input) appears: each line is
    a measurement of the sea floor depth as the sweep looks further and further away from
    the submarine.

    For example, suppose you had the following report:

        >>> measurements = [199, 200, 208, 210, 200, 207, 240, 269, 260, 263]

    This report indicates that, scanning outward from the submarine, the sonar sweep found
    depths of `199`, `200`, `208`, `210`, and so on.

    The first order of business is to figure out how quickly the depth increases.

    To do this, count the number of times a depth measurement increases from the previous
    measurement. (There is no measurement before the first measurement.) In the example above,
    there are **7** measurements that are larger than the previous measurement.

        >>> count_increases(measurements)
        7

    **How many measurements are larger than the previous measurement?**

        >>> part_1(measurements)
        part 1: 7 increases
        7
    """

    result = count_increases(values)

    print(f"part 1: {result} increases")
    return result


def part_2(values: Iterable[int]) -> int:
    """
    Considering every single measurement isn't as useful as you expected: there's just too much
    noise in the data.

    Instead, consider sums of a **three-measurement sliding window**. Again considering the above
    example:

        >>> measurements = [199, 200, 208, 210, 200, 207, 240, 269, 260, 263]
        >>> [sum(w) for w in slidingw(measurements, 3)]
        [607, 618, 618, 617, 647, 716, 769, 792]

    In this example, there are **5** sums that are larger than the previous sum.

        >>> count_increases(_)
        5

    Consider sums of a three-measurement sliding window.
    **How many sums are larger than the previous sum?**

        >>> part_2(measurements)
        part 2: 5 increases
        5
    """

    triples = (sum(w) for w in slidingw(values, 3))
    result = count_increases(triples)

    print(f"part 2: {result} increases")
    return result


def count_increases(values: Iterable[int]) -> int:
    return sum(v1 > v0 for v0, v1 in slidingw(values, 2))


def values_from_file(fn: str) -> list[int]:
    return [int(line.strip()) for line in open(relative_path(__file__, fn))]


if __name__ == '__main__':
    values_ = list(values_from_file('data/01-input.txt'))
    part_1(values_)
    part_2(values_)
