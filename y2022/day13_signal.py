"""
Advent of Code 2022
Day 13: Distress Signal
https://adventofcode.com/2022/day/13
"""

import math
import re
from ast import literal_eval
from dataclasses import dataclass
from typing import Iterable

from common.file import relative_path
from common.math import sgn
from common.text import line_groups


def part_1(packet_pairs: Iterable['PacketPair']) -> int:
    """
    You climb the hill and again try contacting the Elves. However, you instead receive a signal you
    weren't expecting: a **distress signal**.

    Your handheld device must still not be working properly; the packets from the distress signal
    got decoded **out of order**. You'll need to re-order the list of received packets (your puzzle
    input) to decode the message.

    Your list consists of pairs of packets; pairs are separated by a blank line. You need to
    identify **how many pairs of packets are in the right order**.

    For example:

        >>> pps = packet_pairs_from_text('''
        ...     [1,1,3,1,1]
        ...     [1,1,5,1,1]
        ...
        ...     [[1],[2,3,4]]
        ...     [[1],4]
        ...
        ...     [9]
        ...     [[8,7,6]]
        ...
        ...     [[4,4],4,4]
        ...     [[4,4],4,4,4]
        ...
        ...     [7,7,7,7]
        ...     [7,7,7]
        ...
        ...     []
        ...     [3]
        ...
        ...     [[[]]]
        ...     [[]]
        ...
        ...     [1,[2,[3,[4,[5,6,7]]]],8,9]
        ...     [1,[2,[3,[4,[5,6,0]]]],8,9]
        ... ''')
        >>> len(pps)
        8

    Packet data consists of lists and integers. Each list starts with `[`, ends with `]`, and
    contains zero or more comma-separated values (either integers or other lists). Each packet is
    always a list and appears on its own line.

    When comparing two values, the first value is called **left** and the second value is called
    **right**. Then:

      - If **both values are integers**, the **lower integer** should come first. If the left
        integer is lower than the right integer, the inputs are in the right order. If the left
        integer is higher than the right integer, the inputs are not in the right order. Otherwise,
        the inputs are the same integer; continue checking the next part of the input.
      - If **both values are lists**, compare the first value of each list, then the second value,
        and so on. If the left list runs out of items first, the inputs are in the right order.
        If the right list runs out of items first, the inputs are not in the right order.
        If the lists are the same length and no comparison makes a decision about the order,
        continue checking the next part of the input.
      - If **exactly one value is an integer**, convert the integer to a list which contains that
        integer as its only value, then retry the comparison. For example, if comparing `[0,0,0]`
        and `2`, convert the right value to `[2]` (a list containing `2`); the result is then found
        by instead comparing `[0,0,0]` and `[2]`.

    Using these rules, you can determine which of the pairs in the example are in the right order:

        >>> def in_correct_order(pair):
        ...     left, right = pair
        ...     return left < right

        >>> pps[0]
        (Packet([1, 1, 3, 1, 1]), Packet([1, 1, 5, 1, 1]))
        >>> in_correct_order(pps[0])
        True

        >>> pps[1]
        (Packet([[1], [2, 3, 4]]), Packet([[1], 4]))
        >>> in_correct_order(pps[1])
        True

        >>> pps[2]
        (Packet([9]), Packet([[8, 7, 6]]))
        >>> in_correct_order(pps[2])
        False

        >>> pps[3]
        (Packet([[4, 4], 4, 4]), Packet([[4, 4], 4, 4, 4]))
        >>> in_correct_order(pps[3])
        True

        >>> pps[4]
        (Packet([7, 7, 7, 7]), Packet([7, 7, 7]))
        >>> in_correct_order(pps[4])
        False

        >>> pps[5]
        (Packet([]), Packet([3]))
        >>> in_correct_order(pps[5])
        True

        >>> pps[6]
        (Packet([[[]]]), Packet([[]]))
        >>> in_correct_order(pps[6])
        False

        >>> pps[7]
        (Packet([1, [2, [3, [4, [5, 6, 7]]]], 8, 9]), Packet([1, [2, [3, [4, [5, 6, 0]]]], 8, 9]))
        >>> in_correct_order(pps[7])
        False

    What are the indices of the pairs that are already in the right order? (The first pair has
    index 1, the second pair has index 2, and so on.) In the above example, the pairs in the right
    order are 1, 2, 4, and 6:

        >>> [index for index, (left, right) in enumerate(pps, start=1) if left < right]
        [1, 2, 4, 6]

    The sum of these indices is 13:

        >>> sum(_)
        13

    Determine which pairs of packets are already in the right order.
    **What is the sum of the indices of those pairs?**

        >>> part_1(pps)
        part 1: sum of indices of pairs in correct order is 13
        13
    """

    result = sum(
        index
        for index, (left, right) in enumerate(packet_pairs, start=1)
        if left < right
    )

    print(f"part 1: sum of indices of pairs in correct order is {result}")
    return result


