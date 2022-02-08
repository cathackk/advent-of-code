"""
Advent of Code 2018
Day 11: Chronal Charge
https://adventofcode.com/2018/day/11
"""

from functools import lru_cache

from tqdm import tqdm

from common.file import relative_path
from common.iteration import maxk
from common.rect import Rect


def part_1(serial: int) -> str:
    """
    You watch the Elves and their sleigh fade into the distance as they head toward the North Pole.

    Actually, you're the one fading. The falling sensation returns.

    The low fuel warning light is illuminated on your wrist-mounted device. Tapping it once causes
    it to project a hologram of the situation: a **300x300** grid of fuel cells and their current
    power levels, some negative. You're not sure what negative power means in the context of time
    travel, but it can't be good.

    Each fuel cell has a coordinate ranging **from 1 to 300** in both the X (horizontal) and Y
    (vertical) direction. In `X,Y` notation, the top-left cell is `1,1`, and the top-right cell is
    `300,1`.

    The interface lets you select **any 3x3 square** of fuel cells. To increase your chances of
    getting to your destination, you decide to choose the 3x3 square with **the largest total
    power**.

    The power level in a given fuel cell can be found through the following process:

      - Find the fuel cell's **rack ID**, which is its **X coordinate plus 10**.
      - Begin with a power level of the **rack ID** times the **Y coordinate**.
      - Increase the power level by the value of the **grid serial number** (your puzzle input).
      - Set the power level to itself multiplied by the **rack ID**.
      - Keep only the **hundreds digit** of the power level (so `12345` becomes `3`; numbers with no
        hundreds digit become `0`).
      - **Subtract 5** from the power level.

    For example, to find the power level of the fuel cell at `3,5` in a grid with serial number `8`:

      - The rack ID is `3 + 10 = 13`.
      - The power level starts at `13 * 5 = 65`.
      - Adding the serial number produces `65 + 8 = 73`.
      - Multiplying by the rack ID produces `73 * 13 = 949`.
      - The hundreds digit of `949` is `9`.
      - Subtracting `5` produces `9 - 5 = 4`.

    So, the power level of this fuel cell is 4.

        >>> power_level(x=3, y=5, serial=8)
        4

    Here are some more example power levels:

        >>> power_level(122, 79, serial=57)
        -5
        >>> power_level(217, 196, serial=39)
        0
        >>> power_level(101, 153, serial=71)
        4

    Your goal is to find the 3x3 square which has the largest total power. The square must be
    entirely within the 300x300 grid. Identify this square using the `X,Y` coordinate of its
    **top-left fuel cell**. For example:

    For grid serial number `18`, the largest total 3x3 square has a top-left corner of **`33,45`**
    (with a total power of `29`):

        >>> max_square(serial=18)
        ((33, 45, 3), 29)

    These fuel cells appear in the middle of this 5x5 region:

        >>> draw_region(x=33, y=45, serial=18, square_size=3, margin=1)
        -2  -4   4   4   4
        -4 [ 4   4   4] -5
         4 [ 3   3   4] -4
         1 [ 1   2   4] -3
        -1   0   2  -5  -2

    For grid serial number `42`, the largest 3x3 square's top-left is `21,61` (with a total power of
    `30`):

        >>> max_square(serial=42)
        ((21, 61, 3), 30)

    They are in the middle of this region:

        >>> draw_region(x=21, y=61, serial=42)
        -3   4   2   2   2
        -4 [ 4   3   3]  4
        -5 [ 3   3   4] -4
         4 [ 3   3   4] -3
         3   3   3  -5  -1

    **What is the `X,Y` coordinate of the top-left fuel cell of the 3x3 square with the largest
    total power?**

        >>> part_1(serial=42)
        part 1: square with the largest power (30) is at 21,61
        '21,61'
    """

    (x, y, size), total_power = max_square(serial)
    assert size == 3
    square_identifier = f"{x},{y}"
    print(f"part 1: square with the largest power ({total_power}) is at {square_identifier}")
    return square_identifier


