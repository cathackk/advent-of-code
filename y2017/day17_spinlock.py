"""
Advent of Code 2017
Day 17: Spinlock
https://adventofcode.com/2017/day/17
"""

from typing import Iterator

from tqdm import tqdm

from common.iteration import last
from common.utils import some
from meta.aoc_tools import data_path


def part_1(step_size: int, count: int = 2017) -> int:
    """
    Suddenly, whirling in the distance, you notice what looks like a massive, pixelated hurricane:
    a deadly [spinlock](https://en.wikipedia.org/wiki/Spinlock). This spinlock isn't just consuming
    computing power, but memory, too; vast, digital mountains are being ripped from the ground and
    consumed by the vortex.

    If you don't move quickly, fixing that printer will be the least of your problems.

    This spinlock's algorithm is simple but efficient, quickly consuming everything in its path. It
    starts with a circular buffer containing only the value `0`, which it marks as the **current
    position**. It then steps forward through the circular buffer some number of steps (your puzzle
    input) before inserting the first new value, `1`, after the value it stopped on. The inserted
    value becomes the **current position**. Then, it steps forward from there the same number of
    steps, and wherever it stops, inserts after it the second new value, `2`, and uses that as
    the new **current position** again.

    It repeats this process of **stepping forward**, **inserting a new value**, and **using the
    location of the inserted value as the new current position** a total of **`2017`** times,
    inserting `2017` as its final operation, and ending with a total of `2018` values (including
    `0`) in the circular buffer.

    For example, if the spinlock were to step `3` times per insert, the circular buffer would begin
    to evolve like this (using parentheses to mark the current position after each iteration of the
    algorithm):

        >>> spinning = spinlock(step_size=3, rounds=2017)

      - The initial state before any insertions:

        >>> print_spin(next(spinning))
        (0)

      - The spinlock steps forward three times (`0`, `0`, `0`), and then inserts the first value,
        `1`, after it. `1` becomes the current position:

        >>> print_spin(next(spinning))
        0 (1)

      - The spinlock steps forward three times (`0`, `1`, `0`), and then inserts the second value,
        `2`, after it. `2` becomes the current position:

        >>> print_spin(next(spinning))
        0 (2) 1

      - The spinlock steps forward three times (`1`, `0`, `2`), and then inserts the third value,
        `3`, after it. `3` becomes the current position:

        >>> print_spin(next(spinning))
        0  2 (3) 1

    And so on:

        >>> for _ in range(6):
        ...     print_spin(next(spinning))
        0  2 (4) 3  1
        0 (5) 2  4  3  1
        0  5  2  4  3 (6) 1
        0  5 (7) 2  4  3  6  1
        0  5  7  2  4  3 (8) 6  1
        0 (9) 5  7  2  4  3  8  6  1

    Eventually, after 2017 insertions, the section of the circular buffer near the last insertion
    looks like this:

        >>> print_spin(last(spinning), context=3)
        1512  1134  151 (2017) 638  1513  851

    Perhaps, if you can identify the value that will ultimately be after the last value written
    (`2017`), you can short-circuit the spinlock. In this example, that would be `638`.

    **What is the value after `2017`** in your completed circular buffer?

        >>> part_1(step_size=3)
        part 1: value after 2017 is 638
        638
    """

    current_pos, numbers = last(spinlock(step_size, count))
    assert numbers[current_pos] == count
    result = numbers[current_pos + 1]
    print(f"part 1: value after 2017 is {result}")
    return result


def part_2(step_size: int, rounds: int = 50_000_000):
    """
    The spinlock does not short-circuit. Instead, it gets **more** angry. At least, you assume
    that's what happened; it's spinning significantly faster than it was a moment ago.

    You have good news and bad news.

    The good news is that you have improved calculations for how to stop the spinlock. They indicate
    that you actually need to identify the value after **`0`** in the current state of the circular
    buffer.

    The bad news is that while you were determining this, the spinlock has just finished inserting
    its fifty millionth value (`50_000_000`).

    **What is the value after `0`** the moment `50_000_000` is inserted?

        >>> part_2(step_size=3)
        part 2: value after 0 is 1222153
        1222153
    """

    result = spinlock_optimized(step_size=step_size, rounds=rounds)
    print(f"part 2: value after 0 is {result}")
    return result


SpinState = tuple[int, list[int]]


def spinlock(step_size: int, rounds: int) -> Iterator[SpinState]:
    buffer = [0]
    head = 0

    yield head, buffer

    for next_value in range(1, rounds + 1):
        head = (head + step_size) % len(buffer)
        buffer.insert(head + 1, next_value)
        head = head + 1
        yield head, buffer


def spinlock_optimized(step_size: int, rounds: int) -> int:
    head = 0
    last_value_at_1: int | None = None

    # we can do this without the buffer!
    for next_value in tqdm(range(1, rounds + 1), desc="inserting", unit_scale=True, delay=0.5):
        head = ((head + step_size) % next_value) + 1
        if head == 1:
            last_value_at_1 = next_value

    return some(last_value_at_1)


def print_spin(spin: SpinState, context: int = None) -> None:
    head, buffer = spin
    if context:
        assert head in range(context, len(buffer) - context)
        buffer = buffer[head - context:head + context + 1]
        head = context

    print("".join(
        f"({val})" if index == head else f" {val} "
        for index, val in enumerate(buffer)
    ).strip())


def step_size_from_file(fn: str) -> int:
    return int(open(fn).readline().strip())


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    step_size = step_size_from_file(input_path)
    result_1 = part_1(step_size)
    result_2 = part_2(step_size)
    return result_1, result_2


if __name__ == '__main__':
    main()
