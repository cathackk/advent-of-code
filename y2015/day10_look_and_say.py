"""
Advent of Code 2015
Day 10: Elves Look, Elves Say
https://adventofcode.com/2015/day/10
"""

from itertools import groupby
from typing import Iterable

from common.file import relative_path
from common.iteration import last


def part_1(starting_number: str, iterations: int = 40) -> str:
    """
    Today, the Elves are playing a game called **look-and-say**. They take turns making sequences by
    reading aloud the previous sequence and using that reading as the next sequence.

    For example, `211` is read as "one two, two ones", which becomes `1221` (1x `2`, 2x `1`s).

        >>> las('211')
        '1221'

    Look-and-say sequences are generated iteratively, using the previous value as input for the next
    step. For each step, take the previous value, and replace each run of digits (like `111`) with
    the number of digits (`3`) followed by the digit itself (`1`).

    For example:

        >>> list(las_sequence('1', iterations=5))
        ['1', '11', '21', '1211', '111221', '312211']

    Starting with the digits in your puzzle input, apply this process **40 times**.
    What is the length of the result?

        >>> part_1('1')  # doctest: +ELLIPSIS
        part 1: after 40 iterations, sequence has length 82350
        '111312211312111322212321121113121112131112132112311321322112111312212321121113122112131...'
    """

    seq = last(las_sequence(starting_number, iterations))
    result = len(seq)
    print(f"part 1: after {iterations} iterations, sequence has length {result}")
    return seq


def part_2(starting_number: str, iterations: int = 50) -> str:
    """
    Now, starting again with the digits in your puzzle input, apply this process **50 times**.
    What is the length of the new result?

        >>> part_2('1')  # doctest: +ELLIPSIS
        part 2: after 50 iterations, sequence has length 1166642
        '311311222113111231133211121312211231131112311211133112111312211213211312111322211231131...'
    """

    seq = last(las_sequence(starting_number, iterations))
    result = len(seq)
    more = " more" if len(starting_number) >= 100 else ""
    print(f"part 2: after {iterations}{more} iterations, sequence has length {result}")
    return seq


def las(number: str) -> str:
    return ''.join(
        str(len(list(group))) + digit
        for digit, group in groupby(number)
    )


def las_sequence(starting_number: str, iterations: int) -> Iterable[str]:
    yield starting_number

    number = starting_number
    for _ in range(iterations):
        number = las(number)
        yield number


def number_from_file(fn: str) -> str:
    return open(relative_path(__file__, fn)).readline().strip()


if __name__ == '__main__':
    starting_number_ = number_from_file('data/10-input.txt')
    seq_40 = part_1(starting_number_)
    part_2(seq_40, iterations=10)
