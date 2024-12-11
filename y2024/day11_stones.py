"""
Advent of Code 2024
Day 11: Plutonian Pebbles
https://adventofcode.com/2024/day/11
"""

from functools import lru_cache
from typing import Iterable

from common.file import relative_path


def part_1(stones: Iterable[int], blink_count: int = 25) -> int:
    """
    The ancient civilization on Pluto (y2019/day20_donut.py) was known for its ability to manipulate
    spacetime, and while The Historians explore their infinite corridors, you've noticed a strange
    set of physics-defying stones.

    At first glance, they seem like normal stones: they're arranged in a perfectly **straight
    line**, and each stone has a **number** engraved on it.

    The strange part is that every time you blink, the stones **change**.

    Sometimes, the number engraved on a stone changes. Other times, a stone might **split in two**,
    causing all the other stones to shift over a bit to make room in their perfectly straight line.

    As you observe them for a while, you find that the stones have a consistent behavior. Every time
    you blink, the stones each **simultaneously** change according to the **first applicable rule**
    in this list:

      - If the stone is engraved with the number `0`, it is replaced by a stone engraved with
        the number `1`.
      - If the stone is engraved with a number that has an **even** number of digits, it is replaced
        by **two stones**. The left half of the digits are engraved on the new left stone, and the
        right half of the digits are engraved on the new right stone. (The new numbers don't keep
        extra leading zeroes: `1000` would become stones `10` and `0`.)
      - If none of the other rules apply, the stone is replaced by a new stone; the old stone's
        number **multiplied by 2024** is engraved on the new stone.

    No matter how the stones change, their **order is preserved**, and they stay on their perfectly
    straight line.

    How will the stones evolve if you keep blinking at them? You take a note of the number engraved
    on each stone in the line (your puzzle input).

    If you have an arrangement of five stones engraved with the numbers `0 1 10 99 999` and you
    blink once, the stones transform as follows:

      - The first stone, `0`, becomes a stone marked `1`.
      - The second stone, `1`, is multiplied by 2024 to become `2024`.
      - The third stone, `10`, is split into a stone marked `1` followed by a stone marked `0`.
      - The fourth stone, `99`, is split into two stones marked `9`.
      - The fifth stone, `999`, is replaced by a stone marked `2021976`.

    So, after blinking once, your five stones would become an arrangement of seven stones engraved
    with the numbers:

        >>> example_0 = stones_from_text('0 1 10 99 999')
        >>> example_0
        [0, 1, 10, 99, 999]
        >>> list(blink(example_0))
        [1, 2024, 1, 0, 9, 9, 2021976]

    Here is a longer example:

        >>> example_1 = stones_from_text('125 17')
        >>> example_1
        [125, 17]
        >>> list(blink(example_1))
        [253000, 1, 7]
        >>> list(blink(_))
        [253, 0, 2024, 14168]
        >>> list(blink(_))
        [512072, 1, 20, 24, 28676032]
        >>> list(blink(_))
        [512, 72, 2024, 2, 0, 2, 4, 2867, 6032]
        >>> list(blink(_))
        [1036288, 7, 2, 20, 24, 4048, 1, 4048, 8096, 28, 67, 60, 32]
        >>> list(blink(_))
        [2097446912, 14168, 4048, 2, 0, 2, 4, 40, 48, 2024, 40, 48, 80, 96, 2, 8, 6, 7, 6, 0, 3, 2]

    In this example, after blinking six times, you would have `22` stones.

        >>> len(_)
        22
        >>> count_stones(example_1, blink_count=6)
        22

    After blinking 25 times, you would have **`55312`** stones!

        >>> count_stones(example_1, blink_count=25)
        55312

    Consider the arrangement of stones in front of you.
    **How many stones will you have after blinking 25 times?**

        >>> part_1(example_1)
        part 1: after blinking 25 times, you will have 55312 stones
        55312
    """

    result = count_stones(stones, blink_count)

    print(f"part 1: after blinking {blink_count} times, you will have {result} stones")
    return result


def part_2(stones: Iterable[int], blink_count: int = 75) -> int:
    """
    The Historians sure are taking a long time. To be fair, the infinite corridors are very large.

    **How many stones would you have after blinking a total of 75 times?**

        >>> example = stones_from_file('data/11-example.txt')
        >>> example
        [125, 17]
        >>> part_2(example)
        part 2: after blinking 75 times, you will have 65601038650482 stones
        65601038650482
    """

    result = count_stones(stones, blink_count)

    print(f"part 2: after blinking {blink_count} times, you will have {result} stones")
    return result


def blink(stones: Iterable[int]) -> Iterable[int]:
    return (new_stone for stone in stones for new_stone in transform_stone(stone))


def transform_stone(stone: int) -> Iterable[int]:
    if stone == 0:
        return (1,)

    stone_str = str(stone)
    if len(stone_str) % 2 == 0:
        k = len(stone_str) // 2
        return int(stone_str[:k]), int(stone_str[k:])

    return (stone * 2024,)


def count_stones(stones: Iterable[int], blink_count: int) -> int:
    return sum(count_stone(stone, blink_count) for stone in stones)


@lru_cache(maxsize=None)
def count_stone(stone: int, blink_count: int) -> int:
    if blink_count == 0:
        return 1

    return sum(
        count_stone(new_stone, blink_count - 1)
        for new_stone in transform_stone(stone)
    )


def stones_from_file(fn: str) -> list[int]:
    return list(stones_from_lines(open(relative_path(__file__, fn))))


def stones_from_text(text: str) -> list[int]:
    return list(stones_from_lines(text.strip().splitlines()))


def stones_from_lines(lines: Iterable[str]) -> Iterable[int]:
    return (int(num) for line in lines for num in line.split())


def main(input_fn: str = 'data/11-input.txt') -> tuple[int, int]:
    stones = stones_from_file(input_fn)
    result_1 = part_1(stones)
    result_2 = part_2(stones)
    return result_1, result_2


if __name__ == '__main__':
    main()
