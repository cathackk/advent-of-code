"""
Advent of Code 2022
Day 1: Calorie Counting
https://adventofcode.com/2022/day/1
"""

from typing import Iterable

from common.file import relative_path
from common.text import line_groups


def part_1(calories: list[list[int]]):
    """
    The jungle must be too overgrown and difficult to navigate in vehicles or access from the air;
    the Elves' expedition traditionally goes on foot. As your boats approach land, the Elves begin
    taking inventory of their supplies. One important consideration is food - in particular,
    the number of **Calories** each Elf is carrying (your puzzle input).

    The Elves take turns writing down the number of Calories contained by the various meals, snacks,
    rations, etc. that they've brought with them, one item per line. Each Elf separates their own
    inventory from the previous Elf's inventory (if any) by a blank line.

    For example, suppose the Elves finish writing their items' Calories and end up with
    the following list:

        >>> elves = calories_from_text('''
        ...     1000
        ...     2000
        ...     3000
        ...
        ...     4000
        ...
        ...     5000
        ...     6000
        ...
        ...     7000
        ...     8000
        ...     9000
        ...
        ...     10000
        ... ''')

    This list represents the Calories of the food carried by five Elves:

        >>> len(elves)
        5

      - The first Elf is carrying food with `1000`, `2000`, and `3000` Calories,
        a total of **`6000`** Calories:

        >>> elves[0]
        [1000, 2000, 3000]
        >>> sum(_)
        6000

      - The second Elf is carrying one food item with **`4000`** Calories:

        >>> elves[1]
        [4000]

      - The third Elf is carrying food with `5000` and `6000` Calories,
        a total of **`11000`** Calories:

        >>> elves[2]
        [5000, 6000]
        >>> sum(_)
        11000

      - The fourth Elf is carrying food with `7000`, `8000`, and `9000` Calories,
        a total of **`24000`** Calories:

        >>> elves[3]
        [7000, 8000, 9000]
        >>> sum(_)
        24000

      - The fifth Elf is carrying one food item with **`10000`** Calories.

        >>> elves[4]
        [10000]

    In case the Elves get hungry and need extra snacks, they need to know which Elf to ask:
    they'd like to know how many Calories are being carried by the Elf carrying the **most**
    Calories. In the example above, this is **`24000`** (carried by the fourth Elf).

        >>> max_total(elves)
        24000

    Find the Elf carrying the most Calories. **How many total Calories is that Elf carrying?**

        >>> part_1(elves)
        part 1: the top elf carries 24000 Calories
        24000
    """

    result = max_total(calories)
    print(f"part 1: the top elf carries {result} Calories")

    return result


def part_2(calories: list[list[int]]) -> int:
    """
    By the time you calculate the answer to the Elves' question, they've already realized that
    the Elf carrying the most Calories of food might eventually **run out of snacks**.

    To avoid this unacceptable situation, the Elves would instead like to know the total Calories
    carried by the **top three** Elves carrying the most Calories. That way, even if one of those
    Elves runs out of snacks, they still have two backups.

    In the example above, the top three Elves are the fourth Elf (with `24000` Calories),
    then the third Elf (with `11000` Calories), then the fifth Elf (with `10000` Calories):

        >>> elves = [[1000, 2000, 3000], [4000], [5000, 6000], [7000, 8000, 9000], [10000]]
        >>> max_n_totals(elves, n=3)
        [24000, 11000, 10000]

    The sum of the Calories carried by these three elves is **`45000`**:

        >>> sum(_)
        45000

    Find the top three Elves carrying the most Calories.
    **How many Calories are those Elves carrying in total?**

        >>> part_2(elves)
        part 2: the top three elves carry total of 45000 Calories
        45000
    """

    result = sum(max_n_totals(calories, n=3))

    print(f"part 2: the top three elves carry total of {result} Calories")
    return result


def max_total(calories: list[list[int]]) -> int:
    return max(sum(elf) for elf in calories)


def max_n_totals(calories: list[list[int]], n: int) -> list[int]:
    return sorted((sum(elf) for elf in calories), reverse=True)[:n]


def calories_from_file(fn: str) -> list[list[int]]:
    return list(calories_from_lines(open(relative_path(__file__, fn))))


def calories_from_text(text: str) -> list[list[int]]:
    return list(calories_from_lines(text.strip().splitlines()))


def calories_from_lines(lines: Iterable[str]) -> Iterable[list[int]]:
    return ([int(line.strip()) for line in group] for group in line_groups(lines))


def main(input_fn: str = 'data/01-input.txt') -> tuple[int, int]:
    calories = calories_from_file(input_fn)
    result_1 = part_1(calories)
    result_2 = part_2(calories)
    return result_1, result_2


if __name__ == '__main__':
    main()
