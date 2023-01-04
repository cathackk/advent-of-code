"""
Advent of Code 2017
Day 9: Stream Processing
https://adventofcode.com/2017/day/9
"""

from typing import Generator
from typing import NamedTuple

from common.iteration import exhaust
from common.iteration import ilen
from meta.aoc_tools import data_path


def part_1(group: str) -> int:
    """
    A large stream blocks your path. According to the locals, it's not safe to cross the stream at
    the moment because it's full of **garbage**. You look down at the stream; rather than water, you
    discover that it's a **stream of characters**.

    You sit for a while and record part of the stream (your puzzle input). The characters represent
    **groups** - sequences that begin with `{` and end with `}`. Within a group, there are zero or
    more other things, separated by commas: either another **group** or **garbage**. Since groups
    can contain other groups, a `}` only closes the **most-recently-opened unclosed group** - that
    is, they are nestable. Your puzzle input represents a single, large group which itself contains
    many smaller ones.

    Sometimes, instead of a group, you will find **garbage**. Garbage begins with `<` and ends
    with `>`. Between those angle brackets, almost any character can appear, including `{` and `}`.
    **Within** garbage, `<` has no special meaning.

    In a futile attempt to clean up the garbage, some program has **canceled** some of the
    characters within it using `!`: inside garbage, **any** character that comes after `!` should be
    **ignored**, including `<`, `>`, and even another `!`.

    You don't see any characters that deviate from these rules. Outside garbage, you only find
    well-formed groups, and garbage always terminates according to the rules above.

    Here are some self-contained pieces of garbage:

      - `<>`, empty garbage.
      - `<random characters>`, garbage containing random characters.
      - `<<<<>`, because the extra `<` are ignored.
      - `<{!>}>`, because the first `>` is canceled.
      - `<!!>`, because the second `!` is canceled, allowing the `>` to terminate the garbage.
      - `<!!!>>`, because the second `!` and the first `>` are canceled.
      - `<{o"i!a,<{i<a>`, which ends at the first `>`.

    Here are some examples of whole streams and the number of groups they contain:

        >>> groups_count('{}')
        1
        >>> groups_count('{{{}}}')
        3
        >>> groups_count('{{},{}}')
        3
        >>> groups_count('{{{},{},{{}}}}')
        6
        >>> groups_count('{<{},{},{{}}>}')  # contains only garbage
        1
        >>> groups_count('{<a>,<a>,<a>,<a>}')
        1
        >>> groups_count('{{<a>},{<a>},{<a>},{<a>}}')
        5
        >>> groups_count('{{<!>},{<!>},{<!>},{<a>}}')  # all but the last `>` are canceled
        2

    Your goal is to find the total score for all groups in your input. Each group is assigned
    a **score** which is one more than the score of the group that immediately contains it.
    (The outermost group gets a score of `1`.)

        >>> group_score('{}')
        1
        >>> group_score('{{{}}}')
        6
        >>> group_score('{{},{}}')
        5
        >>> group_score('{{{},{},{{}}}}')
        16
        >>> group_score('{<a>,<a>,<a>,<a>}')
        1
        >>> group_score('{{<ab>},{<ab>},{<ab>},{<ab>}}')
        9
        >>> group_score('{{<!!>},{<!!>},{<!!>},{<!!>}}')
        9
        >>> group_score('{{<a!>},{<a!>},{<a!>},{<ab>}}')
        3

    **What is the total score** for all groups in your input?

        >>> part_1('{{{},{},{{}}}}')
        part 1: group score is 16
        16
    """

    result = group_score(group)
    print(f"part 1: group score is {result}")
    return result


def part_2(group: str) -> int:
    """
    Now, you're ready to remove the garbage.

    To prove you've removed it, you need to count all of the characters within the garbage. The
    leading and trailing `<` and `>` don't count, nor do any canceled characters or the `!` doing
    the canceling.

        >>> count_garbage('<>')
        0
        >>> count_garbage('<random characters>')
        17
        >>> count_garbage('<<<<>')
        3
        >>> count_garbage('<{!>}>')
        2
        >>> count_garbage('<!!>')
        0
        >>> count_garbage('<!!!>>')
        0
        >>> count_garbage('<{o"i!a,<{i<a>')
        10

    **How many non-canceled characters are within the garbage** in your puzzle input?

        >>> part_2('{<>,<random characters>,<<<<>,<{!>}>,<!!>}')
        part 2: 22 garbage collected
        22
    """

    result = count_garbage(group)
    print(f"part 2: {result} garbage collected")
    return result


class Group(NamedTuple):
    start: int
    end: int
    depth: int


def find_groups(text: str) -> Generator[Group, None, int]:
    starts_buffer = []
    in_garbage = False
    ignore_next = False
    garbage_collected = 0

    for k, c in enumerate(text):
        if not in_garbage:
            # outside of garbage
            if c == '{':
                starts_buffer.append(k)
            elif c == '}':
                depth = len(starts_buffer)
                start = starts_buffer.pop()
                end = k
                yield Group(start, end, depth)
            elif c == '<':
                in_garbage = True
        else:
            # in garbage
            if ignore_next:
                ignore_next = False
            elif c == '>':
                in_garbage = False
            elif c == '!':
                ignore_next = True
            else:
                garbage_collected += 1

    return garbage_collected


def groups_count(text: str) -> int:
    return ilen(find_groups(text))


def group_score(text: str) -> int:
    return sum(group.depth for group in find_groups(text))


def count_garbage(text: str) -> int:
    return exhaust(find_groups(text))


def group_from_file(fn: str) -> str:
    return open(fn).readline().strip()


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    group = group_from_file(input_path)
    result_1 = part_1(group)
    result_2 = part_2(group)
    return result_1, result_2


if __name__ == '__main__':
    main()
