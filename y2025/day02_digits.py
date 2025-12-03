"""
Advent of Code 2025
Day 2: Gift Shop
https://adventofcode.com/2025/day/2
"""

from typing import Iterable, Iterator

from tqdm import tqdm

from common.file import relative_path


def part_1(ranges: Iterable[range]) -> int:
    """
    You get inside and take the elevator to its only other stop: the gift shop. "Thank you for
    visiting the North Pole!" gleefully exclaims a nearby sign. You aren't sure who is even allowed
    to visit the North Pole, but you know you can access the lobby through here, and from there you
    can access the rest of the North Pole base.

    As you make your way through the surprisingly extensive selection, one of the clerks recognizes
    you and asks for your help.

    As it turns out, one of the younger Elves was playing on a gift shop computer and managed to add
    a whole bunch of invalid product IDs to their gift shop database! Surely, it would be no trouble
    for you to identify the invalid product IDs for them, right?

    They've even checked most of the product ID ranges already; they only have a few product ID
    ranges (your puzzle input) that you'll need to check. For example:

        >>> example = ranges_from_text('''
        ...     11-22,95-115,998-1012,1188511880-1188511890,222220-222224,
        ...     1698522-1698528,446443-446449,38593856-38593862,565653-565659,
        ...     824824821-824824827,2121212118-2121212124
        ... ''')

    (The ID ranges are wrapped here for legibility; in your input, they appear on a single long
    line.)

    The ranges are separated by commas (`,`); each range gives its **first ID** and **last ID**
    separated by a dash (`-`).

        >>> example  # doctest: +NORMALIZE_WHITESPACE
        [range(11, 23), range(95, 116), range(998, 1013), range(1188511880, 1188511891),
         range(222220, 222225), range(1698522, 1698529), range(446443, 446450),
         range(38593856, 38593863), range(565653, 565660), range(824824821, 824824828),
         range(2121212118, 2121212125)]


    Since the young Elf was just doing silly patterns, you can find the **invalid IDs** by looking
    for any ID which is made only of some sequence of digits repeated twice. So, `55` (`5` twice),
    `6464` (`64` twice), and `123123` (`123` twice) would all be invalid IDs.

        >>> is_invalid_id(55)
        True
        >>> is_invalid_id(6464)
        True
        >>> is_invalid_id(123123)
        True

    None of the numbers have leading zeroes; `0101` isn't an ID at all. (`101` is a **valid** ID
    that you would ignore.)

        >>> is_invalid_id(101)
        False

    Your job is to find all the invalid IDs that appear in the given ranges. In the above example:

        >>> [list(invalid_ids(range_)) for range_ in example]
        [[11, 22], [99], [1010], [1188511885], [222222], [], [446446], [38593859], [], [], []]

    Adding up all the invalid IDs in this example produces:

        >>> sum(inv_id for inv_ids in _ for inv_id in inv_ids)
        1227775554

    **What do you get if you add up all of the invalid IDs?**

        >>> part_1(example)
        part 1: sum of all the invalid IDs is 1227775554
        1227775554
    """

    result = sum(
        invalid_id
        for range_ in tqdm(ranges, unit=" ranges", delay=0.25)
        for invalid_id in invalid_ids(range_)
    )

    print(f"part 1: sum of all the invalid IDs is {result}")
    return result


def part_2(ranges: Iterable[range]) -> int:
    """
    The clerk quickly discovers that there are still invalid IDs in the ranges in your list. Maybe
    the young Elf was doing other silly patterns as well?

    Now, an ID is invalid if it is made only of some sequence of digits repeated **at least** twice:

        >>> is_invalid_id(12341234, multiple=True)  # `1234` two times
        True
        >>> is_invalid_id(123123123, multiple=True)  # `123` three times
        True
        >>> is_invalid_id(1212121212, multiple=True)  # `12` five times
        True
        >>> is_invalid_id(1111111, multiple=True)  # `1` seven times
        True

    From the same example as before:

        >>> example = ranges_from_file('data/02-example.txt')
        >>> [list(invalid_ids(range_, multiple=True)) for range_ in example]
        ... # doctest: +NORMALIZE_WHITESPACE
        [[11, 22], [99, 111], [999, 1010], [1188511885], [222222], [], [446446], [38593859],
         [565656], [824824824], [2121212121]]

    Adding up all the invalid IDs in this example produces

        >>> sum(inv_id for inv_ids in _ for inv_id in inv_ids)
        4174379265

    **What do you get if you add up all of the invalid IDs using these new rules?**

        >>> part_2(example)
        part 2: sum of all the invalid IDs (including multiple repeats) is 4174379265
        4174379265
    """

    result = sum(
        invalid_id
        for range_ in tqdm(ranges, unit=" ranges", delay=0.25)
        for invalid_id in invalid_ids(range_, multiple=True)
    )

    print(f"part 2: sum of all the invalid IDs (including multiple repeats) is {result}")
    return result


def invalid_ids(ids_range: range, multiple: bool = False) -> Iterator[int]:
    return (id_ for id_ in ids_range if is_invalid_id(id_, multiple=multiple))


def is_invalid_id(id_: int, multiple: bool = False) -> bool:
    id_str = str(id_)
    id_len = len(id_str)

    if multiple:
        group_lengths = range(1, id_len // 2 + 1)
    elif id_len % 2 == 0:
        group_lengths = [id_len // 2]
    else:
        return False

    return any(
        all(
            id_str[:group_length] == id_str[i * group_length:(i + 1) * group_length]
            for i in range(1, id_len // group_length)
        )
        for group_length in group_lengths
        if id_len % group_length == 0
    )


def ranges_from_file(fn: str) -> list[range]:
    return list(ranges_from_lines(open(relative_path(__file__, fn))))


def ranges_from_text(text: str) -> list[range]:
    return list(ranges_from_lines(text.strip().splitlines()))


def ranges_from_lines(lines: Iterable[str]) -> Iterable[range]:
    return (
        range_from_str(range_str)
        for line in lines
        for range_str in line.strip().split(',')
        if range_str
    )


def range_from_str(range_str: str) -> range:
    first, last = range_str.split('-')
    return range(int(first), int(last) + 1)


def main(input_fn: str = 'data/02-input.txt') -> tuple[int, int]:
    ranges = ranges_from_file(input_fn)
    result_1 = part_1(ranges)
    result_2 = part_2(ranges)
    return result_1, result_2


if __name__ == '__main__':
    main()
