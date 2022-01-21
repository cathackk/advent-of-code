"""
Advent of Code 2020
Day 15: Rambunctious Recitation
https://adventofcode.com/2020/day/15
"""

from itertools import count
from typing import Iterator

from tqdm import tqdm

from common.file import relative_path


def part_1(numbers: list[int]) -> int:
    """
    In this game, the players take turns saying *numbers*. They begin by taking turns reading from
    a list of *starting numbers* (your puzzle input). Then, each turn consists of considering the
    *most recently spoken number*:

        - If that was the *first* time the number has been spoken, the current player says *`0`*.
        - Otherwise, the number had been spoken before; the current player announces *how many
        turns apart* the number is from when it was previously spoken.

    So, after the starting numbers, each turn results in that player speaking aloud either *0*
    (if the last number is new) or an *age* (if the last number is a repeat).

    For example, suppose these starting numbers:

        >>> game = memory_game_it([0, 3, 6])

        - *Turn 1*: The 1st number spoken is a starting number, `0`.
        - *Turn 2*: The 2nd number spoken is a starting number, `3`.
        - *Turn 3*: The 3rd number spoken is a starting number, `6`.

            >>> next(game), next(game), next(game)
            (0, 3, 6)

        - *Turn 4*: Now, consider the last number spoken, `6`. Since that was the first time the
          number had been spoken, the 4th number spoken is `0`.

            >>> next(game)
            0

        - *Turn 5*: Next, again consider the last number spoken, `0`. Since it *had* been spoken
          before, the next number to speak is the difference between the turn number when it was
          last spoken (the previous turn, `4`) and the turn number of the time it was most recently
          spoken before then (turn `1`). Thus, the 5th number spoken is `4 - 1 = 3`.

            >>> next(game)
            3

        - *Turn 6*: The last number spoken, `3` had also been spoken before, most recently on turns
          `5` and `2`. So, the 6th number spoken is `5 - 2 = 3`.

            >>> next(game)
            3

        - *Turn 7*: Since `3` was just spoken twice in a row, and the last two turns are `1` turn
          apart, the 7th number spoken is `1`.

            >>> next(game)
            1

        - *Turn 8*: Since `1` is new, the 8th number spoken is `0`.

            >>> next(game)
            0

        - *Turn 9*: `0` was last spoken on turns `8` and `4`, so the 9th number spoken is the
          difference between them, `4`.

            >>> next(game)
            4

        - *Turn 10*: `4` is new, so the 10th number spoken is `0`.

            >>> next(game)
            0

    Thei question for you is: what will be the *2020th& number spoken? In the example above, the
    2020th number spoken will be 436.

        >>> part_1([0, 3, 6])
        part 1: the 2020th number spoken will be 436
        436

    Here are a few more examples:

        >>> memory_game([1, 3, 2], turns=2020)
        1
        >>> memory_game([2, 1, 3], turns=2020)
        10
        >>> memory_game([1, 2, 3], turns=2020)
        27
        >>> memory_game([2, 3, 1], turns=2020)
        78
        >>> memory_game([3, 2, 1], turns=2020)
        438
        >>> memory_game([3, 1, 2], turns=2020)
        1836

    Given your starting numbers, *what will be the 2020th number spoken?*
    """

    turns = 2020
    result = memory_game(numbers, turns=turns)

    print(f"part 1: the {turns}th number spoken will be {result}")
    return result


def part_2(numbers: list[int]) -> int:
    """
    Impressed, the Elves issue you a challenge: determine the *30_000_000th* number spoken.

        >>> part_2([0, 3, 6])
        part 2: the 30000000th number spoken will be 175594
        175594

    More examples:

        >>> memory_game([1, 3, 2], turns=30_000_000)  # doctest: +SKIP
        2578
        >>> memory_game([2, 1, 3], turns=30_000_000)  # doctest: +SKIP
        3544142
        >>> memory_game([1, 2, 3], turns=30_000_000)  # doctest: +SKIP
        261214
        >>> memory_game([2, 3, 1], turns=30_000_000)  # doctest: +SKIP
        6895259
        >>> memory_game([3, 2, 1], turns=30_000_000)  # doctest: +SKIP
        18
        >>> memory_game([3, 1, 2], turns=30_000_000)  # doctest: +SKIP
        362

    *Given your starting numbers, what will be the 30_000_000th number spoken?*
    """

    turns = 30_000_000
    result = memory_game(numbers, turns=turns)

    print(f"part 2: the {turns}th number spoken will be {result}")
    return result


def memory_game_it(starting_numbers: list[int]) -> Iterator[int]:
    last_seen_on: dict[int, int] = {}
    age = 0
    for turn in count(0):
        num = starting_numbers[turn] if turn < len(starting_numbers) else age
        yield num
        age = turn - last_seen_on.get(num, turn)
        last_seen_on[num] = turn


def memory_game(numbers: list[int], turns: int) -> int:
    game = memory_game_it(numbers)

    last_number = None
    for _ in tqdm(range(turns), unit=" turns", unit_scale=True, delay=1.0):
        last_number = next(game)

    return last_number


def load_numbers(fn: str) -> list[int]:
    return [
        int(v)
        for line in relative_path(__file__, fn)
        for v in line.split(",")
    ]


if __name__ == '__main__':
    starting_numbers_ = load_numbers('data/15-input.txt')

    part_1(starting_numbers_)
    part_2(starting_numbers_)
