"""
Advent of Code 2015
Day 4: The Ideal Stocking Stuffer
https://adventofcode.com/2015/day/4
"""

from itertools import count

from common.md5 import md5
from common.utils import relative_path


def part_1(key: str) -> int:
    """
    Santa needs help mining some AdventCoins (very similar to bitcoins) to use as gifts for all the
    economically forward-thinking little girls and boys.

    To do this, he needs to find MD5 hashes which, in hexadecimal, start with at least
    **five zeroes**. The input to the MD5 hash is some secret key (your puzzle input, given below)
    followed by a number in decimal. To mine AdventCoins, you must find Santa the lowest positive
    number (no leading zeroes: `1`, `2`, `3`, ...) that produces such a hash.

    For example:

      - If your secret key is `abcdef`, the answer is `609043`, because the MD5 hash of
        `abcdef609043` starts with five zeroes (`000001dbbfa...`), and it is the lowest such number
        to do so:

        >>> md5('abcdef609043')  # doctest: +ELLIPSIS
        '000001dbbfa...'
        >>> mine('abcdef', target='00000')
        609043

      - If your secret key is `pqrstuv`, the lowest number it combines with to make an MD5 hash
        starting with five zeroes is `1048970`:

        >>> md5('pqrstuv1048970')  # doctest: +ELLIPSIS
        '000006136ef...'
        >>> mine('pqrstuv', target='00000')
        1048970

    Mine one AdventCoin!

        >>> part_1('uvwxyz')
        part 1: coin mined with number 181349
        181349
    """

    result = mine(key, target='00000')
    print(f"part 1: coin mined with number {result}")
    return result


def part_2(key: str) -> int:
    """
    Now find one that starts with **six zeroes**.

        >>> part_2('uvwxyz')
        part 2: coin mined with number 8218955
        8218955
    """

    result = mine(key, target='000000')
    print(f"part 2: coin mined with number {result}")
    return result


def mine(key: str, target: str = '00000') -> int:
    return next(k for k in count(1) if md5(key + str(k)).startswith(target))


def key_from_file(fn: str) -> str:
    return open(relative_path(__file__, fn)).readline().strip()


if __name__ == '__main__':
    key_ = key_from_file('data/04-input.txt')
    part_1(key_)
    part_2(key_)
