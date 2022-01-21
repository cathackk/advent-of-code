"""
Advent of Code 2017
Day 6: Memory Reallocation
https://adventofcode.com/2017/day/6
"""

from typing import Iterable
from typing import Iterator

from common.file import relative_path


def part_1(initial_state: Iterable[int]) -> int:
    """
    A debugger program here is having an issue: it is trying to repair a memory reallocation
    routine, but it keeps getting stuck in an infinite loop.

    In this area, there are sixteen memory banks; each memory bank can hold any number of
    **blocks**. The goal of the reallocation routine is to balance the blocks between the memory
    banks.

    The reallocation routine operates in cycles. In each cycle, it finds the memory bank with the
    most blocks (ties won by the lowest-numbered memory bank) and redistributes those blocks among
    the banks. To do this, it removes all of the blocks from the selected bank, then moves to the
    next (by index) memory bank and inserts one of the blocks. It continues doing this until it runs
    out of blocks; if it reaches the last memory bank, it wraps around to the first one.

    The debugger would like to know how many redistributions can be done before a blocks-in-banks
    configuration is produced that **has been seen before**.

    For example, imagine a scenario with only four memory banks `0`, `2`, `7`, and `0`:

        >>> gen = realloc([0, 2, 7, 0])
        >>> next(gen)
        (0, 2, 7, 0)

      - The third bank has the most blocks, so it is chosen for redistribution. Starting with the
        next bank (the fourth bank) and then continuing to the first bank, the second bank, and so
        on, the `7` blocks are spread out over the memory banks. The fourth, first, and second banks
        get two blocks each, and the third bank gets one back. The final result looks like this:

        >>> next(gen)
        (2, 4, 1, 2)

      - Next, the second bank is chosen because it contains the most blocks (four). Because there
        are four memory banks, each gets one block. The result is:

        >>> next(gen)
        (3, 1, 2, 3)

      - Now, there is a tie between the first and fourth memory banks, both of which have three
        blocks. The first bank wins the tie, and its three blocks are distributed evenly over
        the other three banks, leaving it with none:

        >>> next(gen)
        (0, 2, 3, 4)

      - The fourth bank is chosen, and its four blocks are distributed such that each of the four
        banks receives one:

        >>> next(gen)
        (1, 3, 4, 1)

      - The third bank is chosen, and the same thing happens:

        >>> next(gen)
        (2, 4, 1, 2)

    At this point, we've reached a state we've seen before: `(2, 4, 1, 2)` was already seen.
    The infinite loop is detected after the fifth block redistribution cycle, and so the answer in
    this example is `5`.

    Given the initial block counts in your puzzle input, **how many redistribution cycles** must be
    completed before a configuration is produced that has been seen before?

        >>> part_1([0, 2, 7, 0])
        part 1: 5 cycles until repeat
        5
    """

    length, _ = wait_for_repeat(realloc(initial_state))
    print(f"part 1: {length} cycles until repeat")
    return length


def part_2(initial_state: Iterable[int]) -> int:
    """
    Out of curiosity, the debugger would also like to know the size of the loop: starting from
    a state that has already been seen, how many block redistribution cycles must be performed
    before that same state is seen again?

    In the example above, `(2, 4, 1, 2)` is seen again after four cycles, and so the answer in that
    example would be `4`.

    **How many cycles** are in the infinite loop that arises from the configuration in your puzzle
    input?

        >>> part_2([0, 2, 7, 0])
        part 2: 4 steps to repeat once again
        4
    """

    length, first_seen = wait_for_repeat(realloc(initial_state))
    result = length - first_seen
    print(f"part 2: {result} steps to repeat once again")
    return result


def realloc(nums: Iterable[int]) -> Iterator[tuple[int, ...]]:
    nums = list(nums)
    assert len(nums) > 0

    yield tuple(nums)

    while True:

        max_index = max(range(len(nums)), key=lambda n: nums[n])
        count = nums[max_index]
        nums[max_index] = 0

        head = max_index
        while count > 0:
            head = (head + 1) % len(nums)
            nums[head] += 1
            count -= 1

        yield tuple(nums)


def wait_for_repeat(states: Iterable) -> tuple[int, int]:
    seen_states = dict()

    for state in states:
        if state not in seen_states:
            seen_states[state] = len(seen_states)
        else:
            return len(seen_states), seen_states[state]

    raise ValueError("nothing was repeated")


def blocks_from_file(fn: str) -> list[int]:
    return blocks_from_line(open(relative_path(__file__, fn)).readline())


def blocks_from_line(line: str) -> list[int]:
    return [int(val) for val in line.strip().split()]


if __name__ == '__main__':
    initial_state_ = blocks_from_file('data/06-input.txt')
    part_1(initial_state_)
    part_2(initial_state_)
