"""
Advent of Code 2020
Day 19: Monster Messages
https://adventofcode.com/2020/day/19
"""

from abc import ABC
from abc import abstractmethod
from functools import cached_property
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

from utils import line_groups
from utils import parse_line
from utils import single_value


def part_1(rules: Dict[int, 'Rule'], messages: List[str]) -> int:
    """
    ... many of the messages sent back from the satellite have been corrupted.

    They sent you a list of *rules valid messages should obey* and a list of *received messages*
    they've collected so far (your puzzle input).

    The *rules for valid messages* (the top part of your puzzle input) are numbered and build upon
    each other. For example:

        >>> rs = rules_from_text('''
        ...
        ...     0: 1 2
        ...     1: "a"
        ...     2: 1 3 | 3 1
        ...     3: "b"
        ...
        ... ''')
        >>> len(rs)
        4

    Some rules, like `3: "b"`, simply match a single character (in this case, `b`).

        >>> rs[3]
        RuleText(3, 'b')
        >>> rs[3].match('b')
        True
        >>> rs[3].match('a')
        False
        >>> rs[3].match('bb')
        False

    The remaining rules list the sub-rules that must be followed; for example, the rule `0: 1 2`
    means that to match rule `0`, the text being checked must match rule `1`, and the text after
    the part that matched rule `1` must then match rule `2`.

        >>> rs[0]  # doctest: +ELLIPSIS
        RuleGroups(0, [[RuleText(1, 'a'), RuleGroups(2, ...)]])

    Some of the rules have multiple lists of sub-rules separated by a pipe (`|`). This means that
    *at least one* list of sub-rules must match. (The ones that match might be different each time
    the rule is encountered.) For example, the rule `2: 1 3 | 3 1` means that to match rule `2`,
    the text being checked must match rule `1` followed by rule `3` *or* it must match rule `3`
    followed by rule `1`.

        >>> rs[2]
        RuleGroups(2, [[RuleText(1, 'a'), RuleText(3, 'b')], [RuleText(3, 'b'), RuleText(1, 'a')]])

    Fortunately, there are no loops in the rules, so the list of possible matches will be finite.
    Since rule `1` matches `a` and rule `3` matches `b`, rule `2` matches either `ab` or `ba`.

        >>> rs[2].pattern
        '(ab|ba)'
        >>> rs[2].match_count(['ab', 'ba'])
        2
        >>> rs[2].match_count(['aa', 'bb', 'aaa', 'b'])
        0

    Therefore, rule `0` matches `aab` or `aba`.

        >>> rs[0].pattern
        'a(ab|ba)'
        >>> rs[0].match_count(['aab', 'aba'])
        2
        >>> rs[0].match_count(['aaa', 'abb', 'bab', 'ab'])
        0

    Here's a more interesting example:

        >>> rs = rules_from_text('''
        ...
        ...     0: 4 1 5
        ...     1: 2 3 | 3 2
        ...     2: 4 4 | 5 5
        ...     3: 4 5 | 5 4
        ...     4: "a"
        ...     5: "b"
        ...
        ... ''')
        >>> len(rs)
        6

    Here, because rule `4` matches `a` and rule `5` matches `b`, ...


        >>> rs[4].pattern
        'a'
        >>> rs[5].pattern
        'b'

    ... rule `2` matches two letters that are the same (`aa` or `bb`), ...

        >>> rs[2].pattern
        '(aa|bb)'
        >>> rs[2].match_count(['aa', 'bb'])
        2
        >>> rs[2].match_count(['ab', 'ba', 'aaa', 'bbb', 'a', 'b'])
        0

    ... and rule `3` matches two letters that are different (`ab` or `ba`).

        >>> rs[3].pattern
        '(ab|ba)'
        >>> rs[3].match_count(['ab', 'ba'])
        2
        >>> rs[3].match_count(['aa', 'bb', 'aaa', 'bba', 'a', 'b'])
        0

    Since rule `1` matches rules `2` and `3` once each in either order, it must match two pairs of
    letters, one pair with matching letters and one pair with different letters. This leaves eight
    possibilities:

        >>> rs[1].pattern
        '((aa|bb)(ab|ba)|(ab|ba)(aa|bb))'
        >>> rs[1].match_count(['aaab', 'aaba', 'bbab', 'bbba', 'abaa', 'abbb', 'baaa', 'babb'])
        8
        >>> rs[1].match_count(['aaaa', 'bbbb', 'abab', 'baab', 'bbaa', 'aabb'])
        0

    Rule `0`, therefore, matches `a` (rule `4`), then any of the eight options from rule `1`,
    then `b` (rule `5`):

        >>> rs[0].pattern
        'a((aa|bb)(ab|ba)|(ab|ba)(aa|bb))b'
        >>> rs[0].match_count(['aaaabb', 'aaabab', 'abbabb', 'abbbab', 'aabaab', 'aabbbb',
        ... 'abaaab', 'ababbb'])
        8
        >>> rs[0].match_count(['aaaaba', 'bababa', 'ababab', 'aabab', 'aaaabbb'])
        0

    The *received messages* (the bottom part of your puzzle input) need to be checked against the
    rules so you can determine which are valid and which are corrupted. Including the rules and the
    messages together, this might look like:

        >>> rs, ms = input_from_text('''
        ...
        ...     0: 4 1 5
        ...     1: 2 3 | 3 2
        ...     2: 4 4 | 5 5
        ...     3: 4 5 | 5 4
        ...     4: "a"
        ...     5: "b"
        ...
        ...     ababbb
        ...     bababa
        ...     abbbab
        ...     aaabbb
        ...     aaaabbb
        ...
        ... ''')
        >>> len(rs), len(ms)
        (6, 5)

    Your goal is to determine *the number of messages that completely match rule `0`*. In the above
    example, `ababbb` and `abbbab` match, but `bababa`, `aaabbb`, and `aaaabbb` do not, producing
    the answer *`2`*.

        >>> rs[0].match_count(ms)
        2

    The whole message must match all of rule `0`; there can't be extra unmatched characters in the
    message. (For example, `aaaabbb` might appear to match rule `0` above, but it has an extra
    unmatched `b` on the end.)

    *How many messages completely match rule 0?*

        >>> part_1(rs, ms)
        part 1: out of 5 messages, rules match 2
        2
    """

    result = rules[0].match_count(messages)

    print(f"part 1: out of {len(messages)} messages, rules match {result}")
    return result


