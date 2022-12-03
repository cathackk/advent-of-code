"""
Advent of Code 2022
Day 3: Rucksack Reorganization
https://adventofcode.com/2022/day/3
"""

import string
from typing import Iterable

from common.file import relative_path
from common.iteration import chunks


def part_1(rucksacks: Iterable[str]) -> int:
    """
    One Elf has the important job of loading all of the rucksacks with supplies for the jungle
    journey. Unfortunately, that Elf didn't quite follow the packing instructions, and so a few
    items now need to be rearranged.

    Each rucksack has two large **compartments**. All items of a given type are meant to go into
    exactly one of the two compartments. The Elf that did the packing failed to follow this rule for
    exactly one item type per rucksack.

    The Elves have made a list of all of the items currently in each rucksack (your puzzle input),
    but they need your help finding the errors. Every item type is identified by a single lowercase
    or uppercase letter (that is, `a` and `A` refer to different types of items).

    The list of items for each rucksack is given as characters all on a single line. A given
    rucksack always has the same number of items in each of its two compartments, so the first half
    of the characters represent items in the first compartment, while the second half of the
    characters represent items in the second compartment.

    For example, suppose you have the following list of contents from six rucksacks:

        >>> rs = rucksacks_from_text('''
        ...     vJrwpWtwJgWrhcsFMMfFFhFp
        ...     jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL
        ...     PmmdzqPrVvPwwTWBwg
        ...     wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn
        ...     ttgJtRGJQctTZtZT
        ...     CrZsJsPPZsGzwwsLwLmpwMDw
        ... ''')

      - The first rucksack contains the items `vJrwpWtwJgWrhcsFMMfFFhFp`, which means its first
        compartment contains the items `vJrwpWtwJgWr`, while the second compartment contains the
        items `hcsFMMfFFhFp`.

        >>> rs[0]
        'vJrwpWtwJgWrhcsFMMfFFhFp'
        >>> compartments(rs[0])
        ('vJrwpWtwJgWr', 'hcsFMMfFFhFp')

        The only item type that appears in both compartments is lowercase **`p`**.

        >>> common_item(rs[0])
        'p'

      - The second rucksack's compartments contain `jqHRNqRjqzjGDLGL` and `rsFMfFZSrLrFZsSL`.
        The only item type that appears in both compartments is uppercase **`L`**.

        >>> compartments(rs[1])
        ('jqHRNqRjqzjGDLGL', 'rsFMfFZSrLrFZsSL')
        >>> common_item(rs[1])
        'L'

      - The third rucksack's compartments contain `PmmdzqPrV` and `vPwwTWBwg`;
        the only common item type is uppercase **`P`**.

        >>> compartments(rs[2])
        ('PmmdzqPrV', 'vPwwTWBwg')
        >>> common_item(rs[2])
        'P'

      - The fourth rucksack's compartments only share item type **`v`**.
      - The fifth rucksack's compartments only share item type **`t`**.
      - The sixth rucksack's compartments only share item type **`s`**.

        >>> [common_item(r) for r in rs[3:]]
        ['v', 't', 's']

    To help prioritize item rearrangement, every item type can be converted to a **priority**:

      - Lowercase item types `a` through `z` have priorities 1 through 26.
      - Uppercase item types `A` through `Z` have priorities 27 through 52.

    In the above example, the priority of the item type that appears in both compartments of each
    rucksack is 16 (`p`), 38 (`L`), 42 (`P`), 22 (`v`), 20 (`t`), and 19 (`s`):

        >>> {(it := common_item(r)): PRIORITY[it] for r in rs}
        {'p': 16, 'L': 38, 'P': 42, 'v': 22, 't': 20, 's': 19}

    The sum of these is 157:

        >>> sum(PRIORITY[common_item(r)] for r in rs)
        157

    Find the item type that appears in both compartments of each rucksack.
    **What is the sum of the priorities of those item types?**

        >>> part_1(rs)
        part 1: priority sum of all rucksacks is 157
        157
    """

    result = sum(PRIORITY[common_item(rucksack)] for rucksack in rucksacks)

    print(f"part 1: priority sum of all rucksacks is {result}")
    return result


