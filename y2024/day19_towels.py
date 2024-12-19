"""
Advent of Code 2024
Day 19: Linen Layout
https://adventofcode.com/2024/day/19
"""

from functools import lru_cache
from typing import Iterable, Iterator, Sequence, TypeAlias

from common.file import relative_path
from common.iteration import maybe_next


Pattern: TypeAlias = str
Patterns = Sequence[Pattern]
Design: TypeAlias = str
Designs = Sequence[Design]


def part_1(patterns: Patterns, designs: Designs) -> int:
    """
    Today, The Historians take you up to the hot springs (y2023/day12_nono.py) on Gear Island!
    Very suspiciously, absolutely nothing goes wrong as they begin their careful search of the vast
    field of helixes.

    Could this **finally** be your chance to visit the onsen next door? Only one way to find out.

    After a brief conversation with the reception staff at the onsen front desk, you discover that
    you don't have the right kind of money to pay the admission fee. However, before you can leave,
    the staff get your attention. Apparently, they've heard about how you helped at the hot springs,
    and they're willing to make a deal: if you can simply help them **arrange their towels**,
    they'll let you in for **free**!

    Every towel at this onsen is marked with a **pattern of colored stripes**. There are only a few
    patterns, but for any particular pattern, the staff can get you as many towels with that pattern
    as you need. Each stripe can be **white** (`w`), **blue** (`u`), **black** (`b`), **red** (`r`),
    or **green** (`g`). So, a towel with the pattern `ggr` would have a green stripe, a green
    stripe, and then a red stripe, in that order. (You can't reverse a pattern by flipping a towel
    upside-down, as that would cause the onsen logo to face the wrong way.)

    The Official Onsen Branding Expert has produced a list of **designs** - each a long sequence of
    stripe colors - that they would like to be able to display. You can use any towels you want, but
    all of the towels' stripes must exactly match the desired design. So, to display the design
    `rgrgr`, you could use two `rg` towels and then an `r` towel, an `rgr` towel and then a `gr`
    towel, or even a single massive `rgrgr` towel (assuming such towel patterns were actually
    available).

    To start, collect together all of the available towel patterns and the list of desired designs
    (your puzzle input). For example:

        >>> example_patterns, example_designs = input_from_text('''
        ...     r, wr, b, g, bwu, rb, gb, br
        ...
        ...     brwrr
        ...     bggr
        ...     gbbr
        ...     rrbgbr
        ...     ubwu
        ...     bwurrg
        ...     brgr
        ...     bbrgwb
        ... ''')

    The first line indicates the available towel patterns; in this example, the onsen has unlimited
    towels with a single red stripe (`r`), unlimited towels with a white stripe and then a red
    stripe (`wr`), and so on.

        >>> example_patterns
        ['r', 'wr', 'b', 'g', 'bwu', 'rb', 'gb', 'br']

    After the blank line, the remaining lines each describe a design the onsen would like to be able
    to display. In this example, the first design (`brwrr`) indicates that the onsen would like to
    be able to display a black stripe, a red stripe, a white stripe, and then two red stripes,
    in that order.

        >>> example_designs
        ['brwrr', 'bggr', 'gbbr', 'rrbgbr', 'ubwu', 'bwurrg', 'brgr', 'bbrgwb']

    Not all designs will be possible with the available towels. In the above example, the designs
    are possible or impossible as follows:

        >>> decompose_design('brwrr', example_patterns)
        ['br', 'wr', 'r']
        >>> decompose_design('bggr', example_patterns)
        ['b', 'g', 'g', 'r']
        >>> decompose_design('gbbr', example_patterns)
        ['gb', 'br']
        >>> decompose_design('rrbgbr', example_patterns)
        ['r', 'rb', 'gb', 'r']
        >>> decompose_design('ubwu', example_patterns)  # impossible
        >>> decompose_design('bwurrg', example_patterns)
        ['bwu', 'r', 'r', 'g']
        >>> decompose_design('brgr', example_patterns)
        ['br', 'g', 'r']
        >>> decompose_design('bbrgwb', example_patterns)  # impossible

    In this example, **`6`** of the eight designs are possible with the available towel patterns.

        >>> sum(1 for des in example_designs if decompose_design(des, example_patterns) is not None)
        6

    To get into the onsen as soon as possible, consult your list of towel patterns and desired
    designs carefully. **How many designs are possible?**

        >>> part_1(patterns=example_patterns, designs=example_designs)
        part 1: out of total 8 designs, 6 are possible
        6
    """

    result = sum(1 for des in designs if decompose_design(des, patterns) is not None)

    print(f"part 1: out of total {len(designs)} designs, {result} are possible")
    return result


