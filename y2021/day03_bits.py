"""
Advent of Code 2021
Day 3: Binary Diagnostic
https://adventofcode.com/2021/day/3
"""

from collections import Counter
from typing import Callable
from typing import Iterable

from common.utils import relative_path


def part_1(values: list[str]) -> int:
    """
    The diagnostic report (your puzzle input) consists of a list of binary numbers which, when
    decoded properly, can tell you many useful things about the conditions of the submarine.
    The first parameter to check is the **power consumption**.

    You need to use the binary numbers in the diagnostic report to generate two new binary numbers
    (called the **gamma rate** and the **epsilon rate**). The power consumption can then be found
    by multiplying the gamma rate by the epsilon rate.

    Each bit in the gamma rate can be determined by finding the **most common bit** in
    the corresponding position of all numbers in the diagnostic report. For example, given
    the following diagnostic report:

        >>> report = [
        ...     '00100', '11110', '10110', '10111', '10101', '01111',
        ...     '00111', '11100', '10000', '11001', '00010', '01010'
        ... ]

    Considering only the first bit of each number, there are five `0` bits and seven `1` bits.
    Since the most common bit is `1`, the first bit of the gamma rate is `1`.

        >>> most_common_bit(report, position=0)
        '1'

    The most common second bit of the numbers in the diagnostic report is `0`, so the second bit
    of the gamma rate is `0`.

        >>> most_common_bit(report, position=1)
        '0'

    The most common value of the third, fourth, and fifth bits are `1`, `1`, and `0`, respectively,
    and so the final three bits of the gamma rate are `110`.

        >>> [most_common_bit(report, pos) for pos in range(2, 5)]
        ['1', '1', '0']

    So, the gamma rate is the binary number `10110`, or **`22`** in decimal.

        >>> gamma_rate(report)
        22

    The epsilon rate is calculated in a similar way; rather than use the most common bit, the least
    common bit from each position is used. So, the epsilon rate is `01001`, or **`9`** in decimal.

        >>> epsilon_rate(report)
        9

    Multiplying the gamma rate `22` by the epsilon rate `9` produces the power consumption `198`.

    Use the binary numbers in your diagnostic report to calculate the gamma rate and epsilon rate,
    then multiply them together. **What is the power consumption of the submarine?**

        >>> part_1(report)
        part 1: power consumption is 22 * 9 = 198
        198
    """

    gamma = gamma_rate(values)
    epsilon = epsilon_rate(values)

    # epsilon could be also calculated like this, because they are complementary, but whatever:
    # epsilon = (1 << length) - 1 - gamma

    result = gamma * epsilon

    print(f"part 1: power consumption is {gamma} * {epsilon} = {result}")
    return result


def part_2(values: list[str]) -> int:
    """
    Next, you should verify the **life support rating**, which can be determined by multiplying
    the **oxygen generator rating** by the **CO2 scrubber rating**.

    Both the oxygen generator rating and the CO2 scrubber rating are values that can be found in
    your diagnostic report - finding them is the tricky part. Both values are located using
    a similar process that involves filtering out values until only one remains. Before searching
    for either rating value, start with the full list of binary numbers from your diagnostic report
    and **consider just the first bit** of those numbers. Then:

      - Keep only numbers selected by the **bit criteria** for the type of rating value for which
        you are searching. Discard numbers which do not match the bit criteria.
      - If you only have one number left, stop; this is the rating value for which you are
        searching.
      - Otherwise, repeat the process, considering the next bit to the right.

    The bit criteria depends on which type of rating value you want to find:

      - To find **oxygen generator rating**, determine the most common value (`0` or `1`) in
        the current bit position, and keep only numbers with that bit in that position.
        If `0` and `1` are equally common, keep values with a **`1`** in the position being
        considered.
      - To find **CO2 scrubber rating**, determine the least common value (`0` or `1`) in
        the current bit position, and keep only numbers with that bit in that position.
        If `0` and `1` are equally common, keep values with a **`0`** in the position being
        considered.

    For example, to determine the oxygen generator rating value using the same example diagnostic
    report from above:

        >>> report='00100 11110 10110 10111 10101 01111 00111 11100 10000 11001 00010 01010'.split()
        >>> len(report)
        12

    [...] Oxygen generator rating is `10111`, or **`23`** in decimal:

        >>> o2_generator_rating(report)
        23


    [...] The CO2 scrubber rating is `01010`, or **`10`** in decimal:

        >>> co2_scrubber_rating(report)
        10

    Finally, to find the life support rating, multiply the oxygen generator rating `23` by
    the CO2 scrubber rating `10` to get **`230`**.

    Use the binary numbers in your diagnostic report to calculate the oxygen generator rating and
    CO2 scrubber rating, then multiply them together. **What is the life support rating of
    the submarine?**

        >>> part_2(report)
        part 2: life support rating is 23 * 10 = 230
        230
    """

    oxygen = o2_generator_rating(values)
    co2 = co2_scrubber_rating(values)
    result = oxygen * co2

    print(f"part 2: life support rating is {oxygen} * {co2} = {result}")
    return result


def gamma_rate(values: list[str]) -> int:
    return _part_1_rating(values, most_common_bit)


def epsilon_rate(values: list[str]) -> int:
    return _part_1_rating(values, least_common_bit)


def o2_generator_rating(values: list[str]) -> int:
    return _part_2_rating(values, lambda vs, pos: most_common_bit(vs, pos, if_equal='1'))


def co2_scrubber_rating(values: list[str]) -> int:
    return _part_2_rating(values, lambda vs, pos: least_common_bit(vs, pos, if_equal='0'))


Criterium = Callable[[list[str], int], str]


def _part_1_rating(values: list[str], crit: Criterium) -> int:
    length = len(values[0])
    binary = ''.join(crit(values, pos) for pos in range(length))
    return int(binary, 2)


def _part_2_rating(values: list[str], crit: Criterium) -> int:
    length = len(values[0])
    for pos in range(length):
        bit = crit(values, pos)
        values = [val for val in values if val[pos] == bit]
        assert values
        if len(values) == 1:
            return int(values[0], 2)
    else:
        raise ValueError(f'too many values left ({len(values)})')


def most_common_bit(values: Iterable[str], position: int, if_equal: str | None = None) -> str:
    return _select_bit(most_common=True, values=values, position=position, if_equal=if_equal)


def least_common_bit(values: Iterable[str], position: int, if_equal: str | None = None) -> str:
    return _select_bit(most_common=False, values=values, position=position, if_equal=if_equal)


def _select_bit(
    most_common: bool,
    values: Iterable[str],
    position: int,
    if_equal: str | None = None
) -> str:
    c = Counter(value[position] for value in values)
    zeroes_count, ones_count = c['0'], c['1']

    if zeroes_count > ones_count:
        return '0' if most_common else '1'
    elif ones_count > zeroes_count:
        return '1' if most_common else '0'
    elif if_equal is not None:
        return if_equal
    else:
        raise ValueError(f'equal num of bits at pos={position}: {zeroes_count} vs {ones_count}')


def values_from_file(fn: str) -> list[str]:
    with open(relative_path(__file__, fn)) as file_in:
        values = [line.strip() for line in file_in]

    # make sure there are any values
    assert values
    # make sure all values have the same length
    assert len(set(len(val) for val in values)) == 1

    return values


if __name__ == '__main__':
    values_ = values_from_file('data/03-input.txt')
    part_1(values_)
    part_2(values_)
