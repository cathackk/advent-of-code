"""
Advent of Code 2016
Day 6: Signals and Noise
https://adventofcode.com/2016/day/6
"""

from collections import Counter

from common.utils import relative_path


def part_1(lines: list[str]) -> str:
    """
    Something is jamming your communications with Santa. Fortunately, your signal is only partially
    jammed, and protocol in situations like this is to switch to a simple repetition code to get
    the message through.

    In this model, the same message is sent repeatedly. You've recorded the repeating message signal
    (your puzzle input), but the data seems quite corrupted - almost too badly to recover. Almost.

    All you need to do is figure out which character is most frequent for each position.
    For example, suppose you had recorded the following messages:

        >>> example_lines = lines_from_text('''
        ...     eedadn
        ...     drvtee
        ...     eandsr
        ...     raavrd
        ...     atevrs
        ...     tsrnev
        ...     sdttsa
        ...     rasrtv
        ...     nssdts
        ...     ntnada
        ...     svetve
        ...     tesnvt
        ...     vntsnd
        ...     vrdear
        ...     dvrsen
        ...     enarar
        ... ''')

    The most common character in the first column is `e`; in the second, `a`; in the third, `s`,
    and so on. Combining these characters returns the error-corrected message, `easter`.

        >>> repcode(example_lines)
        'easter'

    Given the recording in your puzzle input, **what is the error-corrected version** of the message
    being sent?

        >>> part_1(example_lines)
        part 1: decoded message is 'easter'
        'easter'
    """

    decoded_message = repcode(lines)
    print(f"part 1: decoded message is {decoded_message!r}")
    return decoded_message


def part_2(lines: list[str]) -> str:
    """
    Of course, that **would** be the message - if you hadn't agreed to use a **modified repetition
    code** instead.

    In this modified code, the sender instead transmits what looks like random data, but for each
    character, the character they actually want to send is **slightly less** likely than the others.
    Even after signal-jamming noise, you can look at the letter distributions in each column and
    choose the **least common** letter to reconstruct the original message.

    In the above example, the least common character in the first column is `a`; in the second, `d`,
    and so on. Repeating this process for the remaining characters produces the original message,
    `advent`.

        >>> example_lines = lines_from_file('data/06-example.txt')
        >>> repcode(example_lines, least_common=True)
        'advent'

    Given the recording in your puzzle input and this new decoding methodology, **what is
    the original message** that Santa is trying to send?

        >>> part_2(example_lines)
        part 2: decoded message is 'advent'
        'advent'
    """

    decoded_message = repcode(lines, least_common=True)
    print(f"part 2: decoded message is {decoded_message!r}")
    return decoded_message


def repcode(lines: list[str], least_common: bool = False) -> str:
    most_common_index = -1 if least_common else 0
    return ''.join(
        Counter(column).most_common()[most_common_index][0]
        for column in zip(*lines)
    )


def lines_from_file(fn: str) -> list[str]:
    return [line.strip() for line in open(relative_path(__file__, fn))]


def lines_from_text(text: str) -> list[str]:
    return [line.strip() for line in text.strip().splitlines()]


if __name__ == '__main__':
    lines_ = lines_from_file("data/06-input.txt")
    part_1(lines_)
    part_2(lines_)
