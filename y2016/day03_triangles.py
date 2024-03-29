"""
Advent of Code 2016
Day 3: Squares With Three Sides
https://adventofcode.com/2016/day/3
"""

from typing import Iterable

from common.iteration import chunks
from meta.aoc_tools import data_path


def part_1(triangles: list['Triangle']) -> int:
    """
    Now that you can think clearly, you move deeper into the labyrinth of hallways and office
    furniture that makes up this part of Easter Bunny HQ. This must be a graphic design department;
    the walls are covered in specifications for triangles.

    Or are they?

    The design document gives the side lengths of each triangle it describes, but... `5 10 25`? Some
    of these aren't triangles. You can't help but mark the impossible ones.

    In a valid triangle, the sum of any two sides must be larger than the remaining side.
    For example, the "triangle" given above is impossible, because 5 + 10 is not larger than 25.

        >>> is_possible((5, 10, 25))
        False
        >>> is_possible((10, 15, 20))
        True

    In your puzzle input, **how many** of the listed triangles are **possible**?

        >>> example = triangles_from_text('''
        ...      1  2  3
        ...      4  5  6
        ...      7  8  9
        ...     10 11 12
        ...     13 14 15
        ...     16 17 18
        ... ''')
        >>> example
        [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12), (13, 14, 15), (16, 17, 18)]

        >>> part_1(example)
        part 1: out of 6 triangles, 5 are possible
        5
    """

    possible_count = sum(1 for triangle in triangles if is_possible(triangle))
    print(f"part 1: out of {len(triangles)} triangles, {possible_count} are possible")
    return possible_count


def part_2(triangles: list['Triangle']) -> int:
    """
    Now that you've helpfully marked up their design documents, it occurs to you that triangles are
    specified in groups of three **vertically**. Each set of three numbers in a column specifies
    a triangle. Rows are unrelated.

    For example, given the following specification, numbers with the same hundreds digit would be
    part of the same triangle:

        >>> example = triangles_from_text('''
        ...     101 301 501
        ...     102 302 502
        ...     103 303 503
        ...     201 401 601
        ...     202 402 602
        ...     203 403 603
        ... ''')
        >>> example  # doctest: +NORMALIZE_WHITESPACE
        [(101, 301, 501), (102, 302, 502), (103, 303, 503),
         (201, 401, 601), (202, 402, 602), (203, 403, 603)]
        >>> list(transposed(example))  # doctest: +NORMALIZE_WHITESPACE
        [(101, 102, 103), (301, 302, 303), (501, 502, 503),
         (201, 202, 203), (401, 402, 403), (601, 602, 603)]

    In your puzzle input, and instead reading by columns, **how many** of the listed triangles
    are **possible**?

        >>> part_2(triangles_from_file(data_path(__file__, 'example.txt')))
        part 2: out of 6 triangles, 3 are possible
        3
    """

    possible_count = sum(1 for triangle in transposed(triangles) if is_possible(triangle))
    print(f"part 2: out of {len(triangles)} triangles, {possible_count} are possible")
    return possible_count


Triangle = tuple[int, int, int]


def is_possible(triangle: Triangle):
    a, b, c = triangle
    return a < b + c and b < c + a and c < a + b


def transposed(triangles: Iterable[Triangle]) -> Iterable[Triangle]:
    return (
        tt
        for t_1, t_2, t_3 in chunks(triangles, 3)
        for tt in zip(t_1, t_2, t_3)
    )


def triangles_from_text(text: str) -> list[Triangle]:
    return list(triangles_from_lines(text.strip().splitlines()))


def triangles_from_file(fn: str) -> list[Triangle]:
    return list(triangles_from_lines(open(fn)))


def triangles_from_lines(lines: Iterable[str]) -> Iterable[Triangle]:
    for line in lines:
        a, b, c = line.strip().split()
        yield int(a), int(b), int(c)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    triangles = triangles_from_file(input_path)
    result_1 = part_1(triangles)
    result_2 = part_2(triangles)
    return result_1, result_2


if __name__ == '__main__':
    main()
