"""
Advent of Code 2018
Day 2: Inventory Management System
https://adventofcode.com/2018/day/2
"""

from collections import Counter
from itertools import combinations
from typing import Iterable

from common.iteration import dgroupby_pairs, single_value
from meta.aoc_tools import data_path


def part_1(box_ids: Iterable[str]) -> int:
    """
    You stop falling through time, catch your breath, and check the screen on the device.
    "Destination reached. Current Year: 1518. Current Location: North Pole Utility Closet 83N10."
    You made it! Now, to find those anomalies.

    Outside the utility closet, you hear footsteps and a voice. "...I'm not sure either. But now
    that so many people have chimneys, maybe he could sneak in that way?" Another voice responds,
    "Actually, we've been working on a new kind of **suit** that would let him fit through tight
    spaces like that. But, I heard that a few days ago, they lost the prototype fabric, the design
    plans, everything! Nobody on the team can even seem to remember important details of the
    project!"

    "Wouldn't they have had enough fabric to fill several boxes in the warehouse? They'd be stored
    together, so the box IDs should be similar. Too bad it would take forever to search the
    warehouse for **two similar box IDs**..." They walk too far away to hear anymore.

    Late at night, you sneak to the warehouse - who knows what kinds of paradoxes you could cause if
    you were discovered - and use your fancy wrist device to quickly scan every box and produce
    a list of the likely candidates (your puzzle input).

    To make sure you didn't miss any, you scan the likely candidate boxes again, counting the number
    that have an ID containing **exactly two of any letter** and then separately counting those with
    **exactly three of any letter**. You can multiply those two counts together to get a rudimentary
    checksum and compare it to what your device predicts.

    For example, if you see the following box IDs:

      - `abcdef` contains no letters that appear exactly two or three times.

        >>> multiple_letters('abcdef')
        {}

      - `bababc` contains two `a` and three `b`, so it counts for both.

        >>> multiple_letters('bababc')
        {3: ['b'], 2: ['a']}

      - `abbcde` contains two `b`, but no letter appears exactly three times.

        >>> multiple_letters('abbcde')
        {2: ['b']}

      - `abcccd` contains three `c`, but no letter appears exactly two times.

        >>> multiple_letters('abcccd')
        {3: ['c']}

      - `aabcdd` contains two `a` and two `d`, but it only counts once.

        >>> multiple_letters('aabcdd')
        {2: ['a', 'd']}

      - `abcdee` contains two `e`.

        >>> multiple_letters('abcdee')
        {2: ['e']}

      - `ababab` contains three `a` and three `b`, but it only counts once.

        >>> multiple_letters('ababab')
        {3: ['a', 'b']}

    Of these box IDs, four of them contain a letter which appears exactly twice, and three of them
    contain a letter which appears exactly three times. Multiplying these together produces
    a checksum of `4 * 3 = 12`.

    **What is the checksum** for your list of box IDs?

        >>> part_1(['abcdef', 'bababc', 'abbcde', 'abcccd', 'aabcdd', 'abcdee', 'ababab'])
        part 1: checksum is 4 * 3 = 12
        12
    """

    counts = Counter(key for box_id in box_ids for key in multiple_letters(box_id))
    count_2, count_3 = counts[2], counts[3]
    checksum = count_2 * count_3
    print(f"part 1: checksum is {count_2} * {count_3} = {checksum}")
    return checksum


def part_2(box_ids: Iterable[str]) -> str:
    """
    Confident that your list of box IDs is complete, you're ready to find the boxes full of
    prototype fabric.

    The boxes will have IDs which differ by exactly one character at the same position in both
    strings. For example, given the following box IDs:

        >>> example = box_ids_from_text('''
        ...     abcde
        ...     fghij
        ...     klmno
        ...     pqrst
        ...     fguij
        ...     axcye
        ...     wvxyz
        ... ''')
        >>> example
        ['abcde', 'fghij', 'klmno', 'pqrst', 'fguij', 'axcye', 'wvxyz']

    The IDs `abcde` and `axcye` are close, but they differ by two characters (the second and
    fourth). However, the IDs `fghij` and `fguij` differ by exactly one character, the third
    (`h` and `u`). Those must be the correct boxes.

    **What letters are common between the two correct box IDs?** (In the example above, this is
    found by removing the differing character from either ID, producing `fgij`.)

        >>> part_2(example)
        part 2: correct box IDs are:
          1. fghij
          2. fguij
        => common letters: fgij
        'fgij'
    """

    box_id_1, box_id_2 = single_value(similar_strings(box_ids))
    common = common_letters(box_id_1, box_id_2)
    print(
        f"part 2: correct box IDs are:\n"
        f"  1. {box_id_1}\n"
        f"  2. {box_id_2}\n"
        f"=> common letters: {common}"
    )
    return common


def multiple_letters(string: str) -> dict[int, list[str]]:
    return dgroupby_pairs(
        (count, number)
        for number, count in Counter(string).items()
        if count > 1
    )


def similar_strings(strings: Iterable[str]) -> Iterable[tuple[str, str]]:
    return (
        pair
        # two strings ...
        for pair in combinations(strings, 2)
        # ... that differ by exactly one character
        if sum(1 for char_1, char_2 in zip(*pair) if char_1 != char_2) == 1
    )


def common_letters(string_1: str, string_2: str) -> str:
    return ''.join(
        char_1
        for char_1, char_2 in zip(string_1, string_2)
        if char_1 == char_2
    )


def box_ids_from_text(text: str) -> list[str]:
    return box_ids_from_lines(text.strip().splitlines())


def box_ids_from_file(fn: str) -> list[str]:
    return box_ids_from_lines(open(fn))


def box_ids_from_lines(lines: Iterable[str]) -> list[str]:
    return [line.strip() for line in lines]


def main(input_path: str = data_path(__file__)) -> tuple[int, str]:
    box_ids = box_ids_from_file(input_path)
    result_1 = part_1(box_ids)
    result_2 = part_2(box_ids)
    return result_1, result_2


if __name__ == '__main__':
    main()
