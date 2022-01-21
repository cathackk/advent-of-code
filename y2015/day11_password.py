"""
Advent of Code 2015
Day 11: Corporate Policy
https://adventofcode.com/2015/day/11
"""

import string
from typing import Iterable
from typing import Iterator

from common.file import relative_path


def part_1(last_password: str) -> str:
    """
    Santa's previous password expired, and he needs help choosing a new one.

    To help him remember his new password after the old one expires, Santa has devised a method of
    coming up with a password based on the previous one. Corporate policy dictates that passwords
    must be **exactly eight lowercase letters** (for security reasons), so he finds his new password
    by **incrementing** his old password string repeatedly until it is valid.

    Incrementing is just like counting with numbers: `xx`, `xy`, `xz`, `ya`, `yb`, and so on.
    Increase the rightmost letter one step; if it was `z`, it wraps around to `a`, and repeat with
    the next letter to the left until one doesn't wrap around.

        >>> next_str('xx')
        'xy'
        >>> next_str('xy')
        'xz'
        >>> next_str('xz')
        'ya'
        >>> next_str('ya')
        'yb'

    Unfortunately for Santa, a new Security-Elf recently started, and he has imposed some additional
    password requirements:

      - Passwords must include one increasing straight of at least three letters, like `abc`, `bcd`,
        `cde`, and so on, up to `xyz`. They cannot skip letters; `abd` doesn't count.
      - Passwords may not contain the letters `i`, `o`, or `l`, as these letters can be mistaken for
        other characters and are therefore confusing.
      - Passwords must contain at least two different, non-overlapping pairs of letters, like `aa`,
        `bb`, or `zz`.

    For example:

      - `hijklmmn` meets the first requirement (because it contains the straight `hij`) but fails
        the second requirement requirement (because it contains `i` and `l`):

        >>> is_valid('hijklmmn')
        False

      - `abbceffg` meets the third requirement (because it repeats `bb` and `ff`) but fails the
        first requirement:

        >>> is_valid('abbceffg')
        False

      - `abbcegjk` fails the third requirement, because it only has one double letter (`bb`):

        >>> is_valid('abbcegjk')
        False

      - The next password after `abcdefgh` is `abcdffaa`:

        >>> next_password('abcdefgh')
        'abcdffaa'

      - The next password after `ghijklmn` is `ghjaabcc`, because you eventually skip all the
        passwords that start with `ghi...`, since `i` is not allowed:

        >>> next_password('ghijklmn')
        'ghjaabcc'

    Given Santa's current password (your puzzle input), what should his next password be?

        >>> part_1('abcdefgh')
        part 1: Santa's new password is 'abcdffaa'
        'abcdffaa'
    """

    result = next_password(last_password)
    print(f"part 1: Santa's new password is {result!r}")
    return result


def part_2(last_password: str) -> str:
    """
    Santa's password expired again. **What's the next one?**

        >>> part_2('abcdffaa')
        part 2: Santa's next password is 'abcdffbb'
        'abcdffbb'
    """

    result = next_password(last_password)
    print(f"part 2: Santa's next password is {result!r}")
    return result


BANNED_CHARS = 'iol'
VALID_CHARS_SET = set(string.ascii_lowercase) - set(BANNED_CHARS)
VALID_CHARS = ''.join(sorted(VALID_CHARS_SET))
VALID_CHARS_ORD = {c: i for i, c in enumerate(VALID_CHARS)}

TRIPLES = [
    triple
    for k in range(len(string.ascii_lowercase) - 2)
    if set(triple := string.ascii_lowercase[k:k+3]).issubset(VALID_CHARS)
]


def is_valid(pwd: str) -> bool:
    assert len(pwd) == 8
    return (
        all(c in VALID_CHARS for c in pwd)
        and any(triple in pwd for triple in TRIPLES)
        and len(set(pairs(pwd))) >= 2
    )


def pairs(line: str) -> Iterable[str]:
    """
        >>> list(pairs('abcddabbc'))
        ['dd', 'bb']
        >>> list(pairs('aaaaabbbaa'))
        ['aa', 'aa', 'bb', 'aa']
    """
    last_pair_k = None
    for k in range(len(line) - 1):
        if line[k] == line[k + 1]:
            if last_pair_k is None or last_pair_k < k - 1:
                yield line[k:k + 2]
                last_pair_k = k


def next_str(line: str) -> str:
    """
        >>> next_str('abc')
        'abd'
        >>> next_str('xxxx')
        'xxxy'
        >>> next_str('xyz')
        'xza'
        >>> next_str('z')
        'a'
        >>> next_str('h')
        'j'
        >>> next_str('n')
        'p'
        >>> next_str('k')
        'm'
    """
    if not line:
        return line

    first_invalid_char_index = next(
        (i for i, c in enumerate(line) if c not in VALID_CHARS_SET),
        None
    )
    if first_invalid_char_index is not None:
        valid_prefix = line[:first_invalid_char_index]
        invalid_char = line[first_invalid_char_index]
        valid_char = chr(ord(invalid_char) + 1)
        assert valid_char in VALID_CHARS
        padding_suffix = VALID_CHARS[0] * (len(line) - len(valid_prefix) - 1)
        return valid_prefix + valid_char + padding_suffix

    if line[-1] == VALID_CHARS[-1]:
        return next_str(line[:-1]) + VALID_CHARS[0]

    return line[:-1] + VALID_CHARS[VALID_CHARS_ORD[line[-1]] + 1]


def valid_passwords(start: str) -> Iterator[str]:
    pwd = start
    while True:
        pwd = next_str(pwd)
        if is_valid(pwd):
            yield pwd


def next_password(pwd: str) -> str:
    return next(valid_passwords(pwd))


def password_from_file(fn: str) -> str:
    return open(relative_path(__file__, fn)).readline().strip()


if __name__ == '__main__':
    last_password_ = password_from_file('data/11-input.txt')
    new_password_ = part_1(last_password_)
    part_2(new_password_)
