"""
Advent of Code 2017
Day 4: High-Entropy Passphrases
https://adventofcode.com/2017/day/4
"""

from typing import Iterable

from meta.aoc_tools import data_path


def part_1(passphrases: Iterable[str]) -> int:
    """
    A new system policy has been put in place that requires all accounts to use a **passphrase**
    instead of simply a pass**word**. A passphrase consists of a series of words (lowercase letters)
    separated by spaces.

    To ensure security, a valid passphrase must contain no duplicate words.

    For example:

      - `aa bb cc dd ee` is valid:

        >>> is_valid('aa bb cc dd ee')
        True

      - `aa bb cc dd aa` is not valid - the word aa appears more than once:

        >>> is_valid('aa bb cc dd aa')
        False

      - `aa bb cc dd aaa` is valid - aa and aaa count as different words:

        >>> is_valid('aa bb cc dd aaa')
        True

    The system's full passphrase list is available as your puzzle input. **How many passphrases are
    valid?**

        >>> part_1(['aa bb cc', 'aa bb aa', 'aa bb aaa'])
        part 1: 2 valid passphrases
        2
    """

    result = sum(1 for pp in passphrases if is_valid(pp))
    print(f"part 1: {result} valid passphrases")
    return result


def part_2(passphrases: Iterable[str]) -> int:
    """
    For added security, yet another system policy has been put in place. Now, a valid passphrase
    must contain no two words that are anagrams of each other - that is, a passphrase is invalid if
    any word's letters can be rearranged to form any other word in the passphrase.

    For example:

      - `abcde fghij` is a valid passphrase:

        >>> is_valid_2('abcde fghij')
        True

      - `abcde xyz ecdab` is not valid - the letters from the third word can be rearranged to form
        the first word:

        >>> is_valid_2('abcde xyz ecdab')
        False

      - `a ab abc abd abf abj` is a valid passphrase, because all letters need to be used when
        forming another word:

        >>> is_valid_2('a ab abc abd abf abj')
        True

      - `iiii oiii ooii oooi oooo` is valid:

        >>> is_valid_2('iiii oiii ooii oooi oooo')
        True

      - `oiii ioii iioi iiio` is not valid - any of these words can be rearranged to form any other
        word:

        >>> is_valid_2('oiii ioii iioi iiio')
        False

    Under this new system policy, how many passphrases are valid?

        >>> part_2(['ab bc cd', 'ab ba cd', 'aa bb cc', 'ab ac cd', 'ad hd da dh'])
        part 2: 3 valid passphrases
        3
    """

    result = sum(1 for pp in passphrases if is_valid_2(pp))
    print(f"part 2: {result} valid passphrases")
    return result


def is_valid(passphrase: str) -> bool:
    words = passphrase.split()
    return len(words) == len(set(words))


def is_valid_2(passphrase: str) -> bool:
    words = [''.join(sorted(word)) for word in passphrase.split()]
    return len(words) == len(set(words))


def passphrases_from_file(fn: str) -> list[str]:
    return [line.strip() for line in open(fn)]


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    passphrases = passphrases_from_file(input_path)
    result_1 = part_1(passphrases)
    result_2 = part_2(passphrases)
    return result_1, result_2


if __name__ == '__main__':
    main()