def part_2(patterns: Patterns, designs: Designs) -> int:
    """
    The staff don't really like some of the towel arrangements you came up with. To avoid an endless
    cycle of towel rearrangement, maybe you should just give them every possible option.

    Here are all of the different ways the above example's designs can be made:

        >>> example_patterns, example_designs = input_from_file('data/19-example.txt')
        >>> list(decompose_design_all('brwrr', example_patterns))
        [['b', 'r', 'wr', 'r'], ['br', 'wr', 'r']]
        >>> list(decompose_design_all('bggr', example_patterns))
        [['b', 'g', 'g', 'r']]
        >>> list(decompose_design_all('gbbr', example_patterns))
        [['g', 'b', 'b', 'r'], ['g', 'b', 'br'], ['gb', 'b', 'r'], ['gb', 'br']]
        >>> list(decompose_design_all('rrbgbr', example_patterns))  # doctest: +NORMALIZE_WHITESPACE
        [['r', 'r', 'b', 'g', 'b', 'r'],
         ['r', 'r', 'b', 'g', 'br'],
         ['r', 'r', 'b', 'gb', 'r'],
         ['r', 'rb', 'g', 'b', 'r'],
         ['r', 'rb', 'g', 'br'],
         ['r', 'rb', 'gb', 'r']]
        >>> list(decompose_design_all('bwurrg', example_patterns))
        [['bwu', 'r', 'r', 'g']]
        >>> list(decompose_design_all('bwurrg', example_patterns))
        [['bwu', 'r', 'r', 'g']]
        >>> list(decompose_design_all('brgr', example_patterns))
        [['b', 'r', 'g', 'r'], ['br', 'g', 'r']]
        >>> list(decompose_design_all('ubwu', example_patterns))
        []
        >>> list(decompose_design_all('bbrgwb', example_patterns))
        []

    Adding up all of the ways the towels in this example could be arranged into the desired designs
    yields **`16`** (`2 + 1 + 4 + 6 + 1 + 2`).

        >>> sum(count_decompositions(des, example_patterns) for des in example_designs)
        16

    They'll let you into the onsen as soon as you have the list.
    **What do you get if you add up the number of different ways you could make each design?**

        >>> part_2(patterns=example_patterns, designs=example_designs)
        part 2: there is total of 16 different ways to make all the designs
        16
    """

    result = sum(count_decompositions(des, patterns) for des in designs)

    print(f"part 2: there is total of {result} different ways to make all the designs")
    return result


def decompose_design(design: Design, patterns: Patterns) -> list[Pattern] | None:
    patterns_sorted = tuple(sorted(patterns, key=lambda pat: -len(pat)))
    return _decompose_design_lru(design, patterns_sorted)


@lru_cache(maxsize=None)
def _decompose_design_lru(design: Design, patterns: tuple[Pattern, ...]) -> list[Pattern] | None:
    if not design:
        return []

    for pat in patterns:
        if design.startswith(pat):
            subsol = _decompose_design_lru(design.removeprefix(pat), patterns)
            if subsol is not None:
                return [pat] + subsol

    return None


def decompose_design_all(design: Design, patterns: Patterns) -> Iterable[list[Pattern]]:
    if not design:
        yield []
        return

    yield from (
        [pat] + subsol
        for pat in patterns
        if design.startswith(pat)
        for subsol in decompose_design_all(design.removeprefix(pat), patterns)
    )


def count_decompositions(design: Design, patterns: Patterns) -> int:
    return _count_decompositions_lru(design, tuple(patterns))


@lru_cache(maxsize=None)
def _count_decompositions_lru(design: Design, patterns: tuple[Pattern, ...]) -> int:
    if not design:
        return 1

    return sum(
        _count_decompositions_lru(design.removeprefix(pat), patterns)
        for pat in patterns
        if design.startswith(pat)
    )


def input_from_file(fn: str) -> tuple[Patterns, Designs]:
    return input_from_lines(open(relative_path(__file__, fn)))


def input_from_text(text: str) -> tuple[Patterns, Designs]:
    return input_from_lines(text.strip().splitlines())


def input_from_lines(lines: Iterable[str]) -> tuple[Patterns, Designs]:
    lines_it = iter(lines)

    patterns_line = next(lines_it).strip()
    patterns = patterns_line.split(sep=', ')

    assert not next(lines_it).strip()  # empty line

    designs = [line.strip() for line in lines_it]

    return patterns, designs


def main(input_fn: str = 'data/19-input.txt') -> tuple[int, int]:
    patterns, designs = input_from_file(input_fn)
    result_1 = part_1(patterns, designs)
    result_2 = part_2(patterns, designs)
    return result_1, result_2


if __name__ == '__main__':
    main()
