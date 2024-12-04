"""
Advent of Code 2017
Day 10: Knot Hash
https://adventofcode.com/2017/day/10
"""

import operator
from functools import reduce
from typing import Iterable, Self

from meta.aoc_tools import data_path


def part_1(lengths: Iterable[int], rope_length: int = 256) -> int:
    r"""
    You come across some programs that are trying to implement a software emulation of a hash based
    on knot-tying. The hash these programs are implementing isn't very strong, but you decide to
    help them anyway. You make a mental note to remind the Elves later not to invent their own
    cryptographic functions.

    This hash function simulates tying a knot in a circle of string with 256 marks on it. Based on
    the input to be hashed, the function repeatedly selects a span of string, brings the ends
    together, and gives the span a half-twist to reverse the order of the marks within it. After
    doing this many times, the order of the marks is used to build the resulting hash.

          4--5   pinch   4  5           4   1
         /    \  5,0,1  / \/ \  twist  / \ / \
        3      0  -->  3      0  -->  3   X   0
         \    /         \ /\ /         \ / \ /
          2--1           2  1           2   5

    To achieve this, begin with a **list** of numbers from `0` to `255`, a **current position**
    which begins at `0` (the first element in the list), a **skip size** (which starts at `0`), and
    a sequence of **lengths** (your puzzle input). Then, for each length:

      - **Reverse** the order of that **length** of elements in the **list**, starting with the
        element at the current position.
      - **Move** the **current position** forward by that **length** plus the **skip size**.
      - **Increase** the **skip size** by one.

    The **list** is circular; if the **current position** and the **length** try to reverse elements
    beyond the end of the list, the operation reverses using as many extra elements as it needs from
    the front of the list. If the **current position** moves past the end of the list, it wraps
    around to the front. **Lengths** larger than the size of the list are invalid.

    Here's an example using a smaller list:

    Suppose we instead only had a circular list containing five elements, `0, 1, 2, 3, 4`, and were
    given input lengths of `3, 4, 1, 5`:

        >>> k = Knot.of_length(5)

      - The list begins as:

        >>> k
        Knot(pos=0, rope=[0, 1, 2, 3, 4], skip_size=0)

      - The first length, `3`, selects `([0] 1 2) 3 4`. After reversing that section, we get
        `([2] 1 0) 3 4`. Then, the **current position** moves forward by the **length**, `3`, plus
        the **skip size**, `0`: `2 1 0 [3] 4`. Finally, the **skip size** increases to `1`:

        >>> (k := k.pinched(3))
        Knot(pos=3, rope=[2, 1, 0, 3, 4], skip_size=1)

      - The second length, `4`, selects a section which wraps: `2 1) 0 ([3] 4`. The sublist
        `3 4 2 1` is reversed to form `1 2 4 3`: `4 3) 0 ([1] 2`. The **current position** moves
        forward by the **length** plus the **skip size**, a total of `5`, causing it not to move
        because it wraps around: `4 3 0 [1] 2`. The **skip size** increases to `2`:

        >>> (k := k.pinched(4))
        Knot(pos=3, rope=[4, 3, 0, 1, 2], skip_size=2)

      - The third length, `1`, selects a sublist of a single element, and so reversing it has no
       effect. The **current position** moves forward by the **length** (`1`) plus the skip size
       (`2`): `4 [3] 0 1 2`. The **skip size** increases to `3`:

        >>> (k := k.pinched(1))
        Knot(pos=1, rope=[4, 3, 0, 1, 2], skip_size=3)

      - The fourth length, `5`, selects every element starting with the second: `4) ([3] 0 1 2`.
        Reversing this sublist produces: `3) ([4] 2 1 0`. Finally, the **current position** moves
        forward by `8`: `3 4 2 1 [0]`. The **skip size** increases to `4`.

        >>> (k := k.pinched(5))
        Knot(pos=4, rope=[3, 4, 2, 1, 0], skip_size=4)

    In this example, the first two numbers in the list end up being `3` and `4`; to check the
    process, you can multiply them together to produce `12`.

    However, you should instead use the standard list size of `256` (with values `0` to `255`) and
    the sequence of **lengths** in your puzzle input. Once this process is complete, **what is the
    result of multiplying the first two numbers in the list**?

        >>> part_1(lengths=[3, 4, 1, 5], rope_length=5)
        part 1: first two numbers on the rope are 3 * 4 = 12
        12
    """

    knot = Knot.of_length(rope_length).pinched(*lengths)
    num_1, num_2 = knot.rope[:2]
    result = num_1 * num_2
    print(f"part 1: first two numbers on the rope are {num_1} * {num_2} = {result}")
    return result


