"""
Advent of Code 2016
Day 5: How About a Nice Game of Chess?
https://adventofcode.com/2016/day/5
"""

from functools import lru_cache
from itertools import count
from typing import Iterable

from tqdm import tqdm

from common.file import relative_path
from common.md5 import md5


def part_1(door_id: str) -> str:
    """
    You are faced with a security door designed by Easter Bunny engineers that seem to have acquired
    most of their security knowledge by watching hacking movies.

    The **eight-character password** for the door is generated one character at a time by finding
    the MD5 hash of some Door ID (your puzzle input) and an increasing integer index (starting with
    `0`).

    A hash indicates the **next character** in the password if its hexadecimal representation starts
    with **five zeroes**. If it does, the sixth character in the hash is the next character of
    the password.

    For example, if the Door ID is `abc`:

      - The first index which produces a hash that starts with five zeroes is `3231929`, which we
        find by hashing `abc3231929`; the sixth character of the hash, and thus the first character
        of the password, is `1`:

        >>> next_digit('abc')
        ('1', 3231929)
        >>> md5('abc3231929')  # doctest: +ELLIPSIS
        '000001...'

      - `5017308` produces the next interesting hash, which starts with `000008f82...`,
        so the second character of the password is `8`:

        >>> next_digit('abc', start_at=3231930)
        ('8', 5017308)
        >>> md5('abc5017308')  # doctest: +ELLIPSIS
        '000008f82...'

      - The third time a hash starts with five zeroes is for `abc5278568`, discovering the char `f`:

        >>> next_digit('abc', start_at=5017309)
        ('f', 5278568)

    In this example, after continuing this search a total of eight times, the password
    is '18f47a30'. Given the actual Door ID, **what is the password**?

        >>> part_1('abc')
        part 1: password v1 for door ID 'abc' is '18f47a30'
        '18f47a30'
    """

    password = create_password(door_id)
    print(f"part 1: password v1 for door ID {door_id!r} is {password!r}")
    return password


def part_2(door_id: str) -> str:
    """
    As the door slides open, you are presented with a second door that uses a slightly more inspired
    security mechanism. Clearly unimpressed by the last version (in what movie is the password
    decrypted **in order**?!), the Easter Bunny engineers have worked out a better solution.

    Instead of simply filling in the password from left to right, the hash now also indicates
    the **position** within the password to fill. You still look for hashes that begin with five
    zeroes; however, now, the **sixth** character represents the **position** (`0`-`7`), and
    the **seventh** character is the character to put in that position.

    A hash result of `000001f` means that `f` is the **second** character in the password. Use only
    the **first result** for each position, and ignore invalid positions.

    For example, if the Door ID is `abc`:

      - The first interesting hash is from `abc3231929`, which produces `0000015...`;
        so, `5` goes in position `1`: `_5______`.

        >>> next_digit_v2('abc')
        ('5', 1, 3231929)
        >>> md5('abc3231929')  # doctest: +ELLIPSIS
        '0000015...'

      - In the previous method, `5017308` produced an interesting hash; however, it is ignored,
        because it specifies an invalid position (`8`).

        >>> md5('abc5017308')  # doctest: +ELLIPSIS
        '000008...'

      - The second interesting hash is at index `5357525`, which produces `000004e...`;
        so, `e` goes in position `4`: `_5__e___`:

        >>> next_digit_v2('abc', 5017309)
        ('e', 4, 5357525)

    You almost choke on your popcorn as the final character falls into place, producing the password
    `05ace8e3`.

    Given the actual Door ID and this new method, **what is the password**? Be extra proud of your
    solution if it uses a cinematic "decrypting" animation.

        >>> part_2('abc')
        part 2: password v2 for door ID 'abc' is '05ace8e3'
        '05ace8e3'
    """

    password = create_password_v2(door_id)
    print(f"part 2: password v2 for door ID {door_id!r} is {password!r}")
    return password


def create_password(door_id: str, length: int = 8, strength: int = 5) -> str:
    def password_digits() -> Iterable[str]:
        index = -1
        for _ in tqdm(range(length), desc="password v1", total=length, unit="digits"):
            digit, index = next_digit(door_id, start_at=index + 1, strength=strength)
            yield digit

    return ''.join(password_digits())


def next_digit(door_id: str, start_at: int = 0, strength: int = 5) -> tuple[str, int]:
    hash_, index = next_hash(door_id, start_at, '0' * strength)
    return hash_[strength], index


def create_password_v2(door_id: str, length: int = 8, strength: int = 5) -> str:
    assert 1 <= length <= 16

    digits_found: list[str] = ['_'] * length

    index = -1
    remaining_count = length

    with tqdm(desc="password v2", total=length, unit="digits") as progress:
        while remaining_count > 0:
            digit, pos, index = next_digit_v2(door_id, index + 1, length, strength)
            if digits_found[pos] == '_':
                digits_found[pos] = digit
                remaining_count -= 1
                progress.update()

    return ''.join(digits_found)


def next_digit_v2(
    door_id: str,
    start_at: int = 0,
    password_length: int = 8,
    strength: int = 5
) -> tuple[str, int, int]:
    hash_, index = next_hash(door_id, start_at, '0' * strength)
    position = int(hash_[strength], 16)
    if position < password_length:
        digit = hash_[strength + 1]
        return digit, position, index
    else:
        return next_digit_v2(door_id, index + 1, password_length, strength)


@lru_cache()
def next_hash(salt: str, start_at: int, prefix: str) -> tuple[str, int]:
    assert len(prefix) <= 16
    return next(
        (digest, index)
        for index in count(start_at)
        if (digest := md5(salt + str(index))).startswith(prefix)
    )


def door_id_from_file(fn: str) -> str:
    return open(relative_path(__file__, fn)).readline().strip()


if __name__ == '__main__':
    door_id_ = door_id_from_file('data/05-input.txt')
    part_1(door_id_)
    part_2(door_id_)