def part_2(rucksacks: Iterable[str]) -> int:
    """
    As you finish identifying the misplaced items, the Elves come to you with another issue.

    For safety, the Elves are divided into groups of three. Every Elf carries a badge that
    identifies their group. For efficiency, within each group of three Elves, the badge is the
    **only item type carried by all three Elves**. That is, if a group's badge is item type `B`,
    then all three Elves will have item type `B` somewhere in their rucksack, and at most two of
    the Elves will be carrying any other item type.

    The problem is that someone forgot to put this year's updated authenticity sticker on the
    badges. All of the badges need to be pulled out of the rucksacks so the new authenticity
    stickers can be attached.

    Additionally, nobody wrote down which item type corresponds to each group's badges. The only way
    to tell which item type is the right one is by finding the one item type that is
    **common between all three Elves** in each group.

    Every set of three lines in your list corresponds to a single group, but each group can have
    a different badge item type. So, in the above example, the first group's rucksacks are the
    first three lines:

        >>> rs = rucksacks_from_file('data/03-example.txt')
        >>> len(rs)
        6
        >>> rgs = list(groups(rs))
        >>> len(rgs)
        2
        >>> rgs[0]
        ['vJrwpWtwJgWrhcsFMMfFFhFp', 'jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL', 'PmmdzqPrVvPwwTWBwg']

    And the second group's rucksacks are the next three lines:

        >>> rgs[1]
        ['wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn', 'ttgJtRGJQctTZtZT', 'CrZsJsPPZsGzwwsLwLmpwMDw']

    In the first group, the only item type that appears in all three rucksacks is lowercase `r`;
    this must be their badges. In the second group, their badge item type must be `Z`.

        >>> badge(rgs[0])
        'r'
        >>> badge(rgs[1])
        'Z'

    Priorities for these items must still be found to organize the sticker attachment efforts:
    here, they are 18 (`r`) for the first group and 52 (`Z`) for the second group:

        >>> {(b := badge(rg)): PRIORITY[b] for rg in rgs}
        {'r': 18, 'Z': 52}

    The sum of these is **70**:

        >>> sum(PRIORITY[badge(rg)] for rg in rgs)
        70

    Find the item type that corresponds to the badges of each three-Elf group.
    **What is the sum of the priorities of those item types?**

        >>> part_2(rs)
        part 2: priority sum of all badges is 70
        70
    """

    result = sum(PRIORITY[badge(group)] for group in groups(rucksacks))

    print(f"part 2: priority sum of all badges is {result}")
    return result


def compartments(rucksack: str) -> tuple[str, str]:
    mid = len(rucksack) // 2
    c1, c2 = rucksack[:mid], rucksack[mid:]
    assert len(c1) == len(c2)
    return c1, c2


def common_item(rucksack: str) -> str:
    c1, c2 = compartments(rucksack)
    (common,) = set(c1) & set(c2)
    return common


def groups(rucksacks: Iterable[str], group_size: int = 3) -> Iterable[list[str]]:
    return chunks(rucksacks, group_size)


def badge(rucksack_groups: list[str]) -> str:
    (common,) = set.intersection(*(set(group) for group in rucksack_groups))
    return common


PRIORITY = {c: v for v, c in enumerate(string.ascii_letters, start=1)}


def rucksacks_from_text(text: str) -> list[str]:
    return [line.strip() for line in text.strip().splitlines()]


def rucksacks_from_file(fn: str) -> list[str]:
    return [line.strip() for line in open(relative_path(__file__, fn))]


if __name__ == '__main__':
    rucksacks_ = rucksacks_from_file('data/03-input.txt')
    part_1(rucksacks_)
    part_2(rucksacks_)
