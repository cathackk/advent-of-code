"""
Advent of Code 2020
Day 6: Custom Customs
https://adventofcode.com/2020/day/6
"""

from typing import Iterable

from common.utils import line_groups
from common.utils import single_value


def part_1(groups: list['Group']) -> int:
    """
    The form asks a series of 26 yes-or-no questions marked `a` through `z`. All you need to do is
    identify the questions for which *anyone in your group* answers "yes". For each of the people
    in a group, you write down the questions for which they answer "yes", one per line. For
    example:

        >>> g = group_from_text('''
        ...
        ...     abcx
        ...     abcy
        ...     abcz
        ...
        ... ''')
        >>> len(g)
        3

    In this group, there are 6 questions to which *anyone* answered "yes":

        >>> answers_anyone(g)
        ['a', 'b', 'c', 'x', 'y', 'z']

    Each group's answers are separated by a blank line, and within each group, each person's
    answers are on a single line. For example:

        >>> gs = groups_from_text('''
        ...
        ...     abc
        ...
        ...     a
        ...     b
        ...     c
        ...
        ...     ab
        ...     ac
        ...
        ...     a
        ...     a
        ...     a
        ...     a
        ...
        ...     b
        ...
        ... ''')

    This list represents answers from five groups:

        >>> g1, g2, g3, g4, g5 = gs

        - The first group contains one person who answered "yes" to 3 questions:

            >>> len(g1), answers_anyone(g1)
            (1, ['a', 'b', 'c'])

        - The second group contains three people; combined, they answered "yes" to 3 questions:

            >>> len(g2), answers_anyone(g2)
            (3, ['a', 'b', 'c'])

        - The third group contains two people; combined, they answered "yes" to 3 questions:

            >>> len(g3), answers_anyone(g3)
            (2, ['a', 'b', 'c'])

        - The fourth group contains four people; combined, they answered "yes" to only 1 question:

            >>> len(g4), answers_anyone(g4)
            (4, ['a'])

        - The last group contains one person who answered "yes" to only 1 question:

            >>> len(g5), answers_anyone(g5)
            (1, ['b'])

    In this example, the sum of these counts is 3 + 3 + 3 + 1 + 1 = *11*.

        >>> part_1(gs)
        part 1: 11 questions total were answered by anyone
        11

    For each group, count the number of questions to which anyone answered "yes".
    *What is the sum of those counts?*
    """

    result = sum(len(answers_anyone(group)) for group in groups)

    print(f"part 1: {result} questions total were answered by anyone")
    return result


def part_2(groups: list['Group']) -> int:
    """
    Actually you don't need to identify the questions to which *anyone* answered "yes";
    you need to identify the questions to which *everyone* answered "yes"!

    Using the same example as above:

        >>> gs = [
        ...     [set('abc')],
        ...     [set('a'), set('b'), set('c')],
        ...     [set('ab'), set('ac')],
        ...     [set('a'), set('a'), set('a'), set('a')],
        ...     [set('b')]
        ... ]
        >>> g1, g2, g3, g4, g5 = gs

    This list represents answers from five groups:

        - In the first group, everyone (all 1 person) answered "yes" to 3 questions:

            >>> answers_everyone(g1)
            ['a', 'b', 'c']

        - In the second group, there is no question to which everyone answered "yes":

            >>> answers_everyone(g2)
            []

        - In the third and fourth group, everyone answered yes to only 1 question:

            >>> answers_everyone(g3)
            ['a']
            >>> answers_everyone(g4)
            ['a']

        - In the fifth group, everyone (all 1 person) answered "yes" to 1 question:

            >>> answers_everyone(g5)
            ['b']

    In this example, the sum of these counts is 3 + 0 + 1 + 1 + 1 = *6*.

        >>> part_2(gs)
        part 2: 6 questions total were answered by everyone
        6

    For each group, count the number of questions to which *everyone* answered "yes".
    *What is the sum of those counts?*
    """

    result = sum(len(answers_everyone(group)) for group in groups)

    print(f"part 2: {result} questions total were answered by everyone")
    return result


Person = set[str]
Group = list[Person]


def group_from_text(text: str) -> Group:
    return single_value(groups_from_text(text))


def groups_from_text(text: str) -> list[Group]:
    return list(groups_from_lines(text.strip().split('\n')))


def groups_from_file(fn: str) -> list[Group]:
    with open(fn) as f:
        return list(groups_from_lines(f))


def groups_from_lines(lines: Iterable[str]) -> Iterable[Group]:
    return (
        [set(line) for line in group]
        for group in line_groups(lines)
    )


def answers_anyone(group: Group) -> list[str]:
    return sorted(set.union(*group))


def answers_everyone(group: Group) -> list[str]:
    return sorted(set.intersection(*group))


if __name__ == '__main__':
    groups_ = groups_from_file('data/06-input.txt')
    part_1(groups_)
    part_2(groups_)