def part_2(rules: Dict[int, 'Rule'], messages: List[str]) -> int:
    r"""
    As you look over the list of messages, you realize your matching rules aren't quite right.
    To fix them, completely replace rules `8: 42` and `11: 42 31` with the following:

        ```
        8: 42 | 42 8
        11: 42 31 | 42 11 31
        ```

    This small change has a big impact: now, the rules *do* contain loops, and the list of messages
    they could hypothetically match is infinite. You'll need to determine how these changes affect
    which messages are valid.

    Fortunately, many of the rules are unaffected by this change; it might help to start by looking
    at which rules always match the same set of values and how those rules (especially rules `42`
    and `31`) are used by the new versions of rules `8` and `11`.

    For example:

        >>> rs, ms = input_from_text('''
        ...
        ...     42: 9 14 | 10 1
        ...     9: 14 27 | 1 26
        ...     10: 23 14 | 28 1
        ...     1: "a"
        ...     11: 42 31
        ...     5: 1 14 | 15 1
        ...     19: 14 1 | 14 14
        ...     12: 24 14 | 19 1
        ...     16: 15 1 | 14 14
        ...     31: 14 17 | 1 13
        ...     6: 14 14 | 1 14
        ...     2: 1 24 | 14 4
        ...     0: 8 11
        ...     13: 14 3 | 1 12
        ...     15: 1 | 14
        ...     17: 14 2 | 1 7
        ...     23: 25 1 | 22 14
        ...     28: 16 1
        ...     4: 1 1
        ...     20: 14 14 | 1 15
        ...     3: 5 14 | 16 1
        ...     27: 1 6 | 14 18
        ...     14: "b"
        ...     21: 14 1 | 1 14
        ...     25: 1 1 | 1 14
        ...     22: 14 14
        ...     8: 42
        ...     26: 14 22 | 1 20
        ...     18: 15 15
        ...     7: 14 5 | 1 21
        ...     24: 14 1
        ...
        ...     abbbbbabbbaaaababbaabbbbabababbbabbbbbbabaaaa
        ...     bbabbbbaabaabba
        ...     babbbbaabbbbbabbbbbbaabaaabaaa
        ...     aaabbbbbbaaaabaababaabababbabaaabbababababaaa
        ...     bbbbbbbaaaabbbbaaabbabaaa
        ...     bbbababbbbaaaaaaaabbababaaababaabab
        ...     ababaaaaaabaaab
        ...     ababaaaaabbbaba
        ...     baabbaaaabbaaaababbaababb
        ...     abbbbabbbbaaaababbbbbbaaaababb
        ...     aaaaabbaabaaaaababaa
        ...     aaaabbaaaabbaaa
        ...     aaaabbaabbaaaaaaabbbabbbaaabbaabaaa
        ...     babaaabbbaaabaababbaabababaaab
        ...     aabbbbbaabbbaaaaaabbbbbababaaaaabbaaabba
        ...
        ... ''')
        >>> len(rs), len(ms)
        (31, 15)
        >>> print(rs[0])
        0: 8 11
        >>> print(rs[8])
        8: 42
        >>> print(rs[11])
        11: 42 31

    Without updating rules `8` and `11`, these rules only match three messages:

        >>> list(rs[0].filter(ms))
        ['bbabbbbaabaabba', 'ababaaaaaabaaab', 'ababaaaaabbbaba']

    However, after updating rules `8` and `11`, ...

        >>> patched = Rule0.patch(rs)
        >>> len(patched)
        29
        >>> print(patched[0])
        0: 8 11
        8: 42 | 42 8
        11: 42 31 | 42 11 31
        >>> patched[0] is rs[0]
        False

    ... a total of *12* messages match:

        >>> print("\n".join(patched[0].filter(ms)))
        bbabbbbaabaabba
        babbbbaabbbbbabbbbbbaabaaabaaa
        aaabbbbbbaaaabaababaabababbabaaabbababababaaa
        bbbbbbbaaaabbbbaaabbabaaa
        bbbababbbbaaaaaaaabbababaaababaabab
        ababaaaaaabaaab
        ababaaaaabbbaba
        baabbaaaabbaaaababbaababb
        abbbbabbbbaaaababbbbbbaaaababb
        aaaaabbaabaaaaababaa
        aaaabbaabbaaaaaaabbbabbbaaabbaabaaa
        aabbbbbaabbbaaaaaabbbbbababaaaaabbaaabba

    *After updating rules `8` and `11`, how many messages completely match rule `0`?*

        >>> part_2(rs, ms)
        part 2: out of 15 messages, patched rules match 12
        12
    """

    patched_rules = Rule0.patch(rules)
    result = patched_rules[0].match_count(messages)

    print(f"part 2: out of {len(messages)} messages, patched rules match {result}")
    return result