def part_2(serial: int) -> str:
    """
    You discover a dial on the side of the device; it seems to let you select a square of **any
    size**, not just 3x3. Sizes from 1x1 to 300x300 are supported.

    Realizing this, you now must find the **square of any size with the largest total power**.
    Identify this square by including its size as a third parameter after the top-left coordinate:
    a 9x9 square with a top-left corner of `3,5` is identified as `3,5,9`.

    For example:

      - For grid serial number `18`, the largest total square (with a total power of `113`) is
        `16x16` and has a top-left corner of `90,269`, so its identifier is **`90,269,16`**:

        >>> max_square(serial=18, square_size=ANY_SQUARE_SIZE)
        ((90, 269, 16), 113)

      - For grid serial number `42`, the largest total square (with a total power of `119`) is
        `12x12` and has a top-left corner of `232,251`, so its identifier is **`232,251,12`**:

        >>> max_square(serial=42, square_size=ANY_SQUARE_SIZE)
        ((232, 251, 12), 119)

    **What is the `X,Y,size` identifier of the square with the largest total power?**

        >>> part_2(serial=42)
        part 2: square with the largest power (119) is at 232,251,12
        '232,251,12'
    """

    (x, y, size), total_power = max_square(serial=serial, square_size=ANY_SQUARE_SIZE)
    square_identifier = f"{x},{y},{size}"
    print(f"part 2: square with the largest power ({total_power}) is at {square_identifier}")
    return square_identifier


def power_level(x: int, y: int, serial: int) -> int:
    return (((x + 10) * y + serial) * (x + 10)) // 100 % 10 - 5


@lru_cache(maxsize=None)
def square_sum(x: int, y: int, size: int, serial: int) -> int:
    assert size >= 0
    if size == 0:
        return 0

    elif size == 1:
        return power_level(x, y, serial)

    elif size % 2 == 0:
        # AABB
        # AABB
        # CCDD
        # CCDD
        hgh = size // 2
        return (
            square_sum(x, y, hgh, serial)                # A
            + square_sum(x + hgh, y, hgh, serial)        # B
            + square_sum(x, y + hgh, hgh, serial)        # C
            + square_sum(x + hgh, y + hgh, hgh, serial)  # D
        )

    else:
        # AAABB
        # AAABB
        # AAXDD
        # CCDDD
        # CCDDD
        h_2 = size // 2
        h_1 = size - h_2
        return (
            square_sum(x, y, h_1, serial)                # A
            + square_sum(x + h_1, y, h_2, serial)        # B
            + square_sum(x, y + h_1, h_2, serial)        # C
            + square_sum(x + h_2, y + h_2, h_1, serial)  # D
            - square_sum(x + h_2, y + h_2, 1, serial)    # X
        )


# no need to go all the way to 300 as the resulting size is never larger than 30 (?)
ANY_SQUARE_SIZE = range(1, 30)


def max_square(
    serial: int,
    square_size: int | range = 3,
    grid_size: int = 300
) -> tuple[tuple[int, int, int], int]:

    if isinstance(square_size, range):
        square_size_range = square_size
    elif isinstance(square_size, int):
        square_size_range = range(square_size, square_size + 1)
    else:
        raise TypeError(type(square_size))

    squares = (
        (x, y, size)
        for size in square_size_range
        for x in range(1, grid_size - size + 2)
        for y in range(1, grid_size - size + 2)
    )
    squares_progress = tqdm(
        squares,
        desc="finding square",
        total=sum((grid_size - size + 1) ** 2 for size in square_size_range),
        unit=" squares",
        unit_scale=True,
        delay=0.5
    )

    return maxk(squares_progress, key=lambda square: square_sum(*square, serial))


def draw_region(x: int, y: int, serial: int, square_size: int = 3, margin: int = 1) -> None:
    bounds = Rect(
        (x - margin, y - margin),
        (x + square_size + margin - 1, y + square_size + margin - 1)
    )

    def cell(c_x: int, c_y: int) -> str:
        left, right = " ", " "
        if c_x == bounds.left_x:
            left = ""
        elif c_x == bounds.right_x:
            right = ""
        elif c_y in range(y, y + square_size):
            if c_x == x:
                left = "["
            elif c_x == x + square_size - 1:
                right = "]"

        return f"{left}{power_level(c_x, c_y, serial):2}{right}"

    for dy in bounds.range_y():
        print("".join(cell(dx, dy) for dx in bounds.range_x()))


def serial_from_file(fn: str) -> int:
    return int(open(relative_path(__file__, fn)).readline())


if __name__ == '__main__':
    serial_ = serial_from_file('data/11-input.txt')
    part_1(serial_)
    part_2(serial_)
