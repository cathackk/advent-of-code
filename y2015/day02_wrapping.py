"""
Advent of Code 2015
Day 2: I Was Told There Would Be No Math
https://adventofcode.com/2015/day/2
"""

from typing import Iterable

from common.utils import relative_path


Dimension = tuple[int, int, int]


def part_1(dimensions: Iterable[Dimension]) -> int:
    """
    The elves are running low on wrapping paper, and so they need to submit an order for more. They
    have a list of the dimensions (length `l`, width `w`, and height `h`) of each present, and only
    want to order exactly as much as they need.

    Fortunately, every present is a box (a perfect right rectangular prism), which makes calculating
    the required wrapping paper for each gift a little easier: find the surface area of the box,
    which is `2*l*w + 2*w*h + 2*h*l`. The elves also need a little extra paper for each present:
    the area of the smallest side.

    For example:

      - A present with dimensions `2x3x4` requires `2*6 + 2*12 + 2*8 = 52` square feet of wrapping
        paper plus `6` square feet of slack, for a total of `58` square feet.

        >>> paper(2, 3, 4)
        58

      - A present with dimensions `1x1x10` requires `2*1 + 2*10 + 2*10 = 42` square feet of wrapping
        paper plus `1` square foot of slack, for a total of `43` square feet.

        >>> paper(1, 1, 10)
        43

    All numbers in the elves' list are in feet. How many total **square feet of wrapping paper**
    should they order?

        >>> part_1([(2, 3, 4), (1, 1, 10)])
        part 1: gifts need total 101 square feet of wrapping paper
        101
    """

    result = sum(paper(*dim) for dim in dimensions)
    print(f"part 1: gifts need total {result} square feet of wrapping paper")
    return result


def part_2(dimensions: Iterable[Dimension]) -> int:
    """
    The elves are also running low on ribbon. Ribbon is all the same width, so they only have to
    worry about the length they need to order, which they would again like to be exact.

    The ribbon required to wrap a present is the shortest distance around its sides, or the smallest
    perimeter of any one face. Each present also requires a bow made out of ribbon as well; the feet
    of ribbon required for the perfect bow is equal to the cubic feet of volume of the present.
    Don't ask how they tie the bow, though; they'll never tell.

    For example:

      - A present with dimensions `2x3x4` requires `2+2+3+3 = 10` feet of ribbon to wrap the present
        plus `2*3*4 = 24` feet of ribbon for the bow, for a total of `34` feet.

        >>> ribbon(2, 3, 4)
        34

      - A present with dimensions `1x1x10` requires `1+1+1+1 = 4` feet of ribbon to wrap the present
        plus `1*1*10 = 10` feet of ribbon for the bow, for a total of `14` feet.

        >>> ribbon(1, 1, 10)
        14

    How many total **feet of ribbon** should they order?

        >>> part_2([(2, 3, 4), (1, 1, 10)])
        part 2: gifts need total 48 feet of ribbon
        48
    """

    result = sum(ribbon(*dim) for dim in dimensions)
    print(f"part 2: gifts need total {result} feet of ribbon")
    return result


def paper(length: int, width: int, height: int) -> int:
    lw = length * width
    wh = width * height
    hl = height * length
    smallest = min([lw, wh, hl])
    return 2 * (lw + wh + hl) + smallest


def ribbon(length: int, width: int, height: int) -> int:
    a, b, c = sorted([length, width, height])
    return (2 * a) + (2 * b) + (a * b * c)


def dimensions_from_file(fn: str) -> list[Dimension]:
    return list(dimensions_from_lines(open(relative_path(__file__, fn))))


def dimensions_from_lines(lines: Iterable[str]) -> Iterable[Dimension]:
    for line in lines:
        l, w, h = line.split('x')
        yield int(l), int(w), int(h)


if __name__ == '__main__':
    dimensions_ = dimensions_from_file('data/02-input.txt')
    part_1(dimensions_)
    part_2(dimensions_)
