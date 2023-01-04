"""
Advent of Code 2017
Day 3: Spiral Memory
https://adventofcode.com/2017/day/3
"""

from itertools import count
from typing import Iterable

from common import spiral
from meta.aoc_tools import data_path


def part_1(number: int) -> int:
    """
    You come across an experimental new kind of memory stored on an infinite two-dimensional grid.

    Each square on the grid is allocated in a spiral pattern starting at a location marked `1` and
    then counting up while spiraling outward. For example, the first few squares are allocated like
    this:

        >>> print(spiral.drawn(range(1, 26)))
        17  16  15  14  13
        18   5   4   3  12
        19   6 [ 1]  2  11
        20   7   8   9  10
        21  22  23  24  25

    While this is very space-efficient (no squares are skipped), requested data must be carried back
    to square 1 (the location of the only access port for this memory system) by programs that can
    only move up, down, left, or right. They always take the shortest path: the Manhattan Distance
    between the location of the data and square `1`.

    For example:

        >>> distance(1)
        0
        >>> distance(12)
        3
        >>> distance(23)
        2
        >>> distance(1024)
        31

    **How many steps** are required to carry the data from the square identified in your puzzle
    input all the way to the access port?

        >>> part_1(1024)
        part 1: number 1024 is 31 steps away
        31
    """

    result = distance(number)
    print(f"part 1: number {number} is {result} steps away")
    return result


def part_2(number: int) -> int:
    """
    As a stress test on the system, the programs here clear the grid and then store the value `1` in
    square `1`. Then, in the same allocation order as shown above, they store the sum of the values
    in all adjacent squares, including diagonals.

    So, the first few squares' values are chosen as follows:

      - Square `1` starts with the value `1`.
      - Square `2` has only one adjacent filled square (with value `1`), so it also stores `1`.
      - Square `3` has both of the above squares as neighbors and stores the sum of their values,
        `2`.
      - Square `4` has all three of the aforementioned squares as neighbors and stores the sum of
        their values, `4`.
      - Square `5` only has the first and fourth squares as neighbors, so it gets the value `5`.

        >>> from itertools import islice
        >>> list(islice(sum_spiral_sequence(), 5))
        [1, 1, 2, 4, 5]

    Once a square is written, its value does not change. Therefore, the first few squares would
    receive the following values:

        >>> print(spiral.drawn(islice(sum_spiral_sequence(), 25)))
        147  142  133  122   59
        304    5    4    2   57
        330   10 [  1]   1   54
        351   11   23   25   26
        362  747  806  880  931

    What is the **first value written** that is **larger** than your puzzle input?

        >>> part_2(800)
        part 2: first value larger than 800 is 806
        806
    """

    result = next(n for n in sum_spiral_sequence() if n > number)
    print(f"part 2: first value larger than {number} is {result}")
    return result


def distance(number: int, from_number: int = 1) -> int:
    x1, y1 = spiral.to_pos(number - 1)
    x2, y2 = spiral.to_pos(from_number - 1)
    return abs(x1 - x2) + abs(y1 - y2)


def sum_spiral_sequence(start: int = 1) -> Iterable[int]:
    spiral_grid = {(0, 0): start}
    yield start

    def neighbors(pos: tuple[int, int]) -> Iterable[int]:
        x, y = pos
        return (
            spiral_grid[npos]
            for dx in (-1, 0, +1)
            for dy in (-1, 0, +1)
            if (npos := (x + dx, y + dy)) != pos
            if npos in spiral_grid
        )

    for index in count(1):
        current_pos = spiral.to_pos(index)
        neighboring = list(neighbors(current_pos))
        new_num = sum(neighboring)
        yield new_num
        spiral_grid[current_pos] = new_num


def number_from_file(fn: str) -> int:
    return int(open(fn).readline().strip())


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    number = number_from_file(input_path)
    result_1 = part_1(number)
    result_2 = part_2(number)
    return result_1, result_2


if __name__ == '__main__':
    main()
