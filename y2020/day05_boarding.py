"""
Advent of Code 2020
Day 5: Binary Boarding
https://adventofcode.com/2020/day/5
"""

from typing import Iterable

from common.utils import maxk
from common.utils import single_value


def part_1(seat_codes: Iterable[str]) -> int:
    """
    This airline uses binary space partitioning to seat people. A seat might be specified like
    `FBFBBFFRLR`, where `F` means "front", `B` means "back", `L` means "left", and `R` means
    "right".

    The first 7 characters will either be `F` or `B`; these specify exactly one of the *128 rows*
    on the plane (numbered 0 through 127). Each letter tells you which half of a region the given
    seat is in. Start with the whole list of rows; the first letter indicates whether the seat is
    in the *front* (0 through 63) or the *back* (64 through 127). The next letter indicates which
    half of that region the seat is in, and so on until you're left with exactly one row.

    For example, consider just the first seven characters of `FBFBBFFRLR`:

        - Start by considering the whole range, rows `0` through `127`.
        - `F` means to take the lower half, keeping rows `0` through `63`.
        - `B` means to take the upper half, keeping rows `32` through `63`.
        - `F` means to take the lower half, keeping rows `32` through `47`.
        - `B` means to take the upper half, keeping rows `40` through `47`.
        - `B` keeps rows `44` through `47`.
        - `F` keeps rows `44` through `45`.
        - The final `F` keeps the lower of the two, row `44`.

        >>> row_number('FBFBBFF')
        44

    The last three characters will be either `L` or `R`; these specify exactly one of the 8 columns
    of seats on the plane (numbered `0` through `7`). The same process as above proceeds again,
    this time with only three steps. `L` means to keep the *lower half*, while `R` means to keep
    the *upper half*.

    For example, consider just the last 3 characters of `FBFBBFFRLR`:

        - Start by considering the whole range, columns `0` through `7`.
        - `R` means to take the upper half, keeping columns `4` through `7`.
        - `L` means to take the lower half, keeping columns `4` through `5`.
        - The final `R` keeps the upper of the two, column `5`.

        >>> column_number('RLR')
        5

    So, decoding `FBFBBFFRLR` reveals that it is the seat at *row `44`, column `5`*.

        >>> seat_coordinates('FBFBBFFRLR')
        (44, 5)

    Every seat also has a unique *seat ID*: multiply the row by 8, then add the column. In this
    example, the seat has ID `44 * 8 + 5 = 357`.

        >>> seat_id('FBFBBFFRLR')
        357

    Here are some other boarding passes:

        >>> passes = ['BFFFBBFRRR', 'FFFBBBFRRR', 'BBFFBBFRLL']
        >>> seat_coordinates(passes[0]), seat_id(passes[0])
        ((70, 7), 567)
        >>> seat_coordinates(passes[1]), seat_id(passes[1])
        ((14, 7), 119)
        >>> seat_coordinates(passes[2]), seat_id(passes[2])
        ((102, 4), 820)

    As a sanity check, look through your list of boarding passes. *What is the highest seat ID on
    a boarding pass?*

        >>> part_1(passes)
        part 1: boarding pass 'BBFFBBFRLL' has the highest seat ID: 820
        820
    """

    max_seat_code, max_seat_id = maxk(seat_codes, key=seat_id)

    print(f"part 1: boarding pass {max_seat_code!r} has the highest seat ID: {max_seat_id}")
    return max_seat_id


def part_2(seat_codes: Iterable[str]) -> int:
    """
    Your seat should be the only missing boarding pass in your list. However, there's a catch: some
    of the seats at the very front and back of the plane don't exist on this aircraft, so they'll
    be missing from your list as well.

    Your seat wasn't at the very front or back, though; the seats with IDs +1 and -1 from yours
    will be in your list.

    *What is the ID of your seat?*

        >>> passes = ['BFFFBBBLRL', 'BFFFBBFRRR', 'BFFFBBBLLL', 'BFFFBBBLRR']
        >>> sorted(seat_id(p) for p in passes)
        [567, 568, 570, 571]
        >>> part_2(passes)
        part 2: your seat ID is 569
        569
    """

    seat_ids = set(seat_id(code) for code in seat_codes)
    full_seat_ids = set(sid for sid in range(min(seat_ids), max(seat_ids) + 1))
    missing_seat_id = single_value(full_seat_ids - seat_ids)

    print(f"part 2: your seat ID is {missing_seat_id}")
    return missing_seat_id


def row_number(row_code: str) -> int:
    assert len(row_code) == 7
    assert all(ch in ('F', 'B') for ch in row_code)
    return int(row_code.replace('F', '0').replace('B', '1'), 2)


def column_number(column_code: str) -> int:
    assert len(column_code) == 3
    assert all(ch in ('L', 'R') for ch in column_code)
    return int(column_code.replace('L', '0').replace('R', '1'), 2)


def seat_coordinates(seat_code: str) -> tuple[int, int]:
    assert len(seat_code) == 10
    return row_number(seat_code[:7]), column_number(seat_code[7:])


def seat_id(seat_code: str) -> int:
    r, c = seat_coordinates(seat_code)
    return r * 8 + c


if __name__ == '__main__':
    passes_ = [line.strip() for line in open('data/05-input.txt')]
    part_1(passes_)
    part_2(passes_)
