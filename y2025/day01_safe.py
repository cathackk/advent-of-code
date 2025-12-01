"""
Advent of Code 2025
Day 1: Secret Entrance
https://adventofcode.com/2025/day/1
"""

from typing import Iterable

from common.file import relative_path


def part_1(rotations: Iterable[int]) -> int:
    """
    The Elves have good news and bad news.

    The good news is that they've discovered project management! This has given them the tools they
    need to prevent their usual Christmas emergency. For example, they now know that the North Pole
    decorations need to be finished soon so that other critical tasks can start on time.

    The bad news is that they've realized they have a **different** emergency: according to their
    resource planning, none of them have any time left to decorate the North Pole!

    To save Christmas, the Elves need **you to finish decorating the North Pole by December 12th.**

    Collect stars by solving puzzles. Two puzzles will be made available on each day; the second
    puzzle is unlocked when you complete the first. Each puzzle grants **one star**. Good luck!

    You arrive at the secret entrance to the North Pole base ready to start decorating.
    Unfortunately, the **password** seems to have been changed, so you can't get in. A document
    taped to the wall helpfully explains:

    "Due to new security protocols, the password is locked in the safe below. Please see the
    attached document for the new combination."

    The safe has a dial with only an arrow on it; around the dial are the numbers `0` through `99`
    in order. As you turn the dial, it makes a small click noise as it reaches each number.

    The attached document (your puzzle input) contains a sequence of **rotations**, one per line,
    which tell you how to open the safe. A rotation starts with an `L` or `R` which indicates
    whether the rotation should be to the **left** (toward lower numbers) or to the **right**
    (toward higher numbers). Then, the rotation has a **distance** value which indicates how many
    clicks the dial should be rotated in that direction.

    So, if the dial were pointing at `11`, a rotation of `R8` would cause the dial to point at `19`:

        >>> 11 + rotation_from_str('R8')
        19

    After that, a rotation of `L19` would cause it to point at `0`:

        >>> 19 + rotation_from_str('L19')
        0

    Because the dial is a circle, turning the dial **left from `0`** one click makes it point at
    `99`. Similarly, turning the dial **right from `99`** one click makes it point at `0`.

    So, if the dial were pointing at `5`, a rotation of `L10` would cause it to point at:

        >>> (5 + rotation_from_str('L10')) % 100
        95

    After that, a rotation of `R5` could cause it to point at:

        >>> (95 + rotation_from_str('R5')) % 100
        0

    The dial starts by pointing at `50`.

    You could follow the instructions, but your recent required official North Pole secret entrance
    security training seminar taught you that the safe is actually a decoy. The actual password is
    **the number of times the dial is left pointing at `0` after any rotation in the sequence**.

    For example, suppose the attached document contained the following rotations:

        >>> example = rotations_from_text('''
        ...     L68
        ...     L30
        ...     R48
        ...     L5
        ...     R60
        ...     L55
        ...     L1
        ...     L99
        ...     R14
        ...     L82
        ... ''')
        >>> example  # doctest: +NORMALIZE_WHITESPACE
        [-68, -30, 48, -5, 60, -55, -1, -99, 14, -82]

    Following these rotations would cause the dial to move as follows:

        >>> zeroes = count_zeroes(start=50, rotations=example, print_steps=True)
        The dial starts by pointing at 50.
        The dial is rotated L68 to point at 82.
        The dial is rotated L30 to point at 52.
        The dial is rotated R48 to point at 0.
        The dial is rotated L5 to point at 95.
        The dial is rotated R60 to point at 55.
        The dial is rotated L55 to point at 0.
        The dial is rotated L1 to point at 99.
        The dial is rotated L99 to point at 0.
        The dial is rotated R14 to point at 14.
        The dial is rotated L82 to point at 32.

    Because the dial points at `0` a total of three times during this process, the password in this
    example is **`3`**.

        >>> zeroes
        3

    Analyze the rotations in your attached document.
    **What's the actual password to open the door?**

        >>> part_1(example)
        part 1: the password is 3
        3
    """

    result = count_zeroes(start=50, rotations=rotations)

    print(f"part 1: the password is {result}")
    return result


