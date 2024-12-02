"""
Advent of Code 2024
Day 2: Red-Nosed Reports
https://adventofcode.com/2024/day/2
"""

from typing import Iterable

from common.file import relative_path
from common.iteration import diffs, omitting


def part_1(reports: Iterable['Report']) -> int:
    """
    Fortunately, the first location The Historians want to search isn't a long walk from the Chief
    Historian's office.

    While the Red-Nosed Reindeer nuclear fusion/fission plant (y2015/day19_medicine.py) appears to
    contain no sign of the Chief Historian, the engineers there run up to you as soon as they see
    you. Apparently, they **still** talk about the time Rudolph was saved through molecular
    synthesis from a single electron.

    They're quick to add that - since you're already here - they'd really appreciate your help
    analyzing some unusual data from the Red-Nosed reactor. You turn to check if The Historians are
    waiting for you, but they seem to have already divided into groups that are currently searching
    every corner of the facility. You offer to help with the unusual data.

    The unusual data (your puzzle input) consists of many **reports**, one report per line.
    Each report is a list of numbers called **levels** that are separated by spaces. For example:

        >>> example_reports = reports_from_text('''
        ...     7 6 4 2 1
        ...     1 2 7 8 9
        ...     9 7 6 2 1
        ...     1 3 2 4 5
        ...     8 6 4 4 1
        ...     1 3 6 7 9
        ... ''')

    This example data contains six reports each containing five levels.

        >>> [len(report) for report in example_reports]
        [5, 5, 5, 5, 5, 5]

    The engineers are trying to figure out which reports are **safe**. The Red-Nosed reactor safety
    systems can only tolerate levels that are either gradually increasing or gradually decreasing.
    So, a report only counts as safe if both of the following are true:

      - The levels are either **all increasing** or **all decreasing**.
      - Any two adjacent levels differ by **at least one** and **at most three**.

    In the example above, the reports can be found safe or unsafe by checking those rules:

      - **Safe** because the levels are all decreasing by 1 or 2:

        >>> example_reports[0]
        [7, 6, 4, 2, 1]
        >>> is_safe(example_reports[0])
        True

      - **Unsafe** because `2 7` is an increase of `5`:

        >>> example_reports[1]
        [1, 2, 7, 8, 9]
        >>> is_safe(example_reports[1])
        False

      - **Unsafe** because `6 2` is a decrease of `4`:

        >>> example_reports[2]
        [9, 7, 6, 2, 1]
        >>> is_safe(example_reports[2])
        False

      - **Unsafe** because `1 3` is increasing but `3 2` is decreasing:

        >>> example_reports[3]
        [1, 3, 2, 4, 5]
        >>> is_safe(example_reports[3])
        False

      - **Unsafe** because `4 4` is neither an increase nor a decrease:

        >>> example_reports[4]
        [8, 6, 4, 4, 1]
        >>> is_safe(example_reports[4])
        False

      - **Safe** because the levels are all increasing by 1, 2, or 3:

        >>> example_reports[5]
        [1, 3, 6, 7, 9]
        >>> is_safe(example_reports[5])
        True

    So, in this example, **`2`** reports are **safe**:

        >>> sum(1 for report in example_reports if is_safe(report))
        2

    Analyze the unusual data from the engineers. **How many reports are safe?**

        >>> part_1(example_reports)
        part 1: there are 2 safe reports
        2
    """

    result = sum(1 for report in reports if is_safe(report))

    print(f"part 1: there are {result} safe reports")
    return result


def part_2(reports: Iterable['Report']) -> int:
    """
    The engineers are surprised by the low number of safe reports until they realize they forgot to
    tell you about the Problem Dampener.

    The Problem Dampener is a reactor-mounted module that lets the reactor safety systems
    **tolerate a single bad level** in what would otherwise be a safe report. It's like the bad
    level never happened!

    Now, the same rules apply as before, except if removing a single level from an unsafe report
    would make it safe, the report instead counts as safe.

    More of the above example's reports are now safe:

        >>> example_reports = reports_from_file('data/02-example.txt')

      - **Safe** without removing any level:

        >>> example_reports[0]
        [7, 6, 4, 2, 1]
        >>> is_safe(example_reports[0], tolerance=1)
        True

      - **Unsafe** regardless of which level is removed:

        >>> example_reports[1]
        [1, 2, 7, 8, 9]
        >>> is_safe(example_reports[1], tolerance=1)
        False

      - **Unsafe** regardless of which level is removed:

        >>> example_reports[2]
        [9, 7, 6, 2, 1]
        >>> is_safe(example_reports[2], tolerance=1)
        False

      - **Safe** by removing the second level, `3`:

        >>> example_reports[3]
        [1, 3, 2, 4, 5]
        >>> is_safe([1, 2, 4, 5], tolerance=0)
        True
        >>> is_safe(example_reports[3], tolerance=1)
        True

      - **Safe** by removing the third level, `4`:

        >>> example_reports[4]
        [8, 6, 4, 4, 1]
        >>> is_safe([8, 6, 4, 1], tolerance=0)
        True
        >>> is_safe(example_reports[4], tolerance=1)
        True

      - **Safe** without removing any level:

        >>> example_reports[5]
        [1, 3, 6, 7, 9]
        >>> is_safe(example_reports[5], tolerance=1)
        True

    Thanks to the Problem Dampener, **`4`** reports are actually **safe**!

        >>> sum(1 for report in example_reports if is_safe(report, tolerance=1))
        4

    And one more report that is not in the original example instructions, but that's a nice
    counter-example to some algorithms. This one would be safe after removing the second level, `5`:

        >>> ugly_report = [4, 5, 3, 2, 1]
        >>> is_safe(ugly_report)
        False
        >>> is_safe(ugly_report, tolerance=1)
        True

    Update your analysis by handling situations where the Problem Dampener can remove a single level
    from unsafe reports. **How many reports are now safe?**

        >>> part_2(example_reports)
        part 2: there are actually 4 safe reports
        4
    """

    result = sum(1 for report in reports if is_safe(report, tolerance=1))

    print(f"part 2: there are actually {result} safe reports")
    return result


Report = list[int]


def is_safe(report: Report, tolerance: int = 0) -> bool:
    assert tolerance >= 0
    if tolerance > 0:
        return any(is_safe(smaller_report) for smaller_report in omitting(report))

    assert len(report) >= 2
    increasing = report[0] < report[1]

    for diff in diffs(report):
        if not 0 < abs(diff) <= 3:
            return False
        if (diff > 0) != increasing:
            return False

    return True


def reports_from_file(fn: str) -> list[Report]:
    return list(reports_from_lines(open(relative_path(__file__, fn))))


def reports_from_text(text: str) -> list[Report]:
    return list(reports_from_lines(text.strip().splitlines()))


def reports_from_lines(lines: Iterable[str]) -> Iterable[Report]:
    return ([int(val) for val in line.split()] for line in lines)


def main(input_fn: str = 'data/02-input.txt') -> tuple[int, int]:
    reports = reports_from_file(input_fn)
    result_1 = part_1(reports)
    result_2 = part_2(reports)
    return result_1, result_2


if __name__ == '__main__':
    main()
