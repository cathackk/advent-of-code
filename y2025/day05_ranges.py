"""
Advent of Code 2025
Day 5: Cafeteria
https://adventofcode.com/2025/day/5
"""

from typing import Iterable, Iterator

from common.file import relative_path
from common.iteration import ilen


def part_1(ranges: list[range], ingredients: list[int]) -> int:
    """
    As the forklifts break through the wall, the Elves are delighted to discover that there was
    a cafeteria on the other side after all.

    You can hear a commotion coming from the kitchen. "At this rate, we won't have any time left to
    put the wreaths up in the dining hall!" Resolute in your quest, you investigate.

    "If only we hadn't switched to the new inventory management system right before Christmas!"
    another Elf exclaims. You ask what's going on.

    The Elves in the kitchen explain the situation: because of their complicated new inventory
    management system, they can't figure out which of their ingredients are **fresh** and which are
    **spoiled**. When you ask how it works, they give you a copy of their database (your puzzle
    input).

    The database operates on **ingredient IDs**. It consists of a list of **fresh ingredient ID
    ranges**, a blank line, and a list of **available ingredient IDs**. For example:

        >>> example_ranges, example_ingredients = input_from_text('''
        ...     3-5
        ...     10-14
        ...     16-20
        ...     12-18
        ...
        ...     1
        ...     5
        ...     8
        ...     11
        ...     17
        ...     32
        ... ''')
        >>> example_ranges
        [range(3, 6), range(10, 15), range(16, 21), range(12, 19)]
        >>> example_ingredients
        [1, 5, 8, 11, 17, 32]

    The fresh ID ranges are **inclusive**: the range `3-5` means that ingredient IDs `3`, `4`, and
    `5` are all fresh. The ranges can also **overlap**; an ingredient ID is fresh if it is in
    **any** range.

    The Elves are trying to determine which of the **available ingredient IDs** are **fresh**.
    In this example, this is done as follows:

        >>> list(fresh_ingredients(example_ranges, example_ingredients))
        [5, 11, 17]

    So, in this example, **`3`** of the available ingredient IDs are fresh.

    Process the database file from the new inventory management system.
    **How many of the available ingredient IDs are fresh?**

        >>> part_1(example_ranges, example_ingredients)
        part 1: there are 3 fresh ingredients
        3
    """

    result = ilen(fresh_ingredients(ranges, ingredients))

    print(f"part 1: there are {result} fresh ingredients")
    return result


def part_2(ranges: list[range]) -> int:
    """
    The Elves start bringing their spoiled inventory to the trash chute at the back of the kitchen.

    So that they can stop bugging you when they get new inventory, the Elves would like to know
    **all** of the IDs that the **fresh ingredient ID ranges** consider to be **fresh**.
    An ingredient ID is still considered fresh if it is in any range.

    Now, the second section of the database (the available ingredient IDs) is irrelevant. Here are
    the fresh ingredient ID ranges from the above example:

        >>> example_ranges, _ = input_from_file('data/05-example.txt')
        >>> example_ranges
        [range(3, 6), range(10, 15), range(16, 21), range(12, 19)]

    The ingredient IDs that these ranges consider to be fresh are:

        >>> list(fresh_ingredients(example_ranges, range(1, 21)))
        [3, 4, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    So, in this example, the fresh ingredient ID ranges consider a total of **`14`*** ingredient IDs
    to be fresh.

        >>> total_fresh_ingredients(example_ranges)
        14

    Process the database file again. **How many ingredient IDs are considered to be fresh according
    to the fresh ingredient ID ranges?**

        >>> part_2(example_ranges)
        part 2: there are 14 fresh ingredients total
        14
    """

    result = total_fresh_ingredients(ranges)

    print(f"part 2: there are {result} fresh ingredients total")
    return result


def fresh_ingredients(ranges: list[range], ingredients: Iterable[int]) -> Iterator[int]:
    return (
        ingr
        for ingr in ingredients
        if any(ingr in range_ for range_ in ranges)
    )


def total_fresh_ingredients(ranges: Iterable[range]) -> int:
    return sum(len(r) for r in simplified_ranges(ranges))


def simplified_ranges(ranges: Iterable[range]) -> list[range]:
    def has_overlap(r_1: range, r_2: range) -> bool:
        return r_2.start in r_1 or r_1.start in r_2

    def merge(r_1: range, r_2: range) -> range:
        return range(min(r_1.start, r_2.start), max(r_1.stop, r_2.stop))

    simplified_rs: list[range] = []
    for range_ in ranges:
        # combine with as many other ranges as possible
        while True:
            range_to_merge = next((xr for xr in simplified_rs if has_overlap(range_, xr)), None)
            if range_to_merge:
                # found one to merge with
                simplified_rs.remove(range_to_merge)
                range_ = merge(range_, range_to_merge)
            else:
                # nothing to merge with -> we are done for this particular range
                simplified_rs.append(range_)
                break

    return simplified_rs


def input_from_file(fn: str) -> tuple[list[range], list[int]]:
    return input_from_lines(open(relative_path(__file__, fn)))


def input_from_text(text: str) -> tuple[list[range], list[int]]:
    return input_from_lines(iter(text.strip().splitlines()))


def input_from_lines(lines: Iterator[str]) -> tuple[list[range], list[int]]:
    return list(ranges_from_lines(lines)), list(ingredients_from_lines(lines))


def ranges_from_lines(lines: Iterator[str]) -> Iterable[range]:
    for line in lines:
        line = line.strip()
        if line:
            minv, maxv = line.split('-')
            yield range(int(minv), int(maxv) + 1)
        else:
            break


def ingredients_from_lines(lines: Iterator[str]) -> Iterable[int]:
    return (int(line.strip()) for line in lines)


def main(input_fn: str = 'data/05-input.txt') -> tuple[int, int]:
    ranges, ingredients = input_from_file(input_fn)
    result_1 = part_1(ranges, ingredients)
    result_2 = part_2(ranges)
    return result_1, result_2


if __name__ == '__main__':
    main()
