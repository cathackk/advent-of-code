"""
Advent of Code 2024
Day 1: Historian Hysteria
https://adventofcode.com/2024/day/1
"""

from collections import Counter
from typing import Iterable

from common.file import relative_path


def part_1(list_left: list[int], list_right: list[int]) -> int:
    """
    The **Chief Historian** is always present for the big Christmas sleigh launch, but nobody has
    seen him in months! Last anyone heard, he was visiting locations that are historically
    significant to the North Pole; a group of Senior Historians has asked you to accompany them as
    they check the places they think he was most likely to visit.

    You haven't even left yet and the group of Elvish Senior Historians has already hit a problem:
    their list of locations to check is currently **empty**. Eventually, someone decides that
    the best place to check first would be the Chief Historian's office.

    Upon pouring into the office, everyone confirms that the Chief Historian is indeed nowhere to be
    found. Instead, the Elves discover an assortment of notes and lists of historically significant
    locations! This seems to be the planning the Chief Historian was doing before he left. Perhaps
    these notes can be used to determine which locations to search?

    Throughout the Chief's office, the historically significant locations are listed not by name but
    by a unique number called the **location ID**. To make sure they don't miss anything,
    The Historians split into two groups, each searching the office and trying to create their own
    complete list of location IDs.

    There's just one problem: by holding the two lists up **side by side** (your puzzle input),
    it quickly becomes clear that the lists aren't very similar. Maybe you can help The Historians
    reconcile their lists?

    For example:

        >>> nums_left, nums_right = lists_from_text('''
        ...     3   4
        ...     4   3
        ...     2   5
        ...     1   3
        ...     3   9
        ...     3   3
        ... ''')
        >>> nums_left
        [3, 4, 2, 1, 3, 3]
        >>> nums_right
        [4, 3, 5, 3, 9, 3]

    Maybe the lists are only off by a small amount! To find out, pair up the numbers and measure how
    far apart they are. Pair up **the smallest number in the left list** with **the smallest number
    in the right list**, then **the second-smallest left number** with **the second-smallest right
    number**, and so on.

        >>> list(zip(sorted(nums_left), sorted(nums_right)))
        [(1, 3), (2, 3), (3, 3), (3, 4), (3, 5), (4, 9)]

    Within each pair, figure out **how far apart** the two numbers are; you'll need to **add up all
    of those distances**:

        >>> [abs(a - b) for a, b in _]
        [2, 1, 0, 1, 2, 5]

    To find the **total distance** between the left list and the right list, add up the distances
    between all of the pairs you found:

        >>> sum(_)
        11

    Your actual left and right lists contain many location IDs.
    **What is the total distance between your lists?**

        >>> part_1(nums_left, nums_right)
        part 1: the total distance between the lists is 11
        11
    """

    result = sum(abs(a - b) for a, b in zip(sorted(list_left), sorted(list_right)))

    print(f"part 1: the total distance between the lists is {result}")
    return result


def part_2(list_left: list[int], list_right: list[int]) -> int:
    """
    Your analysis only confirmed what everyone feared: the two lists of location IDs are indeed very
    different.

    Or are they?

    The Historians can't agree on which group made the mistakes **or** how to read most of
    the Chief's handwriting, but in the commotion you notice an interesting detail: a lot of
    location IDs appear in both lists! Maybe the other numbers aren't location IDs at all but rather
    misinterpreted handwriting.

    This time, you'll need to figure out exactly how often each number from the left list appears in
    the right list. Calculate a total **similarity score** by adding up each number in the left list
    after multiplying it by the number of times that number appears in the right list.

    Here are the same example lists again:

        >>> nums_left, nums_right = lists_from_file('data/01-example.txt')
        >>> nums_left, nums_right
        ([3, 4, 2, 1, 3, 3], [4, 3, 5, 3, 9, 3])
        >>> counts_right = Counter(nums_right)
        >>> counts_right
        Counter({3: 3, 4: 1, 5: 1, 9: 1})

    For these example lists, here is the process of finding the similarity score:

      - The first number in the left list is `3`. It appears in the right list three times,
        so the similarity score increases by `3 * 3 = 9`.
      - The second number in the left list is `4`. It appears in the right list once,
        so the similarity score increases by `4 * 1 = 4`.
      - The third number in the left list is `2`. It does not appear in the right list,
        so the similarity score does not increase (`2 * 0 = 0`).
      - The fourth number, `1`, also does not appear in the right list.
      - The fifth number, `3`, appears in the right list three times;
        the similarity score increases by `9`.
      - The last number, `3`, appears in the right list three times; the similarity score again
        increases by 9.

        >>> [num * counts_right[num] for num in nums_left]
        [9, 4, 0, 0, 9, 9]

    So, for these example lists, the similarity score at the end of this process is 31:

        >>> sum(_)
        31

    Once again consider your left and right lists. **What is their similarity score?**

        >>> part_2(nums_left, nums_right)
        part 2: the similarity score of the lists is 31
        31
    """

    counts_right = Counter(list_right)

    result = sum(num * counts_right[num] for num in list_left)

    print(f"part 2: the similarity score of the lists is {result}")
    return result


def lists_from_file(fn: str) -> tuple[list[int], list[int]]:
    return lists_from_lines(open(relative_path(__file__, fn)))


def lists_from_text(text: str) -> tuple[list[int], list[int]]:
    return lists_from_lines(text.strip().splitlines())


def lists_from_lines(lines: Iterable[str]) -> tuple[list[int], list[int]]:
    pairs = ((int(a), int(b)) for a, b in (line.split() for line in lines))
    nums_1, nums_2 = zip(*pairs)
    return list(nums_1), list(nums_2)


def main(input_fn: str = 'data/01-input.txt') -> tuple[int, int]:
    list_left, list_right = lists_from_file(input_fn)
    result_1 = part_1(list_left, list_right)
    result_2 = part_2(list_left, list_right)
    return result_1, result_2


if __name__ == '__main__':
    main()
