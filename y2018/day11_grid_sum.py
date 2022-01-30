from functools import lru_cache
from typing import Callable

from common.iteration import maxk


def power_fn(serial: int) -> Callable[[int, int], int]:
    """
    >>> power_fn(8)(3, 5)
    4
    >>> power_fn(57)(122, 79)
    -5
    >>> power_fn(39)(217, 196)
    0
    >>> power_fn(71)(101, 153)
    4
    """
    def power(x: int, y: int) -> int:
        return (((x+10) * y + serial) * (x+10)) // 100 % 10 - 5

    return power


@lru_cache(maxsize=None)
def square_sum(x: int, y: int, size: int, val: Callable[[int, int], int]) -> int:
    """
    >>> square_sum(33, 45, 3, power_fn(18))
    29
    >>> square_sum(21, 61, 3, power_fn(42))
    30
    """
    assert size >= 0
    if size == 0:
        return 0

    elif size == 1:
        return val(x, y)

    elif size % 2 == 0:
        # AABB
        # AABB
        # CCDD
        # CCDD
        hgh = size // 2
        return (
            square_sum(x, y, hgh, val)            # A
            + square_sum(x+hgh, y, hgh, val)      # B
            + square_sum(x, y+hgh, hgh, val)      # C
            + square_sum(x+hgh, y+hgh, hgh, val)  # D
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
            square_sum(x, y, h_1, val)            # A
            + square_sum(x+h_1, y, h_2, val)      # B
            + square_sum(x, y+h_1, h_2, val)      # C
            + square_sum(x+h_2, y+h_2, h_1, val)  # D
            - square_sum(x+h_2, y+h_2, 1, val)    # X
        )


def max_square(
    serial: int,
    square_size: range = range(3, 4),
    grid_size: int = 300
) -> tuple[tuple[int, int, int], int]:
    """
    >>> max_square(18)
    ((33, 45, 3), 29)
    >>> max_square(42)
    ((21, 61, 3), 30)
    """
    power = power_fn(serial)

    return maxk((
        (x, y, s)
        for s in square_size
        for x in range(1, grid_size - s + 2)
        for y in range(1, grid_size - s + 2)
    ), key=lambda xys: square_sum(xys[0], xys[1], xys[2], power))


def part_1(serial: int) -> tuple[int, int]:
    (x, y, size), total_power = max_square(serial)
    assert size == 3
    print(f"part 1: square at {(x, y)} with total power {total_power}")
    return x, y


def part_2(serial: int) -> tuple[int, int, int]:
    (x, y, size), total_power = max_square(serial=serial, square_size=range(1, 30))
    print(f"part 2: square at {(x, y)} of size {size} with total power {total_power}")
    return x, y, size


if __name__ == '__main__':
    SERIAL = 1308
    part_1(SERIAL)
    part_2(SERIAL)
