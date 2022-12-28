"""
Advent of Code 2020
Day 7: Handy Haversacks
https://adventofcode.com/2020/day/7
"""

from functools import lru_cache
from typing import Iterable

from common.file import relative_path
from common.iteration import dgroupby_pairs_set
from common.text import parse_line


def part_1(rule_set: 'RuleSet', my_bag_color='shiny gold') -> int:
    """
    Many rules (your puzzle input) are being enforced about bags and their contents; bags must be
    color-coded and must contain specific quantities of other color-coded bags. For example,
    consider the following rules:

        >>> rules = RuleSet.from_text('''
        ...     light red bags contain 1 bright white bag, 2 muted yellow bags.
        ...     dark orange bags contain 3 bright white bags, 4 muted yellow bags.
        ...     bright white bags contain 1 shiny gold bag.
        ...     muted yellow bags contain 2 shiny gold bags, 9 faded blue bags.
        ...     shiny gold bags contain 1 dark olive bag, 2 vibrant plum bags.
        ...     dark olive bags contain 3 faded blue bags, 4 dotted black bags.
        ...     vibrant plum bags contain 5 faded blue bags, 6 dotted black bags.
        ...     faded blue bags contain no other bags.
        ...     dotted black bags contain no other bags.
        ... ''')

    These rules specify the required contents for 9 bag types.

        >>> len(rules)
        9

    In this example, every `faded blue` bag is empty, ...

        >>> rules.contains_count('faded blue')
        0

    ... every `vibrant plum` bag contains 11 bags (5 `faded blue` and 6 `dotted black`), ...

        >>> rules.contains_count('vibrant plum')
        11
        >>> rules.contains['vibrant plum']
        [(5, 'faded blue'), (6, 'dotted black')]

    ... and so on.


    You have a *`shiny gold`* bag. If you wanted to carry it in at least one other bag, how many
    different bag colors would be valid for the outermost bag? (In other words: how many colors
    can, eventually, contain at least one `shiny gold` bag?)

    In the above rules, the following options would be available to you:

        - A `bright white` bag, which can hold your `shiny gold` bag directly.
        - A `muted yellow` bag, which can hold your `shiny gold` bag directly + some other bags.

            >>> sorted(rules.colors_outside_of('shiny gold', recursive=False))
            ['bright white', 'muted yellow']

        - A `dark orange` bag, which can hold `bright white` and `muted yellow` bags, either of
          which could then hold your `shiny gold` bag.
        - A `light red` bag, which can hold `bright white` and `muted yellow` bags, either of which
          could then hold your `shiny gold` bag.

            >>> sorted(rules.colors_outside_of('shiny gold', recursive=True))
            ['bright white', 'dark orange', 'light red', 'muted yellow']

    So, in this example, the number of bag colors that can eventually contain at least one
    `shiny gold` bag is 4.

        >>> part_1(rules)
        part 1: 4 bag colors can contain at least one 'shiny gold' bag
        4

    *How many bag colors can eventually contain at least one `shiny gold` bag?*
    """

    result = len(rule_set.colors_outside_of(my_bag_color))

    print(f"part 1: {result} bag colors can contain at least one {my_bag_color!r} bag")
    return result


