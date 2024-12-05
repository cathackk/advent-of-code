"""
Advent of Code 2023
Day 12: Hot Springs
https://adventofcode.com/2023/day/12
"""

from functools import lru_cache
from typing import Iterable

from common.file import relative_path


def part_1(rows: list['Row']) -> int:
    r"""
    You finally reach the hot springs! You can see steam rising from secluded areas attached to
    the primary, ornate building.

    As you turn to enter, the researcher stops you. "Wait - I thought you were looking for the hot
    springs, weren't you?" You indicate that this definitely looks like hot springs to you.

    "Oh, sorry, common mistake! This is actually the onsen! The hot springs are next door."

    You look in the direction the researcher is pointing and suddenly notice the massive metal
    helixes towering overhead. "This way!"

    It only takes you a few more steps to reach the main gate of the massive fenced-off area
    containing the springs. You go through the gate and into a small administrative building.

    "Hello! What brings you to the hot springs today? Sorry they're not very hot right now; we're
    having a **lava shortage** at the moment." You ask about the missing machine parts for Desert
    Island.

    "Oh, all of Gear Island is currently offline! Nothing is being manufactured at the moment, not
    until we get more lava to heat our forges. And our springs. The springs aren't very springy
    unless they're hot!"

    "Say, could you go up and see why the lava stopped flowing? The springs are too cold for normal
    operation, but we should be able to find one springy enough to launch **you** up there!"

    There's just one problem - many of the springs have fallen into disrepair, so they're not
    actually sure which springs would even be **safe** to use! Worse yet, their **condition records
    of which springs are damaged** (your puzzle input) are also damaged! You'll need to help them
    repair the damaged records.

    In the giant field just outside, the springs are arranged into **rows**. For each row, the
    condition records show every spring and whether it is **operational** (`.`) or **damaged**
    (`#`). This is the part of the condition records that is itself damaged; for some springs, it is
    simply **unknown** (`?`) whether the spring is operational or damaged.

    However, the engineer that produced the condition records also duplicated some of this
    information in a different format! After the list of springs for a given row, the size of each
    **contiguous group of damaged springs** is listed in the order those groups appear in the row.
    This list always accounts for every damaged spring, and each number is the entire size of its
    contiguous group (that is, groups are always separated by at least one operational spring:
    `####` would always be `4`, never `2,2`).

    So, condition records with no unknown spring conditions might look like this:

        >>> list(annotate('#.#.###'))
        [1, 1, 3]
        >>> list(annotate('#...#....###.'))
        [1, 1, 3]
        >>> list(annotate('#.###.#.######'))
        [1, 3, 1, 6]
        >>> list(annotate('####.#...#...'))
        [4, 1, 1]
        >>> list(annotate('#....######..#####.'))
        [1, 6, 5]
        >>> list(annotate('###.##....#'))
        [3, 2, 1]

    However, the condition records are partially damaged; some of the springs' conditions are
    actually **unknown** (`?`). For example:

        >>> rows_ = rows_from_text('''
        ...     ???.### 1,1,3
        ...     .??..??...?##. 1,1,3
        ...     ?#?#?#?#?#?#?#? 1,3,1,6
        ...     ????.#...#... 4,1,1
        ...     ????.######..#####. 1,6,5
        ...     ?###???????? 3,2,1
        ... ''')
        >>> len(rows_)
        6

    Equipped with this information, it is your job to figure out **how many different arrangements**
    of operational and broken springs fit the given criteria in each row.

    In the first line, there is exactly **one** way separate groups of one, one, and three broken
    springs (in that order) can appear in that row: the first three unknown springs must be broken,
    then operational, then broken (`#.#`), making the whole row `#.#.###`:

        >>> rows_[0]
        ('???.###', [1, 1, 3])
        >>> list(solutions(rows_[0]))
        ['#.#.###']

    The second line is more interesting. It could be a total of **four** different arrangements.
    The last `?` must always be broken (to satisfy the final contiguous group of three broken
    springs), and each `??` must hide exactly one of the two broken springs. (Neither `??` could be
    both broken springs or they would form a single contiguous group of two; if that were true, the
    numbers afterward would have been `2,3` instead.) Since each `??` can either be `#.` or `.#`,
    there are four possible arrangements of springs:

        >>> rows_[1]
        ('.??..??...?##.', [1, 1, 3])
        >>> list(solutions(rows_[1]))  # doctest: +NORMALIZE_WHITESPACE
        ['.#...#....###.',
         '.#....#...###.',
         '..#..#....###.',
         '..#...#...###.']

    The last line is actually consistent with **ten** different arrangements! Because the first
    number is `3`, the first and second `?` must both be `.` (if either were `#`, the first number
    would have to be `4` or higher). However, the remaining run of unknown spring conditions have
    many different ways they could hold groups of two and one broken springs:

        >>> rows_[-1]
        ('?###????????', [3, 2, 1])
        >>> print('\n'.join(solutions(rows_[-1])))
        .###.##.#...
        .###.##..#..
        .###.##...#.
        .###.##....#
        .###..##.#..
        .###..##..#.
        .###..##...#
        .###...##.#.
        .###...##..#
        .###....##.#

    In this example, the number of possible arrangements for each row is:

        >>> [solutions_count(row) for row in rows_]
        [1, 4, 1, 1, 4, 10]
        >>> sum(_)
        21

    For each row, count all of the different arrangements of operational and broken springs that
    meet the given criteria. **What is the sum of those counts?**

        >>> part_1(rows_)
        part 1: there is total 21 solutions
        21
    """

    result = sum(solutions_count(row) for row in rows)

    print(f"part 1: there is total {result} solutions")
    return result


