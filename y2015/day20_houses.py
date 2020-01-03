import math
from itertools import count
from typing import Iterable


def divisors(num: int) -> Iterable[int]:
    """
    >>> list(divisors(1))
    [1]
    >>> sorted(divisors(2))
    [1, 2]
    >>> sorted(divisors(3))
    [1, 3]
    >>> sorted(divisors(4))
    [1, 2, 4]
    >>> sorted(divisors(6))
    [1, 2, 3, 6]
    >>> sorted(divisors(24))
    [1, 2, 3, 4, 6, 8, 12, 24]
    >>> sorted(divisors(29))
    [1, 29]
    >>> sorted(divisors(180))
    [1, 2, 3, 4, 5, 6, 9, 10, 12, 15, 18, 20, 30, 36, 45, 60, 90, 180]
    """
    assert num > 0
    if num == 1:
        yield 1
        return

    for d in range(1, int(math.sqrt(num)) + 1):
        if num % d == 0:
            yield d
            dn = num // d
            if dn != d:
                yield dn
            else:
                return


def gifts(house: int) -> int:
    return sum(divisors(house)) * 10


def gifts2(house: int) -> int:
    return sum(
        d
        for d in divisors(house)
        if house // d <= 50
    ) * 11


def part_1(target_gifts: int) -> int:
    max_gifts = 0
    for house_number in count(1):
        current_gifts = gifts(house_number)
        if current_gifts > max_gifts:
            max_gifts = current_gifts
            print(f"... house {house_number} -> {current_gifts} gifts")
            if current_gifts >= target_gifts:
                print(f"part 1: house {house_number} receives {current_gifts} gifts")
                return house_number


def part_2(target_gifts: int) -> int:
    max_gifts = 0
    for house_number in count(1):
        current_gifts = gifts2(house_number)
        if current_gifts > max_gifts:
            max_gifts = current_gifts
            print(f"... house {house_number} -> {current_gifts} gifts")
            if current_gifts >= target_gifts:
                print(f"part 2: house {house_number} receives {current_gifts} gifts")
                return house_number


if __name__ == '__main__':
    tg = 29_000_000
    part_1(tg)
    part_2(tg)
