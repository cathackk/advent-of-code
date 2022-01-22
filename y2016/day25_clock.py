"""
Advent of Code 2016
Day 25: Clock Signal
https://adventofcode.com/2016/day/25
"""

from itertools import count
from typing import Iterator

from tqdm import tqdm

from y2016 import assembunny


def part_1(tape: assembunny.Tape):
    """
    You open the door and find yourself on the roof. The city sprawls away from you for miles and
    miles.

    There's not much time now - it's already Christmas, but you're nowhere near the North Pole, much
    too far to deliver these stars to the sleigh in time.

    However, maybe the **huge antenna** up here can offer a solution. After all, the sleigh doesn't
    need the stars, exactly; it needs the timing data they provide, and you happen to have a massive
    signal generator right here.

    You connect the stars you have to your prototype computer, connect that to the antenna, and
    begin the transmission.

    Nothing happens.

    You call the service number printed on the side of the antenna and quickly explain
    the situation. "I'm not sure what kind of equipment you have connected over there," he says,
    "but you need a clock signal." You try to explain that this is a signal for a clock.

    "No, no, a clock signal - timing information so the antenna computer knows how to read the data
    you're sending it. An endless, alternating pattern of `0`, `1`, `0`, `1`, `0`, `1`, `0`, `1`,
    `0`, `1`...." He trails off.

    You ask if the antenna can handle a clock signal at the frequency you would need to use for the
    data from the stars. "There's **no way** it can! The only antenna we've installed capable of
    **that** is on top of a top-secret Easter Bunny installation, and you're **definitely** not-"
    You hang up the phone.

    You've extracted the antenna's clock signal generation assembunny code (your puzzle input);
    it looks mostly compatible with code you worked on just recently.

    This antenna code, being a signal generator, uses one extra instruction:

      - `out x` **transmits** `x` (either an integer or the **value** of a register) as the next
        value for the clock signal.

        >>> example = assembunny.Tape.from_text(
        ...     'dec a; dec a; cpy 1 b; out 0; out 1; out a; out b; jnz 1 -4'
        ... )
        >>> from itertools import islice
        >>> list(islice(assembunny.run_out(example), 20))  # doctest: +ELLIPSIS
        [0, 1, -2, 1, 0, 1, -2, 1, 0, ...]

    The code takes a value (via register `a`) that describes the signal to generate, but you're not
    sure how it's used. You'll have to find the input to produce the right signal through
    experimentation.

    **What is the lowest positive integer** that can be used to initialize register `a` and cause
    the code to output a clock signal of `0`, `1`, `0`, `1`... repeating forever?

        >>> part_1(example)
        part 1: initialize a=2
        2
    """

    result = find_init_a(assembunny.optimized_tape(tape), 100)
    print(f"part 1: initialize a={result}")
    return result


# pylint: disable=inconsistent-return-statements
def find_init_a(tape: assembunny.Tape, target_signal_length: int = 100) -> int:
    for a in tqdm(count(1), desc="finding init a", unit=" runs", delay=0.5):
        signal = assembunny.run_out(tape, a=a)
        length = clock_length(signal, target_signal_length)
        if length == target_signal_length:
            return a

    # unreachable
    assert False


def clock_length(signal: Iterator[int], test_length: int) -> int:
    expected = 0
    max_tick = 0

    for tick, value in enumerate(signal):
        if value != expected:
            return tick
        if tick >= test_length:
            return test_length

        expected = int(not expected)
        max_tick = tick

    return max_tick


if __name__ == '__main__':
    tape_ = assembunny.Tape.from_file('data/25-input.txt')
    part_1(tape_)
