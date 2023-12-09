"""
Advent of Code 2023
Day 9: Mirage Maintenance
https://adventofcode.com/2023/day/9
"""

from typing import Iterable

from common.file import relative_path
from common.iteration import zip1


def part_1(sequences: Iterable[list[int]]) -> int:
    """
    You ride the camel through the sandstorm and stop where the ghost's maps told you to stop.
    The sandstorm subsequently subsides, somehow seeing you standing at an **oasis**!

    The camel goes to get some water and you stretch your neck. As you look up, you discover what
    must be yet another giant floating island, this one made of metal! That must be where
    the **parts to fix the sand machines** come from.

    There's even a hang glider partially buried in the sand here; once the sun rises and heats up
    the sand, you might be able to use the glider and the hot air to get all the way up to the metal
    island!

    While you wait for the sun to rise, you admire the oasis hidden here in the middle of Desert
    Island. It must have a delicate ecosystem; you might as well take some ecological readings while
    you wait. Maybe you can report any environmental instabilities you find to someone so the oasis
    can be around for the next sandstorm-worn traveler.

    You pull out your handy **Oasis And Sand Instability Sensor** and analyze your surroundings.
    The OASIS produces a report of many values and how they are changing over time (your puzzle
    input). Each line in the report contains the **history** of a single value. For example:

        >>> seqs = sequences_from_text('''
        ...     0 3 6 9 12 15
        ...     1 3 6 10 15 21
        ...     10 13 16 21 30 45
        ... ''')

    To best protect the oasis, your environmental report should include a **prediction of the next
    value** in each history. To do this, start by making a new sequence from the **difference at
    each step** of your history. If that sequence is **not** all zeroes, repeat this process, using
    the sequence you just generated as the input sequence. Once all of the values in your latest
    sequence are zeroes, you can extrapolate what the next value of the original history should be.

    In the above dataset, the first history is:

        >>> seqs[0]
        [0, 3, 6, 9, 12, 15]

    Because the values increase by `3` each step, the first sequence of differences that you
    generate will be:

        >>> list(diffs(_))
        [3, 3, 3, 3, 3]

    Note that this sequence has one fewer value than the input sequence because at each step it
    considers two numbers from the input. Since these values aren't **all zero**, repeat the
    process: the values differ by `0` at each step, so the next sequence is:

        >>> list(diffs(_))
        [0, 0, 0, 0]
        >>> any(_)
        False

    This means you have enough information to extrapolate the history! Visually, these sequences can
    be arranged like this:

        >>> visualize_diffs(seqs[0])
        0   3   6   9   12  15
          3   3   3   3   3
            0   0   0   0

    To extrapolate, start by adding a new zero to the end of your list of zeroes; because the zeroes
    represent differences between the two values above them, this also means there is now a
    placeholder in every sequence above it:

        0   3   6   9   12  15 *B*
          3   3   3   3   3  *A*
            0   0   0   0  *0*

    You can then start filling in placeholders from the bottom up. `A` needs to be the result of
    increasing `3` (the value to its left) by `0` (the value below it); this means `A` must be
    **`3`**:

    0   3   6   9   12  15  B
      3   3   3   3  *3* *3*
        0   0   0   0  *0*

    Finally, you can fill in `B`, which needs to be the result of increasing `15` (the value to its
    left) by `3` (the value below it), or **`18`**:

    0   3   6   9   12 *15**18*
      3   3   3   3   3  *3*
        0   0   0   0   0

    So, the next value of the first history is:

        >>> extrapolate(seqs[0])
        18

    Finding all-zero differences for the second history requires an additional sequence:


        >>> visualize_diffs(seqs[1])
        1   3   6   10  15  21
          2   3   4   5   6
            1   1   1   1
              0   0   0

    Then, following the same process as before, work out the next value in each sequence from the
    bottom up:

        >>> visualize_diffs(seqs[1], with_extrapolation=True)
        1   3   6   10  15  21  28
          2   3   4   5   6   7
            1   1   1   1   1
              0   0   0   0

    So, the next value of the second history is:

        >>> extrapolate(seqs[1])
        28

    The third history requires even more sequences, but its next value can be found the same way:

        >>> visualize_diffs(seqs[2], with_extrapolation=True)
        10  13  16  21  30  45  68
          3   3   5   9   15  23
            0   2   4   6   8
              2   2   2   2
                0   0   0

    So, the next value of the third history is:

        >>> extrapolate(seqs[2])
        68

    If you find the next value for each history in this example and add them together, you get:

        >>> sum(extrapolate(seq) for seq in seqs)
        114

    Analyze your OASIS report and extrapolate the next value for each history.
    **What is the sum of these extrapolated values?**

        >>> part_1(seqs)
        part 1: sum of extrapolated values is 114
        114
    """

    result = sum(extrapolate(seq) for seq in sequences)

    print(f"part 1: sum of extrapolated values is {result}")
    return result


