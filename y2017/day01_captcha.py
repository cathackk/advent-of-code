"""
Advent of Code 2017
Day 1: Inverse Captcha
https://adventofcode.com/2017/day/1
"""

from common.file import relative_path
from common.iteration import slidingw


def part_1(digits: str) -> int:
    """
    You're standing in a room with "digitization quarantine" written in LEDs along one wall.
    The only door is locked, but it includes a small interface. "Restricted Area - Strictly No
    Digitized Users Allowed."

    It goes on to explain that you may only leave by solving a captcha to prove you're **not**
    a human. Apparently, you only get one millisecond to solve the captcha: too fast for a normal
    human, but it feels like hours to you.

    The captcha requires you to review a sequence of digits (your puzzle input) and find the **sum**
    of all digits that match the **next** digit in the list. The list is circular, so the digit
    after the last digit is the **first** digit in the list.

    For example:

      - `1122` produces a sum of `3` (`1` + `2`) because the first digit (`1`) matches the second
        digit and the third digit (`2`) matches the fourth digit:

        >>> captcha_1('1122')
        3

      - `1111` produces `4` because each digit (all `1`) matches the next:

        >>> captcha_1('1111')
        4

      - `1234` produces `0` because no digit matches the next:

        >>> captcha_1('1234')
        0

      - `91212129` produces `9` because the only digit that matches the next one is the last digit:

        >>> captcha_1('91212129')
        9

    **What is the solution** to your captcha?

        >>> part_1('123321')
        part 1: solution is 4
        4
    """

    result = captcha_1(digits)
    print(f"part 1: solution is {result}")
    return result


def part_2(digits: str) -> int:
    """
    You notice a progress bar that jumps to 50% completion. Apparently, the door isn't yet
    satisfied, but it did emit a **star** as encouragement. The instructions change:

    Now, instead of considering the **next** digit, it wants you to consider the digit **halfway
    around** the circular list. That is, if your list contains `10` items, only include a digit in
    your sum if the digit `10/2 = 5` steps forward matches it. Fortunately, your list has an even
    number of elements.

    For example:

      - `1212` produces `6`: the list contains `4` items, and all four digits match the digit `2`
        items ahead:

        >>> captcha_2('1212')
        6

      - `1221` produces `0`, because every comparison is between a `1` and a `2`:

        >>> captcha_2('1221')
        0

      - `123425` produces `4`, because both `2`s match each other, but no other digit has a match:

        >>> captcha_2('123425')
        4

        >>> captcha_2('123123')
        12
        >>> captcha_2('12131415')
        4

    **What is the solution** to your new captcha?

        >>> part_2('12341234')
        part 2: solution is 20
        20
    """

    result = captcha_2(digits)
    print(f"part 2: solution is {result}")
    return result


def captcha_1(digits: str) -> int:
    return sum(
        int(a)
        for a, b in slidingw(digits, 2, wrap=True)
        if a == b
    )


def captcha_2(digits: str) -> int:
    d = len(digits)
    return sum(
        int(digits[k])
        for k in range(d)
        if digits[k] == digits[(k + d // 2) % d]
    )


def digits_from_file(fn: str) -> str:
    return open(relative_path(__file__, fn)).readline().strip()


if __name__ == '__main__':
    digits_ = digits_from_file('data/01-input.txt')
    part_1(digits_)
    part_2(digits_)
