"""
Advent of Code 2017
Day 14: Disk Defragmentation
https://adventofcode.com/2017/day/14
"""

from typing import Iterable

from common.file import relative_path
from common.iteration import ilen
from y2017.day10_knots import knot_hash


def part_1(key: str) -> int:
    """
    Suddenly, a scheduled job activates the system's disk defragmenter. Were the situation
    different, you might sit and watch it for a while, but today, you just don't have that kind of
    time. It's soaking up valuable system resources that are needed elsewhere, and so the only
    option is to help it finish its task as soon as possible.

    The disk in question consists of a 128x128 grid; each square of the grid is either **free** or
    **used**. On this disk, the state of the grid is tracked by the bits in a sequence of
    [knot hashes](./day10_knots.py).

    A total of 128 knot hashes are calculated, each corresponding to a single row in the grid; each
    hash contains 128 bits which correspond to individual grid squares. Each bit of a hash indicates
    whether that square is **free** (0) or **used** (1).

    The hash inputs are a key string (your puzzle input), a dash, and a number from `0` to `127`
    corresponding to the row. For example, if your key string were `flqrgnkx`, then the first row
    would be given by the bits of the knot hash of `flqrgnkx-0`, the second row from the bits of the
    knot hash of `flqrgnkx-1`, and so on until the last row, `flqrgnkx-127`.

    The output of a knot hash is traditionally represented by 32 hexadecimal digits; each of these
    digits correspond to 4 bits, for a total of `4 * 32 = 128` bits. To convert to bits, turn each
    hexadecimal digit to its equivalent binary value, high-bit first: `0` becomes `0000`,
    `1` becomes `0001`, `e` becomes `1110`, `f` becomes `1111`, and so on; a hash that begins with
    `a0c2017...` in hexadecimal would begin with `1010000011000010000000010111...` in binary.

        >>> format(int('a0c2017', base=16), "08b")
        '1010000011000010000000010111'

    Continuing this process, the **first 8 rows and columns** for key `flqrgnkx` appear as follows,
    using `#` to denote used squares, and `·` to denote free ones:

        >>> print_grid(key='flqrgnkx', rows=8, columns=8)
        ##·#·#··->
        ·#·#·#·#
        ····#·#·
        #·#·##·#
        ·##·#···
        ##··#··#
        ·#···#··
        ##·#·##·->
        ↓      ↓

    In this example, `8108` squares are used across the entire 128x128 grid.

        >>> count_used('flqrgnkx')
        8108

    Given your actual key string, **how many squares are used**?

        >>> part_1('flqrgnkx')
        part 1: 8108 used squares
        8108
    """

    result = count_used(key)
    print(f"part 1: {result} used squares")
    return result


def part_2(key: str) -> int:
    """
    Now, all the defragmenter needs to know is the number of **regions**. A region is a group of
    **used** squares that are all **adjacent**, not including diagonals. Every used square is in
    exactly one region: lone used squares form their own isolated regions, while several adjacent
    squares all count as a single region.

    In the example above, the following nine regions are visible, each marked with a distinct digit:

        >>> print_grid('flqrgnkx', rows=8, columns=8, show_regions=True)
        11·2·3··->
        ·1·2·3·4
        ····5·6·
        7·8·55·9
        ·88·5···
        88··5··8
        ·8···8··
        88·8·88·->
        ↓      ↓

    Of particular interest is the region marked `8`; while it does not appear contiguous in this
    small view, all of the squares marked `8` are connected when considering the whole 128x128 grid.
    In total, in this example, `1242` regions are present.

        >>> count_regions('flqrgnkx')
        1242

    How many regions are present given your key string?

        >>> part_2('flqrgnkx')
        part 2: 1242 regions
        1242
    """

    result = count_regions(key)
    print(f"part 2: {result} regions")
    return result


Pos = tuple[int, int]


def disk_rows(key: str, rows_count: int = 128) -> Iterable[bytes]:
    return (knot_hash(f'{key}-{r}'.encode()) for r in range(rows_count))


def count_used(key: str, rows_count: int = 128) -> int:
    return sum(bin(byte).count('1') for row in disk_rows(key, rows_count) for byte in row)


def count_regions(key: str) -> int:
    return ilen(create_regions(key))


def create_regions(key: str) -> Iterable[set[Pos]]:
    ones: set[Pos] = {
        (b * 8 + x, y)
        for y, row in enumerate(disk_rows(key))
        for b, byte in enumerate(row)
        for x, bit in enumerate(format(byte, '08b'))
        if bit == '1'
    }

    while ones:
        buffer: list[Pos] = [ones.pop()]
        region: set[Pos] = set()

        while buffer:
            pos = buffer.pop()
            region.add(pos)
            for npos in neighbors(pos):
                if npos in ones:
                    ones.remove(npos)
                    buffer.append(npos)

        yield region


def neighbors(pos: Pos) -> Iterable[Pos]:
    x, y = pos
    yield x, y - 1
    yield x, y + 1
    yield x - 1, y
    yield x + 1, y


def print_grid(
    key: str,
    rows: int = 128,
    columns: int = 128,
    char_free: str = '·',
    char_used: str = '#',
    show_regions: bool = False
) -> None:
    regions = [frozenset(region) for region in create_regions(key)]
    region_numbering: dict[frozenset[Pos], int] = {}

    used_squares = {square for region in regions for square in region}

    def char(pos: Pos) -> str:
        if pos not in used_squares:
            return char_free

        if not show_regions:
            return char_used

        pos_region = next(region for region in regions if pos in region)
        if pos_region not in region_numbering:
            region_numbering[pos_region] = max(region_numbering.values(), default=0) + 1

        return str(region_numbering[pos_region])

    for y in range(rows):
        row_str = ''.join(char((x, y)) for x in range(columns))
        suffix = "->" if columns < 128 and y in (0, rows - 1) else ""
        print(row_str + suffix)

    if rows < 128:
        print("↓" + " " * (columns - 2) + "↓")


def key_from_file(fn: str) -> str:
    return open(relative_path(__file__, fn)).readline().strip()


if __name__ == '__main__':
    key_ = key_from_file('data/14-input.txt')
    part_1(key_)
    part_2(key_)