def part_2(rows: list['Row']) -> int:
    """
    As you look out at the field of springs, you feel like there are way more springs than the
    condition records list. When you examine the records, you discover that they were actually
    **folded up** this whole time!

    To **unfold the records**, on each row, replace the list of spring conditions with five copies
    of itself (separated by `?`) and replace the list of contiguous groups of damaged springs with
    five copies of itself (separated by `,`).


        >>> unfolded(('.#', [1]))
        ('.#?.#?.#?.#?.#', [1, 1, 1, 1, 1])

    The first line of the above example would become:

        >>> rows_ = rows_from_file('data/12-example.txt')
        >>> unfolded(rows_[0])
        ('???.###????.###????.###????.###????.###', [1, 1, 3, 1, 1, 3, 1, 1, 3, 1, 1, 3, 1, 1, 3])

    In the above example, after unfolding, the number of possible arrangements for some rows is now
    much larger:

        >>> [solutions_count(unfolded(row)) for row in rows_]
        [1, 16384, 1, 16, 2500, 506250]

    After unfolding, adding all of the possible arrangement counts together produces:

        >>> sum(_)
        525152

    Unfold your condition records; **what is the new sum of possible arrangement counts?**

        >>> part_2(rows_)
        part 2: after unfolding, there is total 525152 solutions
        525152
    """

    result = sum(solutions_count(unfolded(row)) for row in rows)

    print(f"part 2: after unfolding, there is total {result} solutions")
    return result


Record = str
Hints = list[int]
Row = tuple[Record, Hints]


def solutions(row: Row) -> Iterable[Record]:
    record, hints = row

    if '?' not in record:
        if list(annotate(record)) == hints:
            yield record
        return

    if not hints:
        if not any(char == '#' for char in record):
            yield len(record) * '.'
        return

    hint, remaining_hints = hints[0], hints[1:]
    min_groups_length = sum(hints) + len(hints) - 1
    for pos in range(len(record) - min_groups_length + 1):
        # previous char cannot be `#` -> abort
        if pos > 0 and record[pos-1] == '#':
            break
        # current group cannot contain `.` -> go on
        if any(char == '.' for char in record[pos:pos+hint]):
            continue
        # following char cannot be `#` -> go on
        if pos + hint < len(record) and record[pos + hint] == '#':
            continue

        # all is fine -> yield subsolutions
        placed_part = '.' * pos + '#' * hint + ('.' if remaining_hints else '')
        remaining_part = record[len(placed_part):]
        for subsolution in solutions((remaining_part, remaining_hints)):
            yield placed_part + subsolution


def solutions_count(row: Row) -> int:
    record, hints = row
    return _solutions_count_memoized(record, tuple(hints))


@lru_cache(maxsize=None)
def _solutions_count_memoized(record: Record, hints: tuple[int, ...]) -> int:
    if '?' not in record:
        return int(tuple(annotate(record)) == hints)
    if not hints:
        return int(not any(char == '#' for char in record))

    counter = 0
    hint, remaining_hints = hints[0], hints[1:]
    min_groups_length = sum(hints) + len(hints) - 1
    for pos in range(len(record) - min_groups_length + 1):
        # previous char cannot be `#` -> abort
        if pos > 0 and record[pos-1] == '#':
            break
        # current group cannot contain `.` -> go on
        if any(char == '.' for char in record[pos:pos+hint]):
            continue
        # following char cannot be `#` -> go on
        if pos + hint < len(record) and record[pos + hint] == '#':
            continue
        # all is fine -> add solutions
        placed_part = '.' * pos + '#' * hint + ('.' if remaining_hints else '')
        remaining_part = record[len(placed_part):]
        counter += _solutions_count_memoized(remaining_part, remaining_hints)

    return counter


def annotate(record: Iterable[str]) -> Iterable[int]:
    group_count = 0
    for char in record:
        if char == '#':
            group_count += 1
        elif char == '.':
            if group_count:
                yield group_count
            group_count = 0
        else:
            raise ValueError(char)
    if group_count:
        yield group_count


def unfolded(row: Row, copies: int = 5) -> Row:
    record, hints = row
    return '?'.join(record for _ in range(copies)), hints * copies


def rows_from_file(fn: str) -> list[Row]:
    return list(rows_from_lines(open(relative_path(__file__, fn))))


def rows_from_text(text: str) -> list[Row]:
    return list(rows_from_lines(text.strip().splitlines()))


def rows_from_lines(lines: Iterable[str]) -> Iterable[Row]:
    for line in lines:
        record, hints = line.strip().split(' ')
        yield record, [int(v) for v in hints.split(',')]


def main(input_fn: str = 'data/12-input.txt') -> tuple[int, int]:
    rows = rows_from_file(input_fn)
    result_1 = part_1(rows)
    result_2 = part_2(rows)
    return result_1, result_2


if __name__ == '__main__':
    main()