def part_2(packet_pairs: list['PacketPair']) -> int:
    r"""
    Now, you just need to put all of the packets in the right order. Disregard the blank lines in
    your list of received packets.

    The distress signal protocol also requires that you include two additional **divider packets**:

        >>> DIVIDER_PACKETS
        [Packet([[2]]), Packet([[6]])]

    Using the same rules as before, organize all packets - the ones in your list of received packets
    as well as the two divider packets - into the correct order.

    For the example above, the result of putting the packets in the correct order is:

        >>> pps = packet_pairs_from_file('data/13-example.txt')
        >>> packets_sorted = sorted([packet for pair in pps for packet in pair] + DIVIDER_PACKETS)
        >>> print("\n".join(str(p) for p in packets_sorted))
        []
        [[]]
        [[[]]]
        [1,1,3,1,1]
        [1,1,5,1,1]
        [[1],[2,3,4]]
        [1,[2,[3,[4,[5,6,0]]]],8,9]
        [1,[2,[3,[4,[5,6,7]]]],8,9]
        [[1],4]
        [[2]]
        [3]
        [[4,4],4,4]
        [[4,4],4,4,4]
        [[6]]
        [7,7,7]
        [7,7,7,7]
        [[8,7,6]]
        [9]

    Afterward, locate the divider packets. To find the **decoder key** for this distress signal, you
    need to determine the indices of the two divider packets and multiply them together. (The first
    packet is at index 1, the second packet is at index 2, and so on.) In this example, the divider
    packets are 10th and 14th:

        >>> divider_indices(packets_sorted)
        [10, 14]

    And so the decoder key is 140:

        >>> decoder_key(packets_sorted)
        140

    Organize all of the packets into the correct order.
    **What is the decoder key for the distress signal?**

        >>> part_2(pps)
        part 2: decoder key is 140
        140
    """

    all_packets = [packet for pair in packet_pairs for packet in pair] + DIVIDER_PACKETS
    result = decoder_key(sorted(all_packets))

    print(f"part 2: decoder key is {result}")
    return result


@dataclass
class Packet:
    value: list[int | list]

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.value!r})'

    def __str__(self) -> str:
        return str(self.value).replace(' ', '')

    def __eq__(self, right):
        return isinstance(right, Packet) and Packet.compare(self.value, right.value) == 0

    def __lt__(self, right):
        if not isinstance(right, Packet):
            return NotImplemented

        return Packet.compare(self.value, right.value) < 0

    @staticmethod
    def compare(left: int | list[int], right: int | list[int]) -> int:
        if isinstance(left, int) and isinstance(right, int):
            # int vs int
            return sgn(left - right)

        elif isinstance(left, list) and isinstance(right, list):
            # list vs list
            for val_left, val_right in zip(left, right):
                if (val_comp := Packet.compare(val_left, val_right)):
                    return val_comp
            else:
                return sgn(len(left) - len(right))

        elif isinstance(left, list) and isinstance(right, int):
            # list vs int
            return Packet.compare(left, [right])

        elif isinstance(left, int) and isinstance(right, list):
            # int vs list
            return Packet.compare([left], right)

        else:
            raise TypeError(type(left), type(right))

    @classmethod
    def from_line(cls, line: str) -> 'Packet':
        line = line.strip()

        # make sure the input is safe for eval
        if not re.fullmatch(r'[0123456789,\[\]]*', line):
            raise ValueError(line)

        return cls(literal_eval(line))


PacketPair = tuple[Packet, Packet]


DIVIDER_PACKETS = [Packet([[2]]), Packet([[6]])]


def divider_indices(packets: list[Packet]) -> list[int]:
    return [index for index, packet in enumerate(packets, start=1) if packet in DIVIDER_PACKETS]


def decoder_key(packets: list[Packet]) -> int:
    return math.prod(divider_indices(packets))


def packet_pairs_from_file(fn: str) -> list[PacketPair]:
    return list(packet_pairs_from_lines(open(relative_path(__file__, fn))))


def packet_pairs_from_text(text: str) -> list[PacketPair]:
    return list(packet_pairs_from_lines(text.strip().splitlines()))


def packet_pairs_from_lines(lines: Iterable[str]) -> Iterable[PacketPair]:
    return (
        (Packet.from_line(left), Packet.from_line(right))
        for left, right in line_groups(lines)
    )


def main(input_fn: str = 'data/13-input.txt') -> tuple[int, int]:
    packet_pairs = packet_pairs_from_file(input_fn)
    result_1 = part_1(packet_pairs)
    result_2 = part_2(packet_pairs)
    return result_1, result_2


if __name__ == '__main__':
    main()
