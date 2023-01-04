"""
Advent of Code 2018
Day 1: Chronal Calibration
https://adventofcode.com/2018/day/1
"""

from itertools import cycle
from typing import Iterable

from common.iteration import first_repeat
from common.utils import some
from meta.aoc_tools import data_path


def part_1(increments: Iterable[int]) -> int:
    """
    "We've detected some temporal anomalies," one of Santa's Elves at the Temporal Anomaly Research
    and Detection Instrument Station tells you. She sounded pretty worried when she called you down
    here. "At 500-year intervals into the past, someone has been changing Santa's history!"

    "The good news is that the changes won't propagate to our time stream for another 25 days, and
    we have a device" - she attaches something to your wrist - "that will let you fix the changes
    with no such propagation delay. It's configured to send you 500 years further into the past
    every few days; that was the best we could do on such short notice."

    "The bad news is that we are detecting roughly **fifty** anomalies throughout time; the device
    will indicate fixed anomalies with *stars*. The other bad news is that we only have one device,
    and you're the best person for the job! Good lu--" She taps a button on the device, and you
    suddenly feel like you're falling. To save Christmas, you need to get all *fifty stars* by
    December 25th.

    Collect stars by solving puzzles. Two puzzles will be made available on each day in the Advent
    calendar; the second puzzle is unlocked when you complete the first. Each puzzle grants
    *one star*. Good luck!

    After feeling like you've been falling for a few minutes, you look at the device's tiny screen.
    "Error: Device must be calibrated before first use. Frequency drift detected. Cannot maintain
    destination lock." Below the message, the device shows a sequence of changes in frequency (your
    puzzle input). A value like `+6` means the current frequency increases by `6`; a value like `-3`
    means the current frequency decreases by `3`.

    For example, if the device displays frequency changes of `+1, -2, +3, +1`, then starting from
    a frequency of zero, the following changes would occur:

      - Current frequency ` 0`, change of `+1`; resulting frequency ` 1`.
      - Current frequency ` 1`, change of `-2`; resulting frequency `-1`.
      - Current frequency `-1`, change of `+3`; resulting frequency ` 2`.
      - Current frequency ` 2`, change of `+1`; resulting frequency ` 3`.

    In this example, the resulting frequency is `3`.

    Here are other example situations:

      - `+1, +1, +1` results in ` 3`
      - `+1, +1, -2` results in ` 0`
      - `-1, -2, -3` results in `-6`

    Starting with a frequency of zero, **what is the resulting frequency** after all of the changes
    in frequency have been applied?

        >>> part_1([+1, -2, +3, +1])
        part 1: resulting frequency is 3
        3
    """
    result = sum(increments)
    print(f"part 1: resulting frequency is {result}")
    return result


def part_2(increments: list[int]) -> int:
    """
    You notice that the device repeats the same frequency change list over and over. To calibrate
    the device, you need to find the first frequency it reaches **twice**.

    For example, using the same list of changes above, the device would loop as follows:

      - Current frequency ` 0`, change of `+1`; resulting frequency ` 1`.
      - Current frequency ` 1`, change of `-2`; resulting frequency `-1`.
      - Current frequency `-1`, change of `+3`; resulting frequency ` 2`.
      - Current frequency ` 2`, change of `+1`; resulting frequency ` 3`.
      - (At this point, the device continues from the start of the list.)
      - Current frequency ` 3`, change of `+1`; resulting frequency ` 4`.
      - Current frequency ` 4`, change of `-2`; resulting frequency ` 2`,
        which has already been seen.

    In this example, the first frequency reached twice is `2`. Note that your device might need to
    repeat its list of frequency changes many times before a duplicate frequency is found, and that
    duplicates might be found while in the middle of processing the list.

    Here are other examples:

        >>> repeated_frequency([+1, -1])
        0
        >>> repeated_frequency([+3, +3, +4, -2, -4])
        10
        >>> repeated_frequency([-6, +3, +8, +5, -6])
        5
        >>> repeated_frequency([+7, +7, -2, -7, -4])
        14

    **What is the first frequency your device reaches twice?**

        >>> part_2([+1, -2, +3, +1])
        part 2: first frequency reached twice is 2
        2
    """

    result = repeated_frequency(increments)
    print(f"part 2: first frequency reached twice is {result}")
    return result


def repeated_frequency(increments: Iterable[int]) -> int:
    return some(first_repeat(cycling_frequencies(increments)))


def cycling_frequencies(increments: Iterable[int]) -> Iterable[int]:
    total = 0
    yield total
    for increment in cycle(increments):
        total += increment
        yield total


def frequencies_from_file(fn: str) -> list[int]:
    return [int(line.strip()) for line in open(fn)]


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    frequencies = frequencies_from_file(input_path)
    result_1 = part_1(frequencies)
    result_2 = part_2(frequencies)
    return result_1, result_2


if __name__ == '__main__':
    main()
