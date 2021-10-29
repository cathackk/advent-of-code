"""
Advent of Code 2020
Day 2: Password Philosophy
https://adventofcode.com/2020/day/2
"""

from typing import Iterable

from utils import parse_line


def part_1(rules_passwords: list[tuple['PasswordRule', str]]) -> int:
    """
    Suppose you have the following list:

        >>> data = data_from_text('''
        ...
        ...     1-3 a: abcde
        ...     1-3 b: cdefg
        ...     2-9 c: ccccccccc
        ...
        ... ''')
        >>> len(data)
        3

    Each line gives the password policy and then the password. The password policy indicates
    the lowest and highest number of times a given letter must appear for the password to be valid.
    For example, `1-3 a` means that the password must contain `a` at least 1 time and at most
    3 times.

    In the above example, 2 passwords are valid. The middle password, `cdefg`, is not;
    it contains no instances of `b`, but needs at least 1.

        >>> data[1]
        (PasswordRule(1, 3, 'b'), 'cdefg')
        >>> PasswordRule(1, 3, 'b').is_valid_1('cdefg')
        False

    The first and third passwords are valid: they contain one `a` or nine `c`, both within
    the limits of their respective policies.

        >>> data[0]
        (PasswordRule(1, 3, 'a'), 'abcde')
        >>> PasswordRule(1, 3, 'a').is_valid_1('abcde')
        True

        >>> data[2]
        (PasswordRule(2, 9, 'c'), 'ccccccccc')
        >>> PasswordRule(2, 9, 'c').is_valid_1('ccccccccc')
        True

    *How many passwords are valid according to their policies?*

        >>> part_1(data)
        part 1: 2/3 passwords are valid
        2
    """
    result = sum(1 for rule, password in rules_passwords if rule.is_valid_1(password))
    print(f"part 1: {result}/{len(rules_passwords)} passwords are valid")
    return result


def part_2(rules_passwords: list[tuple['PasswordRule', str]]) -> int:
    """
    Each policy actually describes two positions in the password, where 1 means the first
    character, 2 means the second character, and so on. *Exactly one* of these positions must
    contain the given letter. Other occurrences of the letter are irrelevant for the purposes
    of policy enforcement.

    Given the same example list from above:

    - `1-3 a: abcde` is *valid*: position 1 contains `a` and position 3 does not.

        >>> PasswordRule(1, 3, 'a').is_valid_2('abcde')
        True

    - `1-3 b: cdefg` is *invalid*: neither position 1 nor position 3 contains `b`.

        >>> PasswordRule(1, 3, 'b').is_valid_2('cdefg')
        False

    - `2-9 c: ccccccccc` is *invalid*: both position 2 and position 9 contain `c`.

        >>> PasswordRule(2, 9, 'c').is_valid_2('ccccccccc')
        False

    *How many passwords are valid according to the new interpretation of the policies?*

        >>> part_2([
        ...     (PasswordRule(1, 3, 'a'), 'abcde'),
        ...     (PasswordRule(1, 3, 'b'), 'cdefg'),
        ...     (PasswordRule(2, 9, 'c'), 'ccccccccc')
        ... ])
        part 2: 1/3 passwords are valid
        1
    """
    result = sum(1 for rule, password in rules_passwords if rule.is_valid_2(password))
    print(f"part 2: {result}/{len(rules_passwords)} passwords are valid")
    return result


class PasswordRule:
    def __init__(self, min_count: int, max_count: int, character: str):
        assert 1 <= min_count < max_count
        assert len(character) == 1

        self.min_count = min_count
        self.max_count = max_count
        self.character = character

    def is_valid_1(self, password: str) -> bool:
        """
        The lowest and highest number of times a given letter must appear
        for the password to be valid.

            >>> PasswordRule(2, 3, 'a').is_valid_1('a')
            False
            >>> PasswordRule(2, 3, 'a').is_valid_1('aa')
            True
            >>> PasswordRule(2, 3, 'a').is_valid_1('aaa')
            True
            >>> PasswordRule(2, 3, 'a').is_valid_1('aaaa')
            False
            >>> PasswordRule(2, 3, 'a').is_valid_1('bcd')
            False
        """
        ch_count = sum(1 for ch in password if ch == self.character)
        return self.min_count <= ch_count <= self.max_count

    def is_valid_2(self, password: str) -> bool:
        """
        Exactly one of these positions must contain the given letter.

            >>> PasswordRule(1, 4, 'a').is_valid_2('bbbb')
            False
            >>> PasswordRule(1, 4, 'a').is_valid_2('abbb')
            True
            >>> PasswordRule(1, 4, 'a').is_valid_2('bbba')
            True
            >>> PasswordRule(1, 4, 'a').is_valid_2('abba')
            False

            >>> PasswordRule(1, 4, 'x').is_valid_2('x')
            Traceback (most recent call last):
            ...
            AssertionError
        """
        pos1, pos2 = self.min_count - 1, self.max_count - 1
        assert 0 <= pos1 < pos2 < len(password)
        found_count = sum(1 for pos in (pos1, pos2) if password[pos] == self.character)
        return found_count == 1

    def __repr__(self):
        return f'{type(self).__name__}({self.min_count!r}, {self.max_count!r}, {self.character!r})'

    def __str__(self):
        return f"{self.min_count}-{self.max_count} {self.character}"


def data_from_file(fn: str) -> list[tuple[PasswordRule, str]]:
    return list(data_from_lines(open(fn)))


def data_from_text(text: str) -> list[tuple[PasswordRule, str]]:
    return list(data_from_lines(text.strip().split("\n")))


def data_from_lines(lines: Iterable[str]) -> Iterable[tuple[PasswordRule, str]]:
    for line in lines:
        # 1-3 b: cdefg
        min_count, max_count, character, password = parse_line(line.strip(), "$-$ $: $")
        yield PasswordRule(int(min_count), int(max_count), character), password


if __name__ == '__main__':
    data_ = data_from_file("data/02-input.txt")
    assert len(data_) == 1000

    part_1(data_)
    part_2(data_)
