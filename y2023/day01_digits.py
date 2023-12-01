"""
Advent of Code 2023
Day 1: Trebuchet?!
https://adventofcode.com/2023/day/1
"""

from typing import Iterable, Literal

from common.file import relative_path


def part_1(lines: Iterable[str]) -> int:
    """
    Something is wrong with global snow production, and you've been selected to take a look.
    The Elves have even given you a map; on it, they've used stars to mark the top fifty locations
    that are likely to be having problems.

    You try to ask why they can't just use a weather machine ("not powerful enough") and where
    they're even sending you ("the sky") and why your map looks mostly blank ("you sure ask a lot of
    questions") and hang on did you just say the sky ("of course, where do you think snow comes
    from") when you realize that the Elves are already loading you into a trebuchet ("please hold
    still, we need to strap you in").

    As they're making the final adjustments, they discover that their calibration document (your
    puzzle input) has been **amended** by a very young Elf who was apparently just excited to show
    off her art skills. Consequently, the Elves are having trouble reading values on the document.

    The newly-improved calibration document consists of lines of text; each line originally
    contained a specific **calibration value** that the Elves now need to recover. On each line,
    the calibration value can be found by combining the **first digit** and the **last digit**
    (in that order) to form a single **two-digit number**.

    For example:

        >>> lines_ = lines_from_text('''
        ...     1abc2
        ...     pqr3stu8vwx
        ...     a1b2c3d4e5f
        ...     treb7uchet
        ... ''')
        >>> [combine_digits(line) for line in lines_]
        [12, 38, 15, 77]
        >>> sum(_)
        142

    Consider your entire calibration document. **What is the sum of all of the calibration values?**

        >>> part_1(lines_)
        part 1: sum of all calibration values is 142
        142
    """

    result = sum(combine_digits(line) for line in lines)

    print(f"part 1: sum of all calibration values is {result}")
    return result


def part_2(lines: Iterable[str]) -> int:
    """
    Your calculation isn't quite right. It looks like some of the digits are actually **spelled out
    with letters**: `one`, `two`, `three`, `four`, `five`, `six`, `seven`, `eight`, and `nine`
    **also** count as valid "digits".

    Equipped with this new information, you now need to find the real first and last digit on each
    line. For example:

        >>> lines_ = lines_from_text('''
        ...     two1nine
        ...     eightwothree
        ...     abcone2threexyz
        ...     xtwone3four
        ...     4nineeightseven2
        ...     zoneight234
        ...     7pqrstsixteen
        ... ''')
        >>> [combine_digits(line, allow_words=True) for line in lines_]
        [29, 83, 13, 24, 42, 14, 76]
        >>> sum(_)
        281

    **What is the sum of all of the calibration values?**

        >>> part_2(lines_)
        part 2: sum of all calibration values is actually 281
        281
    """

    result = sum(combine_digits(line, allow_words=True) for line in lines)

    print(f"part 2: sum of all calibration values is actually {result}")
    return result


DIGIT_WORDS = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']


def combine_digits(line: str, allow_words: bool = False) -> int:
    first_digit = find_digit(line, 'first', allow_words)
    last_digit = find_digit(line, 'last', allow_words)
    return first_digit * 10 + last_digit


def find_digit(line: str, direction: Literal['first', 'last'], allow_words: bool) -> int:
    positions = range(len(line))

    return next(
        digit
        for pos in (positions if direction == 'first' else reversed(positions))
        if (digit := digit_at(line, pos, allow_words)) is not None
    )


def digit_at(line: str, pos: int, allow_words: bool = False) -> int | None:
    if line[pos].isdigit():
        return int(line[pos])

    elif allow_words:
        digits = (
            value
            for value, word in enumerate(DIGIT_WORDS, start=1)
            if line[pos:].startswith(word)
        )
        return next(digits, None)

    return None


def lines_from_file(fn: str) -> list[str]:
    return list(open(relative_path(__file__, fn)))


def lines_from_text(text: str) -> list[str]:
    return text.strip().splitlines()


def main(input_fn: str = 'data/01-input.txt') -> tuple[int, int]:
    lines = lines_from_file(input_fn)
    result_1 = part_1(lines)
    result_2 = part_2(lines)
    return result_1, result_2


if __name__ == '__main__':
    main()