class Rule(ABC):
    def __init__(self, number: int):
        self.number = number

    @abstractmethod
    def __len__(self):
        pass

    @property
    @abstractmethod
    def pattern(self) -> str:
        pass

    def match(self, text: str) -> bool:
        return self._match_partial(text) == ""

    @abstractmethod
    def _match_partial(self, text: str) -> Optional[str]:
        pass

    def filter(self, texts: Iterable[str]) -> Iterable[str]:
        return (text for text in texts if self.match(text))

    def match_count(self, texts: Iterable[str]):
        return sum(1 for _ in self.filter(texts))


class RuleText(Rule):
    def __init__(self, number: int, text: str):
        super().__init__(number)
        self.text = text

    def __repr__(self):
        return f'{type(self).__name__}({self.number!r}, {self.text!r})'

    def __str__(self):
        return f'{self.number}: "{self.text}"'

    def __len__(self):
        return len(self.text)

    @property
    def pattern(self) -> str:
        return self.text

    def _match_partial(self, text: str) -> Optional[str]:
        if text.startswith(self.text):
            return text[len(self.text):]
        else:
            return None


class RuleGroups(Rule):
    def __init__(self, number: int, groups: Iterable[Iterable[Rule]]):
        super().__init__(number)
        self.groups = list(list(group) for group in groups)
        assert len(self.groups) > 0

    def __repr__(self):
        groups_repr = ", ".join(repr(group) for group in self.groups)
        return f'{type(self).__name__}({self.number!r}, [{groups_repr}])'

    def __str__(self):
        groups_str = " | ".join(
            " ".join(str(rule.number) for rule in group)
            for group in self.groups
        )
        return f'{self.number}: {groups_str}'

    def __len__(self):
        return single_value(set(
            sum(len(rule) for rule in group)
            for group in self.groups
        ))

    @cached_property
    def pattern(self) -> str:
        if len(self.groups) == 1:
            return ''.join(rule.pattern for rule in self.groups[0])
        else:
            return '(' + '|'.join(
                ''.join(rule.pattern for rule in group)
                for group in self.groups
            ) + ')'

    def _match_partial(self, text: str) -> Optional[str]:
        for group in self.groups:
            remainder = self._match_single_group(text, group)
            if remainder is not None:
                return remainder
        else:
            return None

    @staticmethod
    def _match_single_group(text: str, group: List[Rule]) -> Optional[str]:
        remainder = text
        for rule in group:
            remainder = rule._match_partial(remainder)
            if remainder is None:
                return None
        return remainder


