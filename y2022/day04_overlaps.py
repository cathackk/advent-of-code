"""
Advent of Code 2022
Day 4: Camp Cleanup
https://adventofcode.com/2022/day/4
"""

from typing import Iterable

from common.text import parse_line
from meta.aoc_tools import data_path

Range = tuple[int, int]
Pair = tuple[Range, Range]


def part_1(assignments: list[Pair]) -> int:
    """
    Space needs to be cleared before the last supplies can be unloaded from the ships, and so
    several Elves have been assigned the job of cleaning up sections of the camp. Every section has
    a unique **ID number**, and each Elf is assigned a range of section IDs.

    However, as some Elves compare their section assignments with each other, they've noticed that
    many of the assignments **overlap**. To try to quickly find overlaps and reduce duplicated
    effort, the Elves pair up and make a **big list of the section assignments for each pair**
    (your puzzle input).

    For example, consider the following list of section assignment pairs:

        >>> work = assignments_from_text('''
        ...     2-4,6-8
        ...     2-3,4-5
        ...     5-7,7-9
        ...     2-8,3-7
        ...     6-6,4-6
        ...     2-6,4-8
        ... ''')

    For the first few pairs, this list means:

      - Within the first pair of Elves, the first Elf was assigned sections `2-4` (sections `2`,
        `3`, and `4`), while the second Elf was assigned sections `6-8` (sections `6`, `7`, `8`).

        >>> work[0]
        ((2, 4), (6, 8))

      - The Elves in the second pair were each assigned two sections.

        >>> work[1]
        ((2, 3), (4, 5))

      - The Elves in the third pair were each assigned three sections: one got sections `5`, `6`,
        and `7`, while the other also got `7`, plus `8` and `9`.

        >>> work[2]
        ((5, 7), (7, 9))

    This example list uses single-digit section IDs to make it easier to draw; your actual list
    might contain larger numbers. Visually, these pairs of section assignments look like this:

        >>> draw_assignments(work, range(1, 10))
        .234.....  2-4
        .....678.  6-8
                   ---
        .23......  2-3
        ...45....  4-5
                   ---
        ....567..  5-7
        ......789  7-9
                   ---
        .2345678.  2-8
        ..34567..  3-7
                   ---
        .....6...  6-6
        ...456...  4-6
                   ---
        .23456...  2-6
        ...45678.  4-8

    Some of the pairs have noticed that one of their assignments **fully contains** the other. For
    example, `2-8` fully contains `3-7`, and `6-6` is fully contained by `4-6`.

        >>> has_full_overlap(((2, 8), (3, 7)))
        True
        >>> has_full_overlap(((6, 6), (4, 6)))
        True
        >>> has_full_overlap(((2, 4), (3, 5)))
        False

    In pairs where one assignment fully contains the other, one Elf in the pair would be exclusively
    cleaning sections their partner will already be cleaning, so these seem like the most in need of
    reconsideration. In this example, there are **2** such pairs.

        >>> [pair for pair in work if has_full_overlap(pair)]
        [((2, 8), (3, 7)), ((6, 6), (4, 6))]

    **In how many assignment pairs does one range fully contain the other?**

        >>> part_1(work)
        part 1: one pair fully contains the other in 2 assignments
        2
    """

    result = sum(1 for pair in assignments if has_full_overlap(pair))

    print(f"part 1: one pair fully contains the other in {result} assignments")
    return result


def part_2(assignments: Iterable[Pair]) -> int:
    """
    It seems like there is still quite a bit of duplicate work planned. Instead, the Elves would
    like to know the number of pairs that **overlap at all**.

    In the above example, the first two pairs (`2-4,6-8` and `2-3,4-5`) don't overlap, while the
    remaining four pairs do overlap:

      - `5-7,7-9` overlaps in a single section, `7`.
      - `2-8,3-7` overlaps all of the sections `3` through `7`.
      - `6-6,4-6` overlaps in a single section, `6`.
      - `2-6,4-8` overlaps in sections `4`, `5`, and `6`.

        >>> work = assignments_from_file(data_path(__file__, 'example.txt'))
        >>> [pair for pair in work if has_overlap(pair)]
        [((5, 7), (7, 9)), ((2, 8), (3, 7)), ((6, 6), (4, 6)), ((2, 6), (4, 8))]

    So, in this example, the number of overlapping assignment pairs is **4**.

        >>> len(_)
        4

    **In how many assignment pairs do the ranges overlap?**

        >>> part_2(work)
        part 2: pairs overlap in 4 assignments
        4
    """

    result = sum(1 for pair in assignments if has_overlap(pair))

    print(f"part 2: pairs overlap in {result} assignments")
    return result


def has_full_overlap(pair: Pair) -> bool:
    (elf_1_start, elf_1_stop), (elf_2_start, elf_2_stop) = pair
    return (
        (elf_1_start <= elf_2_start and elf_2_stop <= elf_1_stop) or
        (elf_2_start <= elf_1_start and elf_1_stop <= elf_2_stop)
    )


def has_overlap(pair: Pair) -> bool:
    (elf_1_start, elf_1_stop), (elf_2_start, elf_2_stop) = pair
    return elf_1_start <= elf_2_stop and elf_2_start <= elf_1_stop


def draw_assignments(assignments: Iterable[Pair], draw_range: range):
    separator = ' ' * (len(draw_range) + 2) + '---'

    def char(section_id: int) -> str:
        return chr(section_id + ord('0'))

    def sections(elf_: Range) -> str:
        elf_range = range(elf_[0], elf_[1] + 1)
        return ''.join(char(sid) if sid in elf_range else '.' for sid in draw_range)

    for index, pair in enumerate(assignments):
        if index > 0:
            print(separator)
        for elf in pair:
            print(f'{sections(elf)}  {elf[0]}-{elf[1]}')


def assignments_from_text(text: str) -> list[Pair]:
    return list(assignments_from_lines(text.strip().splitlines()))


def assignments_from_file(fn: str) -> list[Pair]:
    return list(assignments_from_lines(open(fn)))


def assignments_from_lines(lines: Iterable[str]) -> Iterable[Pair]:
    def to_pair(line: str) -> Pair:
        # '2-4,6-8'
        e1_start, e1_stop, e2_start, e2_stop = parse_line(line.strip(), '$-$,$-$')
        return (int(e1_start), int(e1_stop)), (int(e2_start), int(e2_stop))

    return (to_pair(line) for line in lines)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    assignments = assignments_from_file(input_path)
    result_1 = part_1(assignments)
    result_2 = part_2(assignments)
    return result_1, result_2


if __name__ == '__main__':
    main()
