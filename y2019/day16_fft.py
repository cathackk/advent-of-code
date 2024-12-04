"""
Advent of Code 2019
Day 16: Flawed Frequency Transmission
https://adventofcode.com/2019/day/16
"""

from itertools import chain, cycle, repeat
from typing import Iterable, Iterator

from tqdm import tqdm

from meta.aoc_tools import data_path


def part_1(number: str) -> int:
    """
    You're 3/4ths of the way through the gas giants. Not only do roundtrip signals to Earth take
    five hours, but the signal quality is quite bad as well. You can clean up the signal with the
    Flawed Frequency Transmission algorithm, or **FFT**.

    As input, FFT takes a list of numbers. In the signal you received (your puzzle input), each
    number is a single digit: data like `15243` represents the sequence `1`, `5`, `2`, `4`, `3`.

    FFT operates in repeated **phases**. In each phase, a new list is constructed with the same
    length as the input list. This new list is also used as the input for the next phase.

    Each element in the new list is built by multiplying every value in the input list by a value in
    a repeating **pattern** and then adding up the results. So, if the input list were
    `9, 8, 7, 6, 5` and the pattern for a given element were `1, 2, 3`, the result would be
    `9*1 + 8*2 + 7*3 + 6*1 + 5*2` (with each input element on the left and each value in the
    repeating pattern on the right of each multiplication). Then, only the ones digit is kept:
    `38` becomes `8`, `-17` becomes `7`, and so on.

        >>> apply_pattern(digits=[9, 8, 7, 6, 5], pattern=[1, 2, 3])
        2

    While each element in the output array uses all of the same input array elements, the actual
    repeating pattern to use depends on **which output element** is being calculated. The base
    pattern is `0, 1, 0, -1`. Then, repeat each value in the pattern a number of times equal to
    the **position in the output list** being considered. Repeat once for the first element, twice
    for the second element, three times for the third element, and so on. So, if the third element
    of the output list is being calculated, repeating the values would produce:

        >>> from itertools import islice
        >>> list(islice(generate_pattern(3, skip_first=False), 24))  # doctest: +ELLIPSIS
        [0, 0, 0, 1, 1, 1, 0, 0, 0, -1, -1, -1, 0, 0, 0, 1, 1, 1, 0, ...]

    When applying the pattern, skip the very first value exactly once. (In other words, offset the
    whole pattern left by one.) So, for the second element of the output list, the actual pattern
    used would be:

        >>> list(islice(generate_pattern(2), 24))  # doctest: +ELLIPSIS
        [0, 1, 1, 0, 0, -1, -1, 0, 0, 1, 1, 0, 0, -1, -1, ...]

    After using this process to calculate each element of the output list, the phase is complete,
    and the output list of this phase is used as the new input list for the next phase, if any.

    Given the input signal `12345678`, below are four phases of FFT:

        >>> fft('12345678', phases=4)
        '01029498'

    Here are the first 8 digits of the final output list after 100 phases for some larger inputs:

        >>> fft('80871224585914546619083218645595')
        '24176176'
        >>> fft('19617804207202209144916044189917')
        '73745418'
        >>> fft('69317163492948606335995924319873')
        '52432133'

    After **100** phases of FFT, **what are the first eight digits in the final output list?**

        >>> part_1('69317163492948606335995924319873')
        part 1: after 100 phases of FFT, the first 8 digits are: 52432133
        52432133
    """

    result = int(fft(number))

    print(f"part 1: after 100 phases of FFT, the first 8 digits are: {result}")
    return result


def part_2(number: str) -> int:
    """
    Now that your FFT is working, you can decode the **real signal**.

    The real signal is your puzzle input **repeated 10_000 times**. Treat this new signal as
    a single input list. Patterns are still calculated as before, and 100 phases of FFT are still
    applied.

    The **first seven digits** of your initial input signal also represent the **message offset**.
    The message offset is the location of the eight-digit message in the final output list.
    Specifically, the message offset indicates the **number of digits to skip** before reading the
    eight-digit message. For example, if the first seven digits of your initial input signal were
    `1234567`, the eight-digit message would be the eight digits after skipping 1_234_567 digits of
    the final output list. Or, if the message offset were 7 and your final output list were
    `98765432109876543210`, the eight-digit message would be `21098765`. (Of course, your real
    message offset will be a seven-digit number, not a one-digit number like `7`.)

    Here is the eight-digit message in the final output list after 100 phases. The message offset
    given in each input has been highlighted. (Note that the inputs given below are repeated 10_000
    times to find the actual starting input lists.)

        >>> fft_offset('03036732577212944063491565474664')
        '84462026'
        >>> fft_offset('02935109699940807407585447034323')
        '78725270'
        >>> fft_offset('03081770884921959731165446850517')
        '53553731'

    After repeating your input signal 10_000 times and running 100 phases of FFT, **what is the
    eight-digit message embedded in the final output list?**

        >>> part_2('03081770884921959731165446850517')  # doctest: +NORMALIZE_WHITESPACE
        part 2: after 100 phases of FFT on the extended number,
                the message at the given offset is: 53553731
        53553731
    """

    result = int(fft_offset(number))

    print(
        f"part 2: after 100 phases of FFT on the extended number, "
        f"the message at the given offset is: {result}"
    )
    return result


def apply_pattern(digits: Iterable[int], pattern: Iterable[int]) -> int:
    return abs(sum(a * b for a, b in zip(digits, cycle(pattern)))) % 10


def generate_pattern(repeats: int, skip_first: bool = True) -> Iterator[int]:
    gen = cycle(
        chain(
            repeat(0, repeats),
            repeat(+1, repeats),
            repeat(0, repeats),
            repeat(-1, repeats),
        )
    )

    if skip_first:
        next(gen)

    yield from gen


def fft(number: str, phases: int = 100, message_length: int = 8) -> str:
    digits = [int(d) for d in number]

    for _ in tqdm(range(phases), delay=1.0, desc="applying FFT", unit=" phases"):
        digits = [apply_pattern(digits, generate_pattern(ix + 1)) for ix in range(len(digits))]

    return ''.join(str(d) for d in digits[:message_length])


def fft_offset(
    number: str,
    phases: int = 100,
    number_repeats: int = 10_000,
    message_length: int = 8,
) -> str:
    offset = int(number[:7])
    assert offset > len(number) // 2
    digits = [int(d) for _ in range(number_repeats) for d in number][offset:]

    def fft_phase(digs: list[int]) -> Iterable[int]:
        digs_sum = sum(digs)
        for index, digit in enumerate(digs):
            yield abs(digs_sum) % 10
            digs_sum -= digit

    for _ in tqdm(range(phases), delay=1.0, desc="applying optimized FFT", unit=" phases"):
        digits = list(fft_phase(digits))

    return ''.join(str(d) for d in digits[:message_length])


def number_from_file(fn: str) -> str:
    return open(fn).readline().strip()


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    number = number_from_file(input_path)
    result_1 = part_1(number)
    result_2 = part_2(number)
    return result_1, result_2


if __name__ == '__main__':
    main()
