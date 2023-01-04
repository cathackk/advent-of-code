"""
Advent of Code 2017
Day 5: A Maze of Twisty Trampolines, All Alike
https://adventofcode.com/2017/day/5
"""

from itertools import count
from typing import Callable
from typing import Generator
from typing import Iterable

from tqdm import tqdm

from common.iteration import exhaust
from meta.aoc_tools import data_path


def part_1(jumps: list[int]) -> int:
    """
    An urgent interrupt arrives from the CPU: it's trapped in a maze of jump instructions, and it
    would like assistance from any programs with spare cycles to help find the exit.

    The message includes a list of the offsets for each jump. Jumps are relative: `-1` moves to the
    previous instruction, and `2` skips the next one. Start at the first instruction in the list.
    The goal is to follow the jumps until one leads **outside** the list.

    In addition, these instructions are a little strange; after each jump, the offset of that
    instruction increases by `1`. So, if you come across an offset of `3`, you would move three
    instructions forward, but change it to a `4` for the next time it is encountered.

    For example, consider the following list of jump offsets:

        >>> example_jumps = [0, 3, 0, 1, -3]

    Positive jumps ("forward") move right; negative jumps move left. The current instruction is
    marked in parentheses. The following steps would be taken before an exit is found:

        >>> jumping = run(example_jumps, yield_states=True)

      - **Before** we have taken any steps:

        >>> print_jump(next(jumping))
        (0) 3  0  1  -3

      - Jump with offset `0` (that is, don't jump at all). Fortunately, the instruction is then
        incremented to 1:

        >>> print_jump(next(jumping))
        (1) 3  0  1  -3

      - Step forward because of the instruction we just modified. The first instruction is
        incremented again, now to `2`:

        >>> print_jump(next(jumping))
        2 (3) 0  1  -3

      - Jump all the way to the end; leave a `4` behind:

        >>> print_jump(next(jumping))
        2  4  0  1 (-3)

      - Go back to where we just were; increment `-3` to `-2`:

        >>> print_jump(next(jumping))
        2 (4) 0  1  -2

      - Jump `4` steps forward, escaping the maze:

        >>> print_jump(next(jumping))
        2  5  0  1  -2

    In this example, the exit is reached in `5` steps.

    **How many steps** does it take to reach the exit?

        >>> part_1(example_jumps)
        part 1: it takes 5 steps to reach the exit
        5
    """

    steps = exhaust(run(jumps))
    print(f"part 1: it takes {steps} steps to reach the exit")
    return steps


def part_2(jumps: list[int]) -> int:
    """
    Now, the jumps are even stranger: after each jump, if the offset was **three or more**, instead
    **decrease** it by `1`. Otherwise, increase it by `1` as before.

        >>> example_jumps = [0, 3, 0, 1, -3]
        >>> exhaust(run(example_jumps, inc=inc_2))
        10
        >>> from common.iteration import last
        >>> print_jump(last(run(example_jumps, inc=inc_2, yield_states=True)))
        2  3  2  3  -1

    **How many steps** does it now take to reach the exit?

        >>> part_2(example_jumps)
        part 2: it takes 10 steps to reach the exit
        10
    """

    steps = exhaust(run(jumps, inc=inc_2))
    print(f"part 2: it takes {steps} steps to reach the exit")
    return steps


Jump = tuple[int, Iterable[int]]


def run(
    jumps: Iterable[int],
    inc: Callable[[int], int] = lambda x: x + 1,
    yield_states: bool = False
) -> Generator[Jump, None, int]:
    jumps = list(jumps)
    pos_range = range(len(jumps))

    pos = 0
    if yield_states:
        yield pos, list(jumps)

    for tick in tqdm(count(0), desc="jumping", unit=" jumps", unit_scale=True, delay=0.5):
        if pos not in pos_range:
            return tick

        jump = jumps[pos]
        jumps[pos] = inc(jump)
        pos += jump

        if yield_states:
            yield pos, list(jumps)

    # unreachable
    assert False


def inc_2(num: int) -> int:
    return num - 1 if num >= 3 else num + 1


def print_jump(jump: Jump) -> None:
    pos, state = jump

    def val_f(val: int, active: bool) -> str:
        return f"({val})" if active else f" {val} "

    print("".join(val_f(value, index == pos) for index, value in enumerate(state)).strip())


def jumps_from_file(fn: str) -> list[int]:
    return [int(line) for line in open(fn)]


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    jumps = jumps_from_file(input_path)
    result_1 = part_1(jumps)
    result_2 = part_2(jumps)
    return result_1, result_2


if __name__ == '__main__':
    main()
