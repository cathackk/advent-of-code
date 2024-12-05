"""
Advent of Code 2024
Day 5: Print Queue
https://adventofcode.com/2024/day/5
"""
import functools
from typing import Any, Iterable, Iterator

from common.file import relative_path
from common.iteration import zip1
from common.text import line_groups


def part_1(rules: 'Rules', updates: Iterable['Update']) -> int:
    """
    Satisfied with their search on Ceres, the squadron of scholars suggests subsequently scanning
    the stationery stacks of sub-basement 17.

    The North Pole printing department is busier than ever this close to Christmas, and while
    The Historians continue their search of this historically significant facility, an Elf operating
    a very familiar printer (y2017/day01_captcha.py) beckons you over.

    The Elf must recognize you, because they waste no time explaining that the new **sleigh launch
    safety manual** updates won't print correctly. Failure to update the safety manuals would be
    dire indeed, so you offer your services.

    Safety protocols clearly indicate that new pages for the safety manuals must be printed in
    a **very specific order**. The notation `X|Y` means that if both page number `X` and page number
    `Y` are to be produced as part of an update, page number `X` **must** be printed at some point
    before page number `Y`.

    The Elf has for you both the **page ordering rules** and the **pages to produce in each update**
    (your puzzle input), but can't figure out whether each update has the pages in the right order.

    For example:

        >>> example_rules, example_updates = input_from_text('''
        ...     47|53
        ...     97|13
        ...     97|61
        ...     97|47
        ...     75|29
        ...     61|13
        ...     75|53
        ...     29|13
        ...     97|29
        ...     53|29
        ...     61|53
        ...     97|53
        ...     61|29
        ...     47|13
        ...     75|47
        ...     97|75
        ...     47|61
        ...     75|61
        ...     47|29
        ...     75|13
        ...     53|13
        ...
        ...     75,47,61,53,29
        ...     97,61,53,29,13
        ...     75,29,13
        ...     75,97,47,61,53
        ...     61,13,29
        ...     97,13,75,29,47
        ... ''')

    The first section specifies the **page ordering rules**, one per line. The first rule, `47|53`,
    means that if an update includes both page number 47 and page number 53, then page number 47
    **must** be printed at some point before page number 53. (47 doesn't necessarily need to be
    **immediately** before 53; other pages are allowed to be between them.)

        >>> example_rules  # doctest: +ELLIPSIS
        [(47, 53), (97, 13), (97, 61), (97, 47), (75, 29), ...]
        >>> len(example_rules)
        21

    The second section specifies the page numbers of each **update**. Because most safety manuals
    are different, the pages needed in the updates are different too. The first update,
    `75,47,61,53,29`, means that the update consists of page numbers 75, 47, 61, 53, and 29.

        >>> example_updates  # doctest: +ELLIPSIS
        [[75, 47, 61, 53, 29], [97, 61, 53, 29, 13], [75, 29, 13], ...]
        >>> len(example_updates)
        6

    To get the printers going as soon as possible, start by identifying **which updates are already
    in the right order**.

    In the above example, the first update (`75,47,61,53,29`) is in the right order:

      - `75` is correctly first because there are rules that put each other page after it:

        >>> sorted((x, y) for x, y in example_rules if x == 75 and y in example_updates[0])
        [(75, 29), (75, 47), (75, 53), (75, 61)]

      - `47` is correctly second because `75` must be before it (see above) and every other page
        must be after it:

        >>> sorted((x, y) for x, y in example_rules if x == 47 and y in example_updates[0])
        [(47, 29), (47, 53), (47, 61)]

      - `61` is correctly in the middle because `75` and `47` are before it and others are after it:

        >>> sorted((x, y) for x, y in example_rules if x == 61 and y in example_updates[0])
        [(61, 29), (61, 53)]

      - `53` is correctly fourth because it is before page number `29`:

        >>> [(x, y) for x, y in example_rules if x == 53 and y in example_updates[0]]
        [(53, 29)]

      - `29` is the only page left and so is correctly last:

        >>> [(x, y) for x, y in example_rules if x == 29 and y in example_updates[0]]
        []

    Because the first update does not include some page numbers, the ordering rules involving those
    missing page numbers are ignored.

        >>> example_rules.is_ordered(example_updates[0])
        True

    The second and third updates are also in the correct order according to the rules. Like the
    first update, they also do not include every page number, and so only some of the ordering rules
    apply - within each update, the ordering rules that involve missing page numbers are not used.

        >>> example_rules.is_ordered(example_updates[1])
        True
        >>> example_rules.is_ordered(example_updates[2])
        True

    The fourth update is **not** in the correct order: it would print `75` before `97`, which
    violates the rule `97|75`:

        >>> example_updates[3]
        [75, 97, 47, 61, 53]
        >>> (97, 75) in example_rules
        True
        >>> example_rules.is_ordered(example_updates[3])
        False

    The fifth update is also **not** in the correct order, since it breaks the rule `29|13`:

        >>> example_updates[4]
        [61, 13, 29]
        >>> (29, 13) in example_rules
        True
        >>> example_rules.is_ordered(example_updates[4])
        False

    The last update is **not** in the correct order due to breaking several rules:

        >>> example_updates[5]
        [97, 13, 75, 29, 47]
        >>> example_rules.is_ordered(example_updates[5])
        False

    For some reason, the Elves also need to know the **middle page number** of each update being
    printed. Because you are currently only printing the correctly-ordered updates, you will need to
    find the middle page number of each correctly-ordered update. In the above example,
    the correctly-ordered updates are:

        >>> [update for update in example_updates if example_rules.is_ordered(update)]
        [[75, 47, 61, 53, 29], [97, 61, 53, 29, 13], [75, 29, 13]]

    These have middle page numbers of:

        >>> [middle_page(update) for update in _]
        [61, 53, 29]

    Adding these page numbers together gives:

        >>> sum(_)
        143

    Of course, you'll need to be careful: the actual list of **page ordering rules** is bigger and
    more complicated than the above example.

    Determine which updates are already in the correct order.
    **What do you get if you add up the middle page number from those correctly-ordered updates?**

        >>> part_1(example_rules, example_updates)
        part 1: there are 3 updates in correct order with sum of middle pages 143
        143
    """

    ordered_updates = [update for update in updates if rules.is_ordered(update)]
    result = sum(middle_page(update) for update in ordered_updates)

    print(
        f"part 1: "
        f"there are {len(ordered_updates)} updates in correct order "
        f"with sum of middle pages {result}"
    )
    return result