def part_2(sequences: Iterable[list[int]]) -> int:
    """
    Of course, it would be nice to have **even more history** included in your report. Surely it's
    safe to just **extrapolate backwards** as well, right?

    For each history, repeat the process of finding differences until the sequence of differences is
    entirely zero. Then, rather than adding a zero to the end and filling in the next values of each
    previous sequence, you should instead add a zero to the **beginning** of your sequence of
    zeroes, then fill in new **first** values for each previous sequence.

    In particular, here's what the third example history looks like when extrapolating back in time:

        >>> seqs = sequences_from_file('data/09-example.txt')
        >>> seqs[2]
        [10, 13, 16, 21, 30, 45]
        >>> visualize_diffs(seqs[2], with_backward_extrapolation=True)
        5   10  13  16  21  30  45
          5   3   3   5   9   15
            -2  0   2   4   6
              2   2   2   2
                0   0   0

    Adding the new values on the left side of each sequence from bottom to top eventually reveals
    the new left-most history value:

        >>> extrapolate(seqs[2], backwards=True)
        5

    Doing this for the remaining example data above results in:

        >>> extrapolate(seqs[0], backwards=True)
        -3
        >>> extrapolate(seqs[1], backwards=True)
        0

    Adding all three new values together produces:

        >>> sum(extrapolate(seq, backwards=True) for seq in seqs)
        2

    Analyze your OASIS report again, this time extrapolating the **previous** value of each history.
    **What is the sum of these extrapolated values?**

        >>> part_2(seqs)
        part 2: sum of backward-extrapolated values is 2
        2
    """

    result = sum(extrapolate(seq, backwards=True) for seq in sequences)

    print(f"part 2: sum of backward-extrapolated values is {result}")
    return result


def diffs(values: Iterable[int]) -> Iterable[int]:
    return (b - a for a, b in zip1(values))


def extrapolate(values: Iterable[int], backwards: bool = False) -> int:
    values_list = list(values)
    if not any(values_list):
        return 0

    new_value = extrapolate(diffs(values_list), backwards)
    if not backwards:
        return values_list[-1] + new_value
    else:
        return values_list[0] - new_value


def visualize_diffs(
    values: Iterable[int],
    with_extrapolation: bool = False,
    with_backward_extrapolation: bool = False,
) -> None:
    values_list = list(values)
    indent = ''

    if with_extrapolation:
        values_list.append(extrapolate(values_list))
    if with_backward_extrapolation:
        values_list.insert(0, extrapolate(values_list, backwards=True))

    while True:
        print(indent + ''.join(str(val).ljust(4) for val in values_list).rstrip())
        if not any(values_list):
            break
        values_list = list(diffs(values_list))
        indent += '  '


def sequences_from_file(fn: str) -> list[list[int]]:
    return list(sequences_from_lines(open(relative_path(__file__, fn))))


def sequences_from_text(text: str) -> list[list[int]]:
    return list(sequences_from_lines(text.strip().splitlines()))


def sequences_from_lines(lines: Iterable[str]) -> Iterable[list[int]]:
    return ([int(val) for val in line.strip().split()] for line in lines)


def main(input_fn: str = 'data/09-input.txt') -> tuple[int, int]:
    sequences = sequences_from_file(input_fn)
    result_1 = part_1(sequences)
    result_2 = part_2(sequences)
    return result_1, result_2


if __name__ == '__main__':
    main()
