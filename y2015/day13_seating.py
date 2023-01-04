"""
Advent of Code 2015
Day 13: Knights of the Dinner Table
https://adventofcode.com/2015/day/13
"""

from itertools import permutations
from typing import Iterable

from common.iteration import slidingw
from common.iteration import zip1
from common.text import parse_line
from meta.aoc_tools import data_path

Rule = tuple[tuple[str, str], int]
Rules = dict[tuple[str, str], int]


def part_1(rules: Rules) -> int:
    """
    In years past, the holiday feast with your family hasn't gone so well. Not everyone gets along!
    This year, you resolve, will be different. You're going to find the **optimal seating
    arrangement** and avoid all those awkward conversations.

    You start by writing up a list of everyone invited and the amount their happiness would increase
    or decrease if they were to find themselves sitting next to each other person. You have a circu-
    lar table that will be just big enough to fit everyone comfortably, and so each person will have
    exactly two neighbors.

    For example, suppose you have only four attendees planned, and you calculate their potential
    happiness as follows:

        >>> example_rules = rules_from_text('''
        ...     Alice would gain 54 happiness units by sitting next to Bob.
        ...     Alice would lose 79 happiness units by sitting next to Carol.
        ...     Alice would lose 2 happiness units by sitting next to David.
        ...     Bob would gain 83 happiness units by sitting next to Alice.
        ...     Bob would lose 7 happiness units by sitting next to Carol.
        ...     Bob would lose 63 happiness units by sitting next to David.
        ...     Carol would lose 62 happiness units by sitting next to Alice.
        ...     Carol would gain 60 happiness units by sitting next to Bob.
        ...     Carol would gain 55 happiness units by sitting next to David.
        ...     David would gain 46 happiness units by sitting next to Alice.
        ...     David would lose 7 happiness units by sitting next to Bob.
        ...     David would gain 41 happiness units by sitting next to Carol.
        ... ''')
        >>> example_rules['Alice', 'Bob']
        54
        >>> example_rules['Bob', 'Alice']
        83

    Then, if you seat Alice next to David, Alice would lose `2` happiness units (because David talks
    so much), but David would gain `46` happiness units (because Alice is such a good listener), for
    a total change of `44`.

    If you continue around the table, you could then seat Bob next to Alice (Bob gains `83`, Alice
    gains `54`). Finally, seat Carol, who sits next to Bob (Carol gains `60`, Bob loses `7`) and
    David (Carol gains `55`, David gains `41`). The arrangement looks like this:

        >>> example_arrangement = ['Alice', 'Bob', 'Carol', 'David']
        >>> draw_arrangement(example_arrangement, example_rules)
         -2 Alice +54
        +83 Bob    -7
        +60 Carol +55
        +41 David +46

    After trying every other seating arrangement in this hypothetical scenario, you find that this
    one is the most optimal, with a total change in happiness of `330`.

        >>> arrangement_happiness(example_arrangement, example_rules)
        330

    What is the **total change in happiness** for the optimal seating arrangement of the actual
    guest list?

        >>> part_1(example_rules)
        part 1: optimal arrangement brings 330 happiness
        330
    """

    happiness, _ = max(generate_arrangements(rules))
    print(f"part 1: optimal arrangement brings {happiness} happiness")
    return happiness


def part_2(rules: Rules) -> int:
    """
    In all the commotion, you realize that you forgot to seat yourself. At this point, you're pretty
    apathetic toward the whole thing, and your happiness wouldn't really go up or down regardless of
    who you sit next to. You assume everyone else would be just as ambivalent about sitting next to
    you, too.

    So, add yourself to the list, and give all happiness relationships that involve you a score `0`.

    What is the **total change in happiness** for the optimal seating arrangement that actually
    includes yourself?

        >>> part_2(rules_from_file(data_path(__file__, 'example.txt')))
        part 2: optimal arrangement (including myself) brings 286 happiness
        286
    """

    rules_with_myself = add_myself(rules)
    happiness, _ = max(generate_arrangements(rules_with_myself))
    print(f"part 2: optimal arrangement (including myself) brings {happiness} happiness")
    return happiness


def draw_arrangement(arrangement: list[str], rules: Rules) -> None:
    assert len(arrangement) > 1

    seats = arrangement[-1:] + arrangement[:-1]
    for neighbor_1, seat, neighbor_2 in slidingw(seats, 3, wrap=True):
        happines_1 = rules[seat, neighbor_1]
        happines_2 = rules[seat, neighbor_2]
        print(f"{happines_1:+3} {seat:5} {happines_2:+3}")


def arrangement_happiness(arrangement: list[str], rules: Rules) -> int:
    return sum(
        rules[p1, p2] + rules[p2, p1]
        for p1, p2 in zip1(arrangement, wrap=True)
    )


def generate_arrangements(rules: Rules) -> Iterable[tuple[int, list[str]]]:
    people = sorted(set(p for ps in rules.keys() for p in ps))
    assert len(people) > 1
    first_person = people[0]

    for rest_permutation in permutations(people[1:]):
        arrangement = [first_person] + list(rest_permutation)
        happiness = arrangement_happiness(arrangement, rules)
        yield happiness, arrangement


def add_myself(rules: Rules) -> Rules:
    people = sorted(set(p for ps in rules.keys() for p in ps))
    rules_extended = dict(rules)
    for person in people:
        rules_extended[person, 'myself'] = 0
        rules_extended['myself', person] = 0
    return rules_extended


def rules_from_file(fn: str) -> Rules:
    return dict(rulelist_from_lines(open(fn)))


def rules_from_text(text: str) -> Rules:
    return dict(rulelist_from_lines(text.strip().splitlines()))


def rulelist_from_lines(lines: Iterable[str]) -> Iterable[Rule]:
    return (rule_from_str(line.strip()) for line in lines)


def rule_from_str(line: str) -> Rule:
    # 'Alice would gain 54 happiness units by sitting next to Bob.'
    # 'Alice would lose 79 happiness units by sitting next to Carol.'
    name1, verb, amount_str, name2 = parse_line(
        line,
        pattern="$ would $ $ happiness units by sitting next to $."
    )

    amount = int(amount_str)
    assert verb in ("lose", "gain")
    if verb == "lose":
        amount = -amount

    return (name1, name2), amount


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    rules = rules_from_file(input_path)
    result_1 = part_1(rules)
    result_2 = part_2(rules)
    return result_1, result_2


if __name__ == '__main__':
    main()
