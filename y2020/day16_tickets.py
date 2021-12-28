"""
Advent of Code 2020
Day 16: Ticket Translation
https://adventofcode.com/2020/day/16
"""

import math
from typing import Callable
from typing import Iterable

from common.utils import line_groups
from common.utils import parse_line
from common.utils import single_value


def part_1(rules: 'RuleList', nearby_tickets: list['Ticket']) -> int:
    """
    Unfortunately, you can't actually *read* the words on the ticket. You can, however, read the
    numbers, and so you figure out *the fields these tickets must have* and *the valid ranges* for
    values in those fields.

    You collect the *rules for ticket fields*, the *numbers on your ticket*, and the *numbers on
    other nearby tickets* for the same train service (via the airport security cameras) together
    into a single document you can reference (your puzzle input).

    The *rules for ticket fields* specify a list of fields that exist *somewhere* on the ticket and
    the *valid ranges of values* for each field. For example, a rule like `class: 1-3 or 5-7` means
    that one of the fields in every ticket is named `class` and can be any value in the ranges
    `1-3` or `5-7` (inclusive, such that `3` and `5` are both valid in this field, but `4` is not).

        >>> r = Rule.from_line('class: 1-3 or 5-7')
        >>> r
        Rule('class', (1, 3), (5, 7))
        >>> r.is_valid(3), r.is_valid(4), r.is_valid(5)
        (True, False, True)

    Each ticket is represented by a single line of comma-separated values. The values are the
    numbers on the ticket in the order they appear; every ticket has the same format. For example,
    consider this ticket:

        ```
        .--------------------------------------------------------.
        | ????: 101    ?????: 102   ??????????: 103     ???: 104 |
        |                                                        |
        | ??: 301  ??: 302             ???????: 303      ??????? |
        | ??: 401  ??: 402           ???? ????: 403    ????????? |
        '--------------------------------------------------------'
        ```

    Here, `?` represents text in a language you don't understand. This ticket might be represented
    as `101,102,103,104,301,302,303,401,402,403`; of course, the actual train tickets you're
    looking at are *much* more complicated. In any case, you've extracted just the numbers in such
    a way that the first number is always the same specific field, the second number is always a
    different specific field, and so on - you just don't know what each position actually means!

    Start by determining which tickets are *completely invalid*; these are tickets that contain
    values which *aren't valid for any field*. Ignore *your ticket* for now.

    For example, suppose you have the following notes:

        >>> rules, my_ticket, nearby_tickets = data_from_text('''
        ...
        ...     class: 1-3 or 5-7
        ...     row: 6-11 or 33-44
        ...     seat: 13-40 or 45-50
        ...
        ...     your ticket:
        ...     7,1,14
        ...
        ...     nearby tickets:
        ...     7,3,47
        ...     40,4,50
        ...     55,2,20
        ...     38,6,12
        ...
        ... ''')
        >>> len(rules), len(nearby_tickets)
        (3, 4)
        >>> rules[2]
        Rule('seat', (13, 40), (45, 50))
        >>> my_ticket
        [7, 1, 14]
        >>> nearby_tickets[3]
        [38, 6, 12]

    It doesn't matter which position corresponds to which field; you can identify invalid *nearby
    tickets* by considering only whether tickets contain *values that are not valid for any field*.
    In this example, the values on the first *nearby ticket* are all valid for at least one field.

        >>> rules.is_valid_ticket(nearby_tickets[0])
        True

    This is not true of the other three nearby tickets: the values `4`, `55`, and `12` are are not
    valid for any field.

        >>> [rules.is_valid_ticket(t) for t in nearby_tickets[1:]]
        [False, False, False]
        >>> list(rules.invalid_values(nearby_tickets))
        [4, 55, 12]

    Adding together all of the invalid values produces your ticket scanning error rate:

        >>> sum(_)
        71

    Consider the validity of the *nearby tickets* you scanned. *What is your ticket scanning error
    rate?*

        >>> part_1(rules, nearby_tickets)
        part 1: ticket scanning error rate is 71
        71
    """

    result = sum(rules.invalid_values(nearby_tickets))

    print(f"part 1: ticket scanning error rate is {result}")
    return result


def part_2(
        rules: 'RuleList',
        my_ticket: 'Ticket',
        nearby_tickets: list['Ticket'],
        consider_field: Callable[[str], bool] = lambda f: True
) -> int:
    """
    Now that you've identified which tickets contain invalid values, *discard those tickets
    entirely.* Use the remaining valid tickets to determine which field is which.

    Using the valid ranges for each field, determine what order the fields appear on the tickets.
    The order is consistent between all tickets: if `seat` is the third field, it is the third
    field on every ticket, including *your ticket*.

    For example, suppose you have the following notes:

        >>> rules, my_ticket, nearby_tickets = data_from_text('''
        ...
        ...     class: 0-1 or 4-19
        ...     row: 0-5 or 8-19
        ...     seat: 0-13 or 16-19
        ...
        ...     your ticket:
        ...     11,12,13
        ...
        ...     nearby tickets:
        ...     3,9,18
        ...     15,1,5
        ...     5,14,9
        ...
        ... ''')

    Based on the *nearby tickets* in the above example, the first position must be `row`, the
    second position must be `class`, and the third position must be `seat`.

        >>> fields = rules.determine_field_order([my_ticket] + nearby_tickets)
        >>> fields
        ['row', 'class', 'seat']

    You can conclude that in your ticket, `class` is `12`, `row` is `11`, and `seat` is `13`.

        >>> rules.describe_ticket(my_ticket, nearby_tickets)
        {'class': 12, 'row': 11, 'seat': 13}

    Once you work out which field is which, look for the six fields on *your ticket* that start
    with the word `departure`. *What do you get if you multiply those six values together?*

        >>> part_2(rules, my_ticket, nearby_tickets)
        part 2: values on your ticket:
            - class: 12
            - row: 11
            - seat: 13
        -> multiplying these values together gives 1716
        1716
    """

    my_ticket_described = rules.describe_ticket(my_ticket, nearby_tickets)

    considered_fields = {r.field for r in rules if consider_field(r.field)}
    assert len(considered_fields) > 0
    all_fields_considered = len(considered_fields) == len(rules)
    result = math.prod(my_ticket_described[f] for f in considered_fields)

    values_text = "values" if all_fields_considered else "selected values"
    print(f"part 2: {values_text} on your ticket:")
    for field, value in my_ticket_described.items():
        if field in considered_fields:
            print(f"    - {field}: {value}")

    print(f"-> multiplying these values together gives {result}")

    return result


