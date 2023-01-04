"""
Advent of Code 2017
Day 15: Dueling Generators
https://adventofcode.com/2017/day/15
"""

from typing import Iterable
from typing import Iterator

from tqdm import tqdm

from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(init_a: int, init_b: int, tests_count: int = 40_000_000) -> int:
    r"""
    Here, you encounter a pair of dueling generators. The generators, called **generator A** and
    **generator B**, are trying to agree on a sequence of numbers. However, one of them is
    malfunctioning, and so the sequences don't always match.

    As they do this, a **judge** waits for each of them to generate its next value, compares the
    lowest 16 bits of both values, and keeps track of the number of times those parts of the values
    match.

    The generators both work on the same principle. To create its next value, a generator will take
    the previous value it produced, multiply it by a **factor** (generator A uses `16807`; generator
    B uses `48271`), and then keep the remainder of dividing that resulting product by `2147483647`.
    That final remainder is the value it produces next.

        >>> FACTOR_A, FACTOR_B
        (16807, 48271)

    To calculate each generator's first value, it instead uses a specific starting value as its
    "previous value" (as listed in your puzzle input).

    For example, suppose that for starting values, generator A uses `65`, while generator B uses
    `8921`. Then, the first five pairs of generated values are:

        >>> a0, b0 = 65, 8921
        >>> from itertools import islice
        >>> first_five_values = list(islice(zip(*gen_pair(a0, b0)), 5))
        >>> first_five_values  # doctest: +NORMALIZE_WHITESPACE
        [(1092455, 430625591),
         (1181022009, 1233683848),
         (245556042, 1431495498),
         (1744312007, 137874439),
         (1352636452, 285222916)]

    In binary, these pairs are (with generator A's value first in each pair):

        >>> print_binary(first_five_values)
        00000000000100001010101101100111
        00011001101010101101001100110111
        --------------------------------
        01000110011001001111011100111001
        01001001100010001000010110001000
        --------------------------------
        00001110101000101110001101001010
        01010101010100101110001101001010
        --------------------------------
        01100111111110000001011011000111
        00001000001101111100110000000111
        --------------------------------
        01010000100111111001100000100100
        00010001000000000010100000000100

    Here, you can see that the lowest (here, rightmost) 16 bits of the third value match:
    `1110001101001010`. Because of this one match, after processing these five pairs, the judge
    would have added only 1 to its total.

        >>> count_matches(*gen_pair(a0, b0), tests_count=5)
        1

    To get a significant sample, the judge would like to consider 40 million pairs. (In the example
    above, the judge would eventually find a total of 588 pairs that match in their lowest 16 bits.)

    After 40 million pairs, what is the judge's final count?

        >>> part_1(a0, b0)
        part 1: 588 matches
        588
    """

    matches = count_matches(*gen_pair(init_a, init_b), tests_count=tests_count)
    print(f"part 1: {matches} matches")
    return matches


def part_2(init_a: int, init_b: int, tests_count: int = 5_000_000) -> int:
    """
    In the interest of trying to align a little better, the generators get more picky about the
    numbers they actually give to the judge.

    They still generate values in the same way, but now they only hand a value to the judge when it
    meets their **criteria**:

      - Generator A looks for values that are multiples of **`4`**.
      - Generator B looks for values that are multiples of **`8`**.

        >>> DIV_A, DIV_B
        (4, 8)

    Each generator functions completely **independently**: they both go through values entirely on
    their own, only occasionally handing an acceptable value to the judge, and otherwise working
    through the same sequence of values as before until they find one.

    The judge still waits for each generator to provide it with a value before comparing them (using
    the same comparison method as before). It keeps track of the order it receives values; the first
    values from each generator are compared, then the second values from each generator, then the
    third values, and so on.

    Using the example starting values given above, the generators now produce the following first
    five values each:

        >>> a0, b0 = 65, 8921
        >>> from itertools import islice
        >>> first_five_values = list(islice(zip(*gen_pair(a0, b0, only_divisible=True)), 5))
        >>> first_five_values  # doctest: +NORMALIZE_WHITESPACE
        [(1352636452, 1233683848),
         (1992081072, 862516352),
         (530830436, 1159784568),
         (1980017072, 1616057672),
         (740335192, 412269392)]

    These values have the following corresponding binary values:

        >>> print_binary(first_five_values)
        01010000100111111001100000100100
        01001001100010001000010110001000
        --------------------------------
        01110110101111001011111010110000
        00110011011010001111010010000000
        --------------------------------
        00011111101000111101010001100100
        01000101001000001110100001111000
        --------------------------------
        01110110000001001010100110110000
        01100000010100110001010101001000
        --------------------------------
        00101100001000001001111001011000
        00011000100100101011101101010000

    Unfortunately, even though this change makes more bits similar on average, none of these values'
    lowest 16 bits match. Now, it's not until the 1056th pair that the judge finds the first match:

        >>> first_matching, = islice(zip(*gen_pair(a0, b0, True)), 1055, 1056)
        >>> first_matching
        (1023762912, 896885216)
        >>> print_binary([first_matching])
        00111101000001010110000111100000
        00110101011101010110000111100000

    This change makes the generators much slower, and the judge is getting impatient; it is now only
    willing to consider **5 million pairs**. (Using the values from the example above, after five
    million pairs, the judge would eventually find a total of `309` pairs that match in their lowest
    16 bits.)

    After 5 million pairs, but using this new generator logic, **what is the judge's final count**?

        >>> part_2(a0, b0)
        part 2: 309 matches using divisibility
        309
    """

    matches = count_matches(*gen_pair(init_a, init_b, only_divisible=True), tests_count=tests_count)
    print(f"part 2: {matches} matches using divisibility")
    return matches


Gen = Iterator[int]

FACTOR_A = 16807
FACTOR_B = 48271
DIV_A = 4
DIV_B = 8


def gen_pair(init_a: int, init_b, only_divisible: bool = False) -> tuple[Gen, Gen]:
    return (
        gen(init_a, FACTOR_A, DIV_A if only_divisible else None),
        gen(init_b, FACTOR_B, DIV_B if only_divisible else None)
    )


def gen(init_value: int, factor: int, divisible: int = None) -> Gen:
    value = init_value
    while True:
        value = (value * factor) % 0x7fffffff
        if not divisible or value % divisible == 0:
            yield value


def count_matches(gen_a: Gen, gen_b: Gen, tests_count: int) -> int:
    matches = 0

    for _ in tqdm(range(tests_count), desc="counting matches", unit_scale=True, delay=0.5):
        a, b = next(gen_a), next(gen_b)
        if a & 0xffff == b & 0xffff:
            matches += 1

    return matches


def print_binary(values: Iterable[tuple[int, int]]) -> None:
    separator = "\n--------------------------------\n"
    print(separator.join(f"{a:032b}\n{b:032b}" for a, b in values))


def initial_values_from_file(fn: str) -> tuple[int, int]:
    with open(fn) as file:
        init_a, = parse_line(next(file), "Generator A starts with $\n")
        init_b, = parse_line(next(file), "Generator B starts with $\n")
        return int(init_a), int(init_b)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    init_values = initial_values_from_file(input_path)
    result_1 = part_1(*init_values)
    result_2 = part_2(*init_values)
    return result_1, result_2


if __name__ == '__main__':
    main()
