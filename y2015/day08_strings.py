"""
Advent of Code 2015
Day 8: Matchsticks
https://adventofcode.com/2015/day/8
"""

from ast import literal_eval

from common.file import relative_path


def part_1(strings: list[str]) -> int:
    r"""
    Space on the sleigh is limited this year, and so Santa will be bringing his list as a digital
    copy. He needs to know how much space it will take up when stored.

    It is common in many programming languages to provide a way to escape special characters in
    strings. For example, C, JavaScript, Perl, Python, and even PHP handle special characters in
    very similar ways.

    However, it is important to realize the difference between the number of characters **in the
    code representation of the string literal** and the number of characters **in the in-memory
    string itself**.

    For example:

      - `""` is `2` characters of code (the two double quotes), but the string contains zero
        characters:

        >>> memory_len('""')
        0

      - `"abc"` is `5` characters of code, but `3` characters in the string data:

        >>> memory_len('"abc"')
        3

      - `"aaa\"aaa"` is `10` characters of code, but the string itself contains six "`a`" characters
        and a single, escaped quote character, for a total of `7` characters in the string data:

        >>> memory_len('"aaa\\"aaa"')
        7

      - `"\x27"` is `6` characters of code, but the string itself contains just one - an apostrophe
        (`'`), escaped using hexadecimal notation:

        >>> memory_len('"\\x27"')
        1

    Santa's list is a file that contains many double-quoted string literals, one on each line.
    The only escape sequences used are:

      - `\\` (which represents a single backslash),
      - `\"` (which represents a lone double-quote character), and
      - `\x` plus two hexadecimal characters (which represents a single char with that ASCII code).

    Disregarding the whitespace in the file, what is **the number of characters of code for string
    literals** minus **the number of characters in memory for the values of the strings** in total
    for the entire file?

    For example, given the four strings above, the total number of characters of string code
    (`2 + 5 + 10 + 6 = 23`) minus the total number of characters in memory for string values
    (`0 + 3 + 7 + 1 = 11`) is:

        >>> part_1(['""', '"abc"', '"aaa\\"aaa"', '"\\x27"'])
        part 1: 23 code chars - 11 memory chars = 12
        12
    """

    total_code_len = sum(len(s) for s in strings)
    total_memory_len = sum(memory_len(s) for s in strings)
    result = total_code_len - total_memory_len

    print(f"part 1: {total_code_len} code chars - {total_memory_len} memory chars = {result}")
    return result


def part_2(strings: list[str]) -> int:
    r"""
    Now, let's go the other way. In addition to finding the number of characters of code, you should
    now **encode each code representation as a new string** and find the number of characters of the
    new encoded representation, including the surrounding double quotes.

    For example:

      - `""` encodes to `"\"\""`, an increase from `2` characters to `6`:

        >>> repr_len('""')
        6

      - `"abc"` encodes to `"\"abc\""`, an increase from `5` characters to `9`:

        >>> repr_len('"abc"')
        9

      - `"aaa\"aaa"` encodes to `"\"aaa\\\"aaa\""`, an increase from `10` characters to `16`:

        >>> repr_len('"aaa\\"aaa"')
        16

      - `"\x27"` encodes to `"\"\\x27\""`, an increase from `6` characters to `11`:

        >>> repr_len('"\\x27"')
        11

    Your task is to find the **total number of characters to represent the newly encoded strings**
    minus **the number of characters of code in each original string literal**. For example, for the
    strings above, the total encoded length (`6 + 9 + 16 + 11 = 42`) minus the characters in the
    original code representation (`23`, just like in the first part of this puzzle) is:

        >>> part_2(['""', '"abc"', '"aaa\\"aaa"', '"\\x27"'])
        part 2: 42 repr chars - 23 code chars = 19
        19
    """

    total_repr_len = sum(repr_len(s) for s in strings)
    total_code_len = sum(len(s) for s in strings)
    result = total_repr_len - total_code_len
    print(f"part 2: {total_repr_len} repr chars - {total_code_len} code chars = {result}")
    return result


def memory_len(string: str) -> int:
    return len(literal_eval(string))


def repr_len(string: str) -> int:
    return 2 + sum(2 if c in ('\\', '"') else 1 for c in string)


def strings_from_file(fn: str) -> list[str]:
    return [line.strip() for line in open(relative_path(__file__, fn))]


if __name__ == '__main__':
    strings_ = strings_from_file('data/08-input.txt')
    part_1(strings_)
    part_2(strings_)
