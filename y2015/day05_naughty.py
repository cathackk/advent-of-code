"""
Advent of Code 2015
Day 5: Doesn't He Have Intern-Elves For This?
https://adventofcode.com/2015/day/5
"""

from typing import Iterable

from common.iteration import zip1
from meta.aoc_tools import data_path


def part_1(strings: Iterable[str]) -> int:
    """
    Santa needs help figuring out which strings in his text file are naughty or nice.

    A nice string is one with all of the following properties:

      - It contains at least three vowels (`aeiou` only), like `aei`, `xazegov`, or `aeiouaeiouaei`.
      - It contains at least one letter that appears twice in a row, like `xx`, `abcdde` (`dd`), or
        `aabbccdd` (`aa`, `bb`, `cc`, or `dd`).
      - It does not contain the strings `ab`, `cd`, `pq`, or `xy`, even if they are part of one of
        the other requirements.

    For example:

      - `ugknbfddgicrmopn` is nice because it has at least three vowels (`u...i...o...`), a double
        letter (`...dd...`), and none of the disallowed substrings:

        >>> is_nice('ugknbfddgicrmopn')
        True

      - `aaa` is nice because it has at least three vowels and a double letter, even though
        the letters used by different rules overlap:

        >>> is_nice('aaa')
        True

      - `jchzalrnumimnmhp` is naughty because it has no double letter,
      - `haegwjzuvuyypxyu` is naughty because it contains the string `xy`,
      - `dvszwmarrgswjxmb` is naughty because it contains only one vowel:

        >>> is_nice('jchzalrnumimnmhp')
        False
        >>> is_nice('haegwjzuvuyypxyu')
        False
        >>> is_nice('dvszwmarrgswjxmb')
        False

    How many strings are nice?

        >>> part_1(['ugknbfddgicrmopn', 'aaa', 'jchzalrnumimnmhp', 'haegwjzuvuyypxyu'])
        part 1: total 2 nice strings
        2
    """

    result = sum(1 for s in strings if is_nice(s))
    print(f"part 1: total {result} nice strings")
    return result


def part_2(strings: Iterable[str]) -> int:
    """
    Realizing the error of his ways, Santa has switched to a better model of determining whether
    a string is naughty or nice. None of the old rules apply, as they are all clearly ridiculous.

    Now, a nice string is one with all of the following properties:

      - It contains a pair of any two letters that appears at least twice in the string without
        overlapping, like `xyxy` (`xy`) or `aabcdefgaa` (`aa`), but not like `aaa` (`aa`, but it
        overlaps).
      - It contains at least one letter which repeats with exactly one letter between them,
        like `xyx`, `abcdefeghi` (`efe`), or even `aaa`.

    For example:

      - `qjhvhtzxzqqjkmpb` is nice because is has a pair that appears twice (`qj`) and a letter that
        repeats with exactly one letter between them (`zxz`):

        >>> is_nice_2('qjhvhtzxzqqjkmpb')
        True

      - `xxyxx` is nice because it has a pair that appears twice and a letter that repeats with one
        between, even though the letters used by each rule overlap:

        >>> is_nice_2('xxyxx')
        True

      - `uurcxstgmygtbstg` is naughty because it has a pair (`tg`) but no repeat with a single
        letter between them:

        >>> is_nice_2('uurcxstgmygtbstg')
        False

      - `ieodomkazucvgmuy` is naughty because it has a repeating letter with one between (`odo`),
        but no pair that appears twice:

        >>> is_nice_2('ieodomkazucvgmuy')
        False

    How many strings are nice under these new rules?

        >>> part_2(['qjhvhtzxzqqjkmpb', 'xxyxx', 'uurcxstgmygtbstg', 'ieodomkazucvgmuy'])
        part 2: total 2 nice strings
        2
    """

    result = sum(1 for s in strings if is_nice_2(s))
    print(f"part 2: total {result} nice strings")
    return result


def is_nice(string: str) -> bool:
    return (
        sum(1 for char in string if char in set('aeiou')) >= 3
        and any(c1 == c2 for c1, c2 in zip1(string))
        and not any(
           string[k:k + 2] in {'ab', 'cd', 'pq', 'xy'}
           for k in range(len(string) - 1)
        )
    )


def is_nice_2(string: str) -> bool:
    return (
        any(
            string[i:i + 2] == string[j:j + 2]
            for i in range(len(string) - 3)
            for j in range(i + 2, len(string) - 1)
        )
        and any(
            string[k - 1] == string[k + 1]
            for k in range(1, len(string) - 1)
        )
    )


def strings_from_file(fn: str) -> list[str]:
    return [line.strip() for line in open(fn)]


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    strings = strings_from_file(input_path)
    result_1 = part_1(strings)
    result_2 = part_2(strings)
    return result_1, result_2


if __name__ == '__main__':
    main()