def part_2(input_bytes: bytes) -> str:
    """
    The logic you've constructed forms a single **round** of the **Knot Hash** algorithm; running
    the full thing requires many of these rounds. Some input and output processing is also required.

    First, from now on, your input should be taken not as a list of numbers, but as a string of
    bytes instead. Unless otherwise specified, convert characters to bytes using their ASCII codes.
    This will allow you to handle arbitrary ASCII strings, and it also ensures that your input
    lengths are never larger than `255`. For example, if you are given `1,2,3`, you should convert
    it to the ASCII codes for each character:

        >>> list('1,2,3'.encode())
        [49, 44, 50, 44, 51]

    Once you have determined the sequence of lengths to use, add the following lengths to the end of
    the sequence: `17, 31, 73, 47, 23`. For example, if you are given `1,2,3`, your final sequence
    of lengths should be `49,44,50,44,51,17,31,73,47,23` (the ASCII codes from the input string
    combined with the standard length suffix values).

    Second, instead of merely running one **round** like you did above, run a total of `64` rounds,
    using the same **length** sequence in each round. The **current position** and **skip size**
    should be preserved between rounds. For example, if the previous example was your first round,
    you would start your second round with the same length sequence (`3,4,1,5,17,31,73,47,23`, now
    assuming they came from ASCII codes and include the suffix), but start with the previous round's
    **current position** (`4`) and **skip size** (`4`).

    Once the rounds are complete, you will be left with the numbers from `0` to `255` in some order,
    called the **sparse hash**. Your next task is to reduce these to a list of only `16` numbers
    called the **dense hash**. To do this, use numeric bitwise XOR to combine each consecutive block
    of `16` numbers in the sparse hash (there are `16` such blocks in a list of `256` numbers). So,
    the first element in the dense hash is the first sixteen elements of the sparse hash XOR'd
    together, the second element in the dense hash is the second sixteen elements of the sparse hash
    XOR'd together, etc.

    For example, if the first sixteen elements of your sparse hash are as shown below, you would
    calculate the first output number like this:

        >>> xor([65, 27, 9, 1, 4, 3, 40, 50, 91, 7, 6, 0, 2, 5, 68, 22])
        64

    Perform this operation on each of the sixteen blocks of sixteen numbers in your sparse hash to
    determine the sixteen numbers in your dense hash.

    Finally, the standard way to represent a Knot Hash is as a single hexadecimal string; the final
    output is the dense hash in hexadecimal notation. Because each number in your dense hash will be
    between `0` and `255` (inclusive), always represent each number as two hexadecimal digits
    (including a leading zero as necessary). So, if your first three numbers are `64`, `7`, `255`,
    they correspond to the hexadecimal numbers `40`, `07`, `ff`, and so the first six characters of
    the hash would be `4007ff`.

        >>> bytes([64, 7, 255]).hex()
        '4007ff'

    Because every Knot Hash is sixteen such numbers, the hexadecimal representation is always 32
    hexadecimal digits (`0`-`f`) long.

    Here are some example hashes:

        >>> knot_hash(b'').hex()
        'a2582a3a0e66e6e86e3812dcb672a272'
        >>> knot_hash(b'AoC 2017').hex()
        '33efeb34ea91902bb2f59c9920caa6cd'
        >>> knot_hash(b'1,2,3').hex()
        '3efbe78a8d82f29979031a4aa0b16a9d'
        >>> knot_hash(b'1,2,4').hex()
        '63960835bcdc130f0b66d7ff4f6a5a8e'

    Treating your puzzle input as a string of ASCII characters, **what is the Knot Hash of your
    puzzle input?** Ignore any leading or trailing whitespace you might encounter.

        >>> part_2(b'1,2,3')
        part 2: knot hash is '3efbe78a8d82f29979031a4aa0b16a9d'
        '3efbe78a8d82f29979031a4aa0b16a9d'
    """

    hashed = knot_hash(input_bytes).hex()
    print(f"part 2: knot hash is {hashed!r}")
    return hashed


class Knot:

    __slots__ = ('pos', 'rope', 'skip_size')

    def __init__(self, pos: int = 0, rope: Iterable[int] = range(256), skip_size: int = 0):
        self.pos = pos
        self.rope = list(rope)
        self.skip_size = skip_size

    def __repr__(self) -> str:
        tn = type(self).__name__
        return f'{tn}(pos={self.pos!r}, rope={self.rope!r}, skip_size={self.skip_size!r})'

    @classmethod
    def of_length(cls, rope_length: int) -> Self:
        return cls(0, range(rope_length), 0)

    def pinched(self, *lengths: int, rounds: int = 1) -> Self:
        assert rounds >= 1
        knot = self

        for _ in range(rounds):
            for length in lengths:
                knot = type(self)(
                    pos=(knot.pos + knot.skip_size + length) % len(knot.rope),
                    rope=_reversed_rope(knot.rope, knot.pos, length),
                    skip_size=knot.skip_size + 1
                )

        return knot

    def hash(self) -> bytes:
        return bytes(
            xor(self.rope[k:k + 16])
            for k in range(0, len(self.rope), 16)
        )


def _reversed_rope(rope: list[int], position: int, length: int) -> list[int]:
    if length == 0:
        return rope

    # shift so that rope starts at `position`
    rope_shifted = rope[position:] + rope[:position]
    # select and reverse
    selected_section = rope_shifted[:length]
    rope_reversed = selected_section[::-1] + rope_shifted[length:]
    # unshift back
    return rope_reversed[-position:] + rope_reversed[:-position]


def xor(numbers: Iterable[int]) -> int:
    return reduce(operator.xor, numbers, 0)


HASH_LENGTHS_SUFFIX = [17, 31, 73, 47, 23]


def knot_hash(input_bytes: bytes) -> bytes:
    lengths = list(input_bytes) + HASH_LENGTHS_SUFFIX
    return Knot().pinched(*lengths, rounds=64).hash()


def line_from_file(fn: str) -> str:
    return open(fn).readline().strip()


def lengths_from_file(fn: str) -> list[int]:
    return [int(val) for val in line_from_file(fn).split(',')]


def input_bytes_from_file(fn: str) -> bytes:
    return line_from_file(fn).encode()


def main(input_path: str = data_path(__file__)) -> tuple[int, str]:
    result_1 = part_1(lengths_from_file(input_path))
    result_2 = part_2(input_bytes_from_file(input_path))
    return result_1, result_2


if __name__ == '__main__':
    main()