def part_2(rule_set: 'RuleSet', my_bag_color: str = 'shiny gold') -> int:
    """
    Consider again your `shiny gold` bag and the rules from the above example:

        >>> rules = RuleSet.from_file('data/07-example.txt')

        - both `faded blue` and `dotted black` bags contain 0 other bags.

            >>> rules.contains_count('faded blue')
            0
            >>> rules.contains_count('dotted black')
            0

        - `vibrant plum` bags contain 11 other bags: 5 faded `blue bags` and 6 `dotted black` bags.

            >>> rules.contains_count('vibrant plum')
            11
            >>> rules.contains['vibrant plum']
            [(5, 'faded blue'), (6, 'dotted black')]

        - `dark olive` bags contain 7 other bags: 3 `faded blue` bags and 4 `dotted black` bags.

            >>> rules.contains_count('dark olive')
            7
            >>> rules.contains['dark olive']
            [(3, 'faded blue'), (4, 'dotted black')]

    So, a single `shiny gold` bag must contain 1 `dark olive` bag (and the 7 bags within it)
    plus 2 `vibrant plum` bags (and the 11 bags within each of those):
    `1 + 1*7 + 2 + 2*11` = *32 bags*!

        >>> rules.contains_count('shiny gold', recursive=True)
        32

    Of course, the actual rules have a small chance of going several levels deeper than this
    example; be sure to count all of the bags, even if the nesting becomes topologically
    impractical!

    Here's another example:

        >>> rules_2 = RuleSet.from_text('''
        ...     shiny gold bags contain 2 dark red bags.
        ...     dark red bags contain 2 dark orange bags.
        ...     dark orange bags contain 2 dark yellow bags.
        ...     dark yellow bags contain 2 dark green bags.
        ...     dark green bags contain 2 dark blue bags.
        ...     dark blue bags contain 2 dark violet bags.
        ...     dark violet bags contain no other bags.
        ... ''')
        >>> len(rules_2)
        7

    In this example, a single `shiny gold` bag must contain *126* other bags.

        >>> part_2(rules_2)
        part 2: 126 bags are contained within a single 'shiny gold' bag
        126

    *How many individual bags are required inside your single `shiny gold` bag?*
    """

    result = rule_set.contains_count(my_bag_color)

    print(f"part 2: {result} bags are contained within a single {my_bag_color!r} bag")
    return result


CountColor = tuple[int, str]
Rule = tuple[str, list[CountColor]]


class RuleSet:
    def __init__(self, rules: Iterable[Rule]):
        # color -> contents
        self.contains: dict[str, list[CountColor]] = dict(rules)

        # color -> outer colors
        self.contained_in: dict[str, set[str]] = dgroupby_pairs_set(
            (inner_color, outer_color)
            for outer_color, contents in self.contains.items()
            for _, inner_color in contents
        )

    @classmethod
    def from_text(cls, text: str):
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_file(cls, fn: str):
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_lines(cls, lines: Iterable[str]):
        return cls(
            parse_rule(line.strip())
            for line in lines
        )

    @lru_cache(maxsize=1024)
    def contains_count(self, outer_color: str, recursive: bool = True) -> int:
        immediate_count = sum(count for count, _ in self.contains[outer_color])
        if not recursive:
            return immediate_count

        return immediate_count + sum(
            count * self.contains_count(inner_color)
            for count, inner_color in self.contains[outer_color]
        )

    @lru_cache(maxsize=1024)
    def colors_outside_of(self, inner_color: str, recursive: bool = True) -> set[str]:
        immediate_colors = self.contained_in[inner_color]
        if not recursive:
            return immediate_colors

        return immediate_colors.union(*(
            self.colors_outside_of(outer_color)
            for outer_color in immediate_colors
            if outer_color in self.contained_in
        ))

    def __len__(self):
        return len(self.contains)

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.contains == other.contains

    def __hash__(self):
        return id(self)


def parse_count_color(text: str) -> tuple[int, str]:
    """
    >>> parse_count_color("1 bright white bag")
    (1, 'bright white')
    >>> parse_count_color("2 muted yellow bags")
    (2, 'muted yellow')
    """

    count, col_1, col_2, bag = text.split(" ")
    assert bag in ("bag", "bags")
    return int(count), f"{col_1} {col_2}"


def parse_rule(text: str) -> Rule:
    """
    >>> parse_rule("light red bags contain 1 bright white bag, 2 muted yellow bags.")
    ('light red', [(1, 'bright white'), (2, 'muted yellow')])
    >>> parse_rule("bright white bags contain 1 shiny gold bag.")
    ('bright white', [(1, 'shiny gold')])
    >>> parse_rule("faded blue bags contain no other bags.")
    ('faded blue', [])
    """

    color, inside_text = parse_line(text.strip(), "$ bags contain $.")

    if inside_text != "no other bags":
        inside = [
            parse_count_color(part)
            for part in inside_text.split(", ")
        ]
    else:
        inside = []

    return color, inside


def main(fn: str = 'data/07-input.txt') -> tuple[int, int]:
    rules = RuleSet.from_file(fn)
    assert len(rules) == 594

    result_1 = part_1(rules)
    result_2 = part_2(rules)
    return result_1, result_2


if __name__ == '__main__':
    main()