def part_2(rotations: Iterable[int]) -> int:
    """
    You're sure that's the right password, but the door won't open. You knock, but nobody answers.
    You build a snowman while you think.

    As you're rolling the snowballs for your snowman, you find another security document that must
    have fallen into the snow:

    "Due to newer security protocols, please use **password method 0x434C49434B** until further
    notice."

    You remember from the training seminar that "method 0x434C49434B" means you're actually supposed
    to count the number of times **any click** causes the dial to point at `0`, regardless of
    whether it happens during a rotation or at the end of one.

    Following the same rotations as in the above example, the dial points at zero a few extra times
    during its rotations:

        >>> example = rotations_from_file('data/01-example.txt')
        >>> zero_count = count_zeroes(start=50, rotations=example, transient=True, print_steps=True)
        The dial starts by pointing at 50.
        The dial is rotated L68 to point at 82; during this rotation, it points at 0 once.
        The dial is rotated L30 to point at 52.
        The dial is rotated R48 to point at 0.
        The dial is rotated L5 to point at 95.
        The dial is rotated R60 to point at 55; during this rotation, it points at 0 once.
        The dial is rotated L55 to point at 0.
        The dial is rotated L1 to point at 99.
        The dial is rotated L99 to point at 0.
        The dial is rotated R14 to point at 14.
        The dial is rotated L82 to point at 32; during this rotation, it points at 0 once.


    In this example, the dial points at `0` three times at the end of a rotation, plus three more
    times during a rotation. So, in this example, the new password would be **`6`**.

        >>> zero_count
        6

    Be careful: if the dial were pointing at `50`, a single rotation like `R1000` would cause the
    dial to point at `0` ten times before returning back to `50`!

        >>> count_zeroes(start=50, rotations=[rotation_from_str('R1000')], transient=True)
        10

    Using password method 0x434C49434B, **what is the password to open the door?**

        >>> part_2(example)
        part 2: the password is actually 6
        6
    """

    result = count_zeroes(start=50, rotations=rotations, transient=True)

    print(f"part 2: the password is actually {result}")
    return result


def count_zeroes(
    rotations: Iterable[int],
    start: int = 50,
    size: int = 100,
    transient: bool = False,
    print_steps: bool = False,
) -> int:
    if print_steps:
        print(f"The dial starts by pointing at {start}.")

    number = start
    zeroes = 0
    zeroes_passed = 0

    for rotation in rotations:
        if transient:
            zeroes += (zeroes_passed := transitions(number, rotation, size))
        number = (number + rotation) % size
        if number == 0:
            zeroes += 1

        if print_steps:
            if zeroes_passed == 1:
                zp = "; during this rotation, it points at 0 once"
            elif zeroes_passed > 1:
                zp = f"; during this rotation, it points at 0 total {zeroes_passed} times"
            else:
                zp = ""
            print(f"The dial is rotated {rotation_to_str(rotation)} to point at {number}{zp}.")

    return zeroes


def transitions(start, rotation, size: int = 100):
    """
    Counts number of times the dial transitions over `0`.

        >>> transitions(0, 1)
        0
        >>> transitions(0, 100)
        0
        >>> transitions(0, 101)
        1
        >>> transitions(0, 200)
        1
        >>> transitions(0, 201)
        2
        >>> transitions(50, 30)
        0
        >>> transitions(50, 80)
        1
        >>> transitions(50, 200)
        2
        >>> transitions(50, 3000)
        30
        >>> transitions(99, 1)
        0
        >>> transitions(99, 2)
        1

        >>> transitions(0, -1)
        0
        >>> transitions(0, -100)
        0
        >>> transitions(0, -101)
        1
        >>> transitions(0, -3000)
        29
        >>> transitions(1, -1)
        0
        >>> transitions(1, -2)
        1
        >>> transitions(1, -101)
        1
        >>> transitions(1, -102)
        2
        >>> transitions(50, -40)
        0
        >>> transitions(50, -60)
        1
        >>> transitions(50, -3000)
        30
    """
    assert 0 <= start < size
    assert rotation != 0

    if rotation > 0:
        return abs((start + rotation - 1) // size)
    else:
        return abs((start + rotation) // size) - (start == 0)


def rotations_from_file(fn: str) -> list[int]:
    return list(rotations_from_lines(open(relative_path(__file__, fn))))


def rotations_from_text(text: str) -> list[int]:
    return list(rotations_from_lines(text.strip().splitlines()))


def rotations_from_lines(lines: Iterable[str]) -> Iterable[int]:
    return (rotation_from_str(line) for line in lines)


def rotation_from_str(rotation_str: str) -> int:
    rss = rotation_str.strip()
    direction = rss[0]
    distance = int(rss[1:])
    assert distance > 0

    if direction == 'R':
        return distance
    elif direction == 'L':
        return -distance
    else:
        raise KeyError(direction)

def rotation_to_str(rotation: int) -> str:
    direction = 'R' if rotation >= 0 else 'L'
    distance = str(abs(rotation))
    return direction + distance


def main(input_fn: str = 'data/01-input.txt') -> tuple[int, int]:
    rotations = rotations_from_file(input_fn)
    result_1 = part_1(rotations)
    result_2 = part_2(rotations)
    return result_1, result_2


if __name__ == '__main__':
    main()