Ticket = list[int]


class Rule:
    def __init__(self, field: str, *ranges: tuple[int, int]):
        assert len(ranges) > 0
        self.field = field
        self.ranges = ranges

    @classmethod
    def from_line(cls, text: str):
        # class: 1-3 or 5-7
        name, l1, h1, l2, h2 = parse_line(text, "$: $-$ or $-$")
        return cls(name, (int(l1), int(h1)), (int(l2), int(h2)))

    def __repr__(self):
        ranges_repr = ', '.join(repr(r) for r in self.ranges)
        return f'{type(self).__name__}({self.field!r}, {ranges_repr})'

    def __hash__(self):
        return hash((self.field, self.ranges))

    def is_valid(self, value: int) -> bool:
        return any(
            low <= value <= high
            for low, high in self.ranges
        )


class RuleList:
    def __init__(self, *rules: Rule):
        self.rules = rules

    @classmethod
    def from_lines(cls, lines: Iterable[str]):
        return cls(*(Rule.from_line(line) for line in lines))

    def __len__(self):
        return len(self.rules)

    def __getitem__(self, index):
        return self.rules[index]

    def __iter__(self):
        return iter(self.rules)

    def __repr__(self):
        rules_repr = ', '.join(repr(rule) for rule in self.rules)
        return f'{type(self).__name__}({rules_repr})'

    def is_valid_ticket(self, ticket: Ticket) -> bool:
        # each value is valid with at least one rule
        return all(
            any(rule.is_valid(value) for rule in self)
            for value in ticket
        )

    def invalid_values(self, tickets: Iterable[Ticket]) -> Iterable[int]:
        # return values that are not valid for any rule
        return (
            value
            for ticket in tickets
            for value in ticket
            if not any(rule.is_valid(value) for rule in self)
        )

    def determine_field_order(self, tickets: Iterable[Ticket]) -> list[str]:
        valid_tickets = [ticket for ticket in tickets if self.is_valid_ticket(ticket)]
        assert len(valid_tickets) > 0

        fields_count = single_value(set(len(ticket) for ticket in valid_tickets))
        assert fields_count == len(self)

        # gather all possible indexes
        possible_rule_indexes: dict[Rule, set[int]] = {
            rule: set(
                index
                for index in range(fields_count)
                if all(
                    rule.is_valid(ticket[index])
                    for ticket in valid_tickets
                )
            )
            for rule in self
        }

        # find the only possible permutation
        field_order: dict[int, str] = dict()
        while possible_rule_indexes:
            rule, index = next(
                (r, single_value(ixs))
                for r, ixs in possible_rule_indexes.items()
                if len(ixs) == 1
            )
            field_order[index] = rule.field
            del possible_rule_indexes[rule]
            for possible_indexes in possible_rule_indexes.values():
                possible_indexes.discard(index)

        return [field_order[ix] for ix in range(fields_count)]

    def describe_ticket(self, ticket: Ticket, other_tickets: list[Ticket]):
        # find out which column (index) is which field
        fields_ordered = self.determine_field_order([ticket] + other_tickets)
        # zip values from `ticket` with newly determined field names
        ticket_described = dict(zip(fields_ordered, ticket))
        # reorder the dict into rule order
        return {
            rule.field: ticket_described[rule.field]
            for rule in self
        }


def data_from_text(text: str) -> tuple[RuleList, Ticket, list[Ticket]]:
    return data_from_lines(text.strip().split("\n"))


def data_from_file(fn: str) -> tuple[RuleList, Ticket, list[Ticket]]:
    return data_from_lines(open(fn))


def data_from_lines(lines: Iterable[str]) -> tuple[RuleList, Ticket, list[Ticket]]:
    rule_lines, my_ticket_lines, nearby_ticket_lines = line_groups(lines)

    rules = RuleList.from_lines(rule_lines)

    assert len(my_ticket_lines) == 2
    assert my_ticket_lines[0] == "your ticket:"
    my_ticket = [int(v) for v in my_ticket_lines[1].split(",")]

    assert len(nearby_ticket_lines) > 0
    assert nearby_ticket_lines[0] == "nearby tickets:"
    nearby_tickets = [
        [int(v) for v in line.split(",")]
        for line in nearby_ticket_lines[1:]
    ]

    return rules, my_ticket, nearby_tickets


if __name__ == '__main__':
    rules_, my_ticket_, nearby_tickets_ = data_from_file('data/16-input.txt')
    assert len(rules_) == 20
    assert len(my_ticket_) == 20
    assert len(nearby_tickets_) == 240

    part_1(rules_, nearby_tickets_)
    part_2(rules_, my_ticket_, nearby_tickets_, consider_field=lambda f: f.startswith("departure"))
