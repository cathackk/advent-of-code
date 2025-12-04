"""
Advent of Code 2025
Day 3: Lobby
https://adventofcode.com/2025/day/3
"""

from typing import Iterable

from tqdm import tqdm

from common.file import relative_path
from common.iteration import maxi


def part_1(batteries: Iterable[str]) -> int:
    """
    You descend a short staircase, enter the surprisingly vast lobby, and are quickly cleared by the
    security checkpoint. When you get to the main elevators, however, you discover that each one has
    a red light above it: they're all **offline**.

    "Sorry about that," an Elf apologizes as she tinkers with a nearby control panel. "Some kind of
    electrical surge seems to have fried them. I'll try to get them online soon."

    You explain your need to get further underground. "Well, you could at least take the escalator
    down to the printing department, not that you'd get much further than that without the elevators
    working. That is, you could if the escalator weren't also offline."

    "But, don't worry! It's not fried; it just needs power. Maybe you can get it running while
    I keep working on the elevators."

    There are batteries nearby that can supply emergency power to the escalator for just such
    an occasion. The batteries are each labeled with their joltage rating, a value from `1` to `9`.
    You make a note of their joltage ratings (your puzzle input). For example:

        >>> example = batteries_from_text('''
        ...     987654321111111
        ...     811111111111119
        ...     234234234234278
        ...     818181911112111
        ... ''')
        >>> len(example)
        4

    The batteries are arranged into **banks**; each line of digits in your input corresponds to
    a single bank of batteries. Within each bank, you need to turn on **exactly two** batteries;
    the joltage that the bank produces is equal to the number formed by the digits on the batteries
    you've turned on. For example, if you have a bank like `12345` and you turn on batteries `2` and
    `4`, the bank would produce `24` jolts. (You cannot rearrange batteries.)

    You'll need to find the largest possible joltage each bank can produce. In the above example:

        >>> example[0], max_joltage(example[0])
        ('987654321111111', 98)
        >>> example[1], max_joltage(example[1])
        ('811111111111119', 89)
        >>> example[2], max_joltage(example[2])
        ('234234234234278', 78)
        >>> example[3], max_joltage(example[3])
        ('818181911112111', 92)

    The total output joltage is the sum of the maximum joltage from each bank, so in this example,
    the total output joltage is:

        >>> sum(max_joltage(bat) for bat in example)
        357

    There are many batteries in front of you. Find the maximum joltage possible from each bank;
    **what is the total output joltage?**

        >>> part_1(example)
        part 1: total output joltage is 357
        357
    """

    result = sum(max_joltage(battery) for battery in batteries)

    print(f"part 1: total output joltage is {result}")
    return result


def part_2(batteries: Iterable[str]) -> int:
    """
    The escalator doesn't move. The Elf explains that it probably needs more joltage to overcome
    the static friction of the system and hits the big red "joltage limit safety override" button.
    You lose count of the number of times she needs to confirm "yes, I'm sure" and decorate the
    lobby a bit while you wait.

    Now, you need to make the largest joltage by turning on **exactly twelve** batteries within each
    bank.

    The joltage output for the bank is still the number formed by the digits of the batteries you've
    turned on; the only difference is that now there will be **12** digits in each bank's joltage
    output instead of two.

    Consider again the example from before:

        >>> example = batteries_from_file('data/03-example.txt')
        >>> len(example)
        4

    Now, the joltages are much larger:

        >>> example[0], max_joltage(example[0], digits=12)
        ('987654321111111', 987654321111)
        >>> example[1], max_joltage(example[1], digits=12)
        ('811111111111119', 811111111119)
        >>> example[2], max_joltage(example[2], digits=12)
        ('234234234234278', 434234234278)
        >>> example[3], max_joltage(example[3], digits=12)
        ('818181911112111', 888911112111)

    The total output joltage is now much larger:

        >>> sum(max_joltage(bat, digits=12) for bat in example)
        3121910778619

    **What is the new total output joltage?**

        >>> part_2(example)
        part 2: new total output joltage is 3121910778619
        3121910778619
    """

    result = sum(
        max_joltage(battery, digits=12)
        for battery in tqdm(batteries, unit=" batteries", delay=1.0)
    )

    print(f"part 2: new total output joltage is {result}")
    return result


def max_joltage(battery: str, digits: int = 2) -> int:
    return int(_max_joltage_str(battery, digits))


def _max_joltage_str(battery: str, digits: int) -> str:
    if digits == 0:
        return ''

    max_digit, index = maxi(battery[:len(battery) - digits + 1])
    return max_digit + _max_joltage_str(battery[index+1:], digits=digits - 1)


def batteries_from_file(fn: str) -> list[str]:
    return list(batteries_from_lines(open(relative_path(__file__, fn))))


def batteries_from_text(text: str) -> list[str]:
    return list(batteries_from_lines(text.strip().splitlines()))


def batteries_from_lines(lines: Iterable[str]) -> Iterable[str]:
    return (line.strip() for line in lines)


def main(input_fn: str = 'data/03-input.txt') -> tuple[int, int]:
    batteries = batteries_from_file(input_fn)
    result_1 = part_1(batteries)
    result_2 = part_2(batteries)
    return result_1, result_2


if __name__ == '__main__':
    main()