class Rule0(Rule):
    def __init__(self, rule_42: RuleGroups, rule_31: RuleGroups):
        assert len(rule_42) == len(rule_31)
        super().__init__(number=0)
        self.rule_42 = rule_42
        self.rule_31 = rule_31

    def __repr__(self):
        return f'{type(self).__name__}({self.rule_42!r}, {self.rule_31!r})'

    def __str__(self):
        return "\n".join([
            "0: 8 11",
            "8: 42 | 42 8",
            "11: 42 31 | 42 11 31"
        ])

    def __len__(self):
        raise ValueError(f"{type(self).__name__} has no fixed length")

    def pattern(self) -> str:
        a, b = self.rule_42.pattern, self.rule_31.pattern
        return f"({a})+({a}){{x}}({b}){{x}}"

    def _match_partial(self, text: str) -> Optional[str]:
        raise ValueError(f"{type(self).__name__} cannot only do full matches")

    def match(self, text: str) -> bool:
        part_length = len(self.rule_42)  # == len(self.rule_31)

        if len(text) < 3 * part_length:
            return False
        if len(text) % part_length != 0:
            return False

        text_parts = [
            text[k:k+part_length]
            for k in range(0, len(text), part_length)
        ]

        matches_42 = 0
        for part in text_parts:
            if self.rule_42.match(part):
                matches_42 += 1
            else:
                break

        matches_31 = 0
        for part in reversed(text_parts):
            if self.rule_31.match(part):
                matches_31 += 1
            else:
                break

        return matches_42 + matches_31 >= len(text_parts) and matches_42 > matches_31 > 0

    @classmethod
    def patch(cls, rules: Dict[int, Rule]) -> Dict[int, Rule]:
        # 0: 8 11
        rule_0 = rules[0]
        assert rule_0.number == 0
        assert isinstance(rule_0, RuleGroups)
        assert len(rule_0.groups) == 1
        assert len(rule_0.groups[0]) == 2
        rule_8, rule_11 = rule_0.groups[0]

        # 8: 42
        # -> 42 | 42 8
        assert rule_8.number == 8
        assert isinstance(rule_8, RuleGroups)
        assert len(rule_8.groups) == 1
        assert len(rule_8.groups[0]) == 1
        rule_42 = rule_8.groups[0][0]

        # 11: 42 31
        # ->  42 31 | 42 11 31
        assert rule_11.number == 11
        assert isinstance(rule_11, RuleGroups)
        assert len(rule_11.groups) == 1
        assert len(rule_11.groups[0]) == 2
        assert rule_42 is rule_11.groups[0][0]
        rule_31 = rule_11.groups[0][1]

        assert isinstance(rule_42, RuleGroups)
        assert rule_42.number == 42
        assert isinstance(rule_31, RuleGroups)
        assert rule_31.number == 31

        patched_rules = dict(rules)
        del patched_rules[8]
        del patched_rules[11]
        patched_rules[0] = cls(rule_42=rule_42, rule_31=rule_31)

        return patched_rules


def rules_from_text(text: str) -> Dict[int, Rule]:
    return rules_from_lines(text.strip().split("\n"))


def rules_from_lines(lines: Iterable[str]) -> Dict[int, Rule]:
    rules: Dict[int, Rule] = dict()
    rule_refs: Dict[int, List[List[int]]] = dict()

    for line in lines:
        if '"' in line:
            # 1: "a"
            number, text = parse_line(line.strip(), '$: "$"')
            rule = RuleText(int(number), text)
            rules[rule.number] = rule

        else:
            # 2: 1 3
            # 6: 12
            # 8: 14 | 15
            # 10: 2 4 | 8 16
            number, rdef = parse_line(line.strip(), '$: $')
            rule_refs[int(number)] = [
                [int(v) for v in group_text.split(' ')]
                for group_text in rdef.split(' | ')
            ]

    while rule_refs:
        number, groups = next(
            (number, groups)
            for number, groups in rule_refs.items()
            if all(
                num in rules
                for group in groups
                for num in group
            )
        )
        referenced_rules = [
            [rules[num] for num in group]
            for group in groups
        ]
        rules[number] = RuleGroups(number, referenced_rules)
        del rule_refs[number]

    return rules


def input_from_file(fn: str) -> Tuple[Dict[int, Rule], List[str]]:
    return input_from_lines(open(fn))


def input_from_text(text: str) -> Tuple[Dict[int, Rule], List[str]]:
    return input_from_lines(text.strip().split("\n"))


def input_from_lines(lines: Iterable[str]) -> Tuple[Dict[int, Rule], List[str]]:
    rule_lines, messages = line_groups(lines)
    rules = rules_from_lines(rule_lines)
    return rules, messages


if __name__ == '__main__':
    rules_, messages_ = input_from_file("data/19-input.txt")
    assert len(rules_) == 130
    assert len(messages_) == 458

    part_1(rules_, messages_)
    part_2(rules_, messages_)
    # 337 too high