def part_2(rules: 'Rules', updates: Iterable['Update']) -> int:
    """
    While the Elves get to work printing the correctly-ordered updates, you have a little time to
    fix the rest of them.

    For each of the **incorrectly-ordered updates**, use the page ordering rules to put the page
    numbers in the right order. For the above example, here are the three incorrectly-ordered
    updates and their correct orderings:

        >>> example_rules, example_updates = input_from_file('data/05-example.txt')
        >>> unordered_updates = [up for up in example_updates if not example_rules.is_ordered(up)]
        >>> unordered_updates
        [[75, 97, 47, 61, 53], [61, 13, 29], [97, 13, 75, 29, 47]]
        >>> [sorted(up, key=example_rules) for up in unordered_updates]
        [[97, 75, 47, 61, 53], [61, 29, 13], [97, 75, 47, 29, 13]]

    After taking **only the incorrectly-ordered updates** and ordering them correctly, their middle
    page numbers are:

        >>> [middle_page(up) for up in _]
        [47, 29, 47]

    Adding these together produces:

        >>> sum(_)
        123

    Find the updates which are not in the correct order. **What do you get if you add up the middle
    page numbers after correctly ordering just those updates?**

        >>> part_2(example_rules, example_updates)
        part 2: there are 3 updates in incorrect order with sum of middle pages after ordering 123
        123
    """

    unordered_updates = [update for update in updates if not rules.is_ordered(update)]
    result = sum(middle_page(sorted(update, key=rules)) for update in unordered_updates)

    print(
        f"part 2: "
        f"there are {len(unordered_updates)} updates in incorrect order "
        f"with sum of middle pages after ordering {result}"
    )
    return result


Rule = tuple[int, int]
Update = list[int]


class Rules:
    def __init__(self, rules: Iterable[Rule]):
        self.rules = list(rules)
        self.rules_set = set(self.rules)
        self.key_func = functools.cmp_to_key(self.compare)

    def is_ordered(self, update: Update) -> bool:
        return all((x, y) in self for x, y in zip1(update))

    def compare(self, page_x: int, page_y: int) -> int:
        if (page_x, page_y) in self:
            return -1
        elif (page_y, page_x) in self:
            return +1
        else:
            raise ValueError(f"no rule to compare pages {page_x} and {page_y}")

    def __contains__(self, rule: Rule) -> bool:
        return rule in self.rules_set

    def __iter__(self) -> Iterator[Rule]:
        return iter(self.rules)

    def __call__(self, page: int) -> Any:
        return self.key_func(page)

    def __repr__(self) -> str:
        return repr(self.rules)

    def __len__(self) -> int:
        return len(self.rules)


def middle_page(update: Update) -> int:
    assert len(update) % 2 == 1
    return update[len(update) // 2]


def input_from_file(fn: str) -> tuple[Rules, list[Update]]:
    return input_from_lines(open(relative_path(__file__, fn)))


def input_from_text(text: str) -> tuple[Rules, list[Update]]:
    return input_from_lines(text.strip().splitlines())


def input_from_lines(lines: Iterable[str]) -> tuple[Rules, list[Update]]:
    rule_lines, update_lines = line_groups(lines)

    def parse_rule(line: str) -> Rule:
        x, y = line.split('|')
        return int(x), int(y)

    rules = Rules(parse_rule(line) for line in rule_lines)

    def parse_update(line: str) -> Update:
        return [int(val) for val in line.split(',')]

    updates = [parse_update(line) for line in update_lines]

    return rules, updates


def main(input_fn: str = 'data/05-input.txt') -> tuple[int, int]:
    rules, updates = input_from_file(input_fn)
    result_1 = part_1(rules, updates)
    result_2 = part_2(rules, updates)
    return result_1, result_2


if __name__ == '__main__':
    main()
