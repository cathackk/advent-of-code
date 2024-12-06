"""
Advent of Code 2016
Day 15: Timing is Everything
https://adventofcode.com/2016/day/15
"""

from typing import Iterable

from common.maths import modular_inverse
from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(discs: list['Disc']) -> int:
    """
    The halls open into an interior plaza containing a large kinetic sculpture. The sculpture is in
    a sealed enclosure and seems to involve a set of identical spherical capsules that are carried
    to the top and allowed to bounce through the maze of spinning pieces.

    Part of the sculpture is even interactive! When a button is pressed, a capsule is dropped and
    tries to fall through slots in a set of rotating discs to finally go through a little hole at
    the bottom and come out of the sculpture. If any of the slots aren't aligned with the capsule
    as it passes, the capsule bounces off the disc and soars away. You feel compelled to get one of
    those capsules.

    The discs pause their motion each second and come in different sizes; they seem to each have a
    fixed number of positions at which they stop. You decide to call the position with the slot `0`,
    and count up for each position it reaches next.

    Furthermore, the discs are spaced out so that after you push the button, one second elapses
    before the first disc is reached, and one second elapses as the capsule passes from one disc to
    the one below it. So, if you push the button at `time=100`, then the capsule reaches the top
    disc at `time=101`, the second disc at `time=102`, the third disc at `time=103`, and so on.

    The button will only drop a capsule at an integer time - no fractional seconds allowed.

    For example, at `time=0`, suppose you see the following arrangement:

        >>> example_discs = discs_from_text('''
        ...     Disc #1 has 5 positions; at time=0, it is at position 4.
        ...     Disc #2 has 2 positions; at time=0, it is at position 1.
        ... ''')
        >>> example_discs
        [(4, 5), (1, 2)]

    If you press the button exactly at `time=0`, the capsule would start to fall; it would reach the
    first disc at `time=1`. Since the first disc was at position `4` at `time=0`, by `time=1` it has
    ticked one position forward. As a five-position disc, the next position is `0`, and the capsule
    falls through the slot.

    Then, at `time=2`, the capsule reaches the second disc. The second disc has ticked forward two
    positions at this point: it started at position `1`, then continued to position `0`, and finally
    ended up at position `1` again. Because there's only a slot at position `0`, the capsule bounces
    away.

        >>> fall(example_discs, time=0)
        (1, (1, 2))

    If, however, you wait until `time=5` to push the button, then when the capsule reaches each
    disc, the first disc will have ticked forward `5+1 = 6` times (to position `0`), and the second
    disc will have ticked forward `5+2 = 7` times (also to position `0`). In this case, the capsule
    would fall through the discs and come out of the machine.

        >>> fall(example_discs, time=5) is None
        True

    However, your situation has more than two discs; you've noted their positions in your puzzle
    input. What is the **first time you can press the button** to get a capsule?

        >>> part_1(example_discs)
        part 1: press the button at time=5
        5
    """

    time = fall_through(discs)
    assert fall(discs, time) is None
    print(f"part 1: press the button at time={time}")
    return time


def part_2(original_discs: list['Disc']) -> int:
    """
    After getting the first capsule (it contained a star! what great fortune!), the machine detects
    your success and begins to rearrange itself.

    When it's done, the discs are back in their original configuration as if it were `time=0` again,
    but a new disc with `11` positions and starting at position `0` has appeared exactly one second
    below the previously-bottom disc.

    With this new disc, and counting again starting from `time=0` with the configuration in your
    puzzle input, what is the **first time you can press the button** to get another capsule?

        >>> example_discs = [(4, 5), (1, 2)]
        >>> example_discs_extended = example_discs + [(0, 11)]
        >>> fall(example_discs, 83)
        (0, (3, 5))
        >>> fall(example_discs, 84)
        (0, (4, 5))
        >>> fall(example_discs, 85) is None
        True

        >>> part_2(example_discs)
        part 2: press the button at time=85
        85
    """

    discs = original_discs + [(0, 11)]
    time = fall_through(discs)
    assert fall(discs, time) is None
    print(f"part 2: press the button at time={time}")
    return time


Disc = tuple[int, int]


def fall(discs: list[Disc], time: int) -> tuple[int, Disc] | None:
    for index, (dpos0, dsize) in enumerate(discs):
        dpos = (dpos0 + time + index + 1) % dsize
        if dpos != 0:
            return index, (dpos, dsize)

    else:
        return None


def fall_through(discs: list[Disc]) -> int:
    time, mod = 0, 1

    while True:
        stuck_at = fall(discs, time)
        if stuck_at is None:
            return time

        _, (pos, size) = stuck_at
        size_inv = modular_inverse(size, mod)
        mod *= size
        time += (size - pos) * (1 - size * size_inv) % mod


def discs_from_file(fn: str) -> list[Disc]:
    return list(discs_from_lines(open(fn)))


def discs_from_text(text: str) -> list[Disc]:
    return list(discs_from_lines(text.strip().splitlines()))


def discs_from_lines(lines: Iterable[str]) -> Iterable[Disc]:
    # "Disc #1 has 5 positions; at time=0, it is at position 4."
    for line_no, line in enumerate(lines):
        disc_no, size, pos0 = parse_line(
            line=line.strip(),
            pattern="Disc #$ has $ positions; at time=0, it is at position $."
        )
        assert line_no + 1 == int(disc_no)
        yield int(pos0), int(size)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    discs = discs_from_file(input_path)
    result_1 = part_1(discs)
    result_2 = part_2(discs)
    return result_1, result_2


if __name__ == '__main__':
    main()
