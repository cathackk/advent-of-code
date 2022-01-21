"""
Advent of Code 2015
Day 20: Infinite Elves and Infinite Houses
https://adventofcode.com/2015/day/20
"""

import math
from itertools import count
from typing import Callable
from typing import Iterable

from tqdm import tqdm

from common.file import relative_path


def part_1(target_gifts: int) -> int:
    """
    To keep the Elves busy, Santa has them deliver some presents by hand, door-to-door. He sends
    them down a street with infinite houses numbered sequentially: `1`, `2`, `3`, `4`, and so on.

    Each Elf is assigned a number, too, and delivers presents to houses based on that number:

      - Elf number `1` delivers presents to every house: `1`, `2`, `3`, `4`, `5`, ....
      - Elf number `2` delivers presents to every second house: `2`, `4`, `6`, `8`, `10`, ....
      - Elf number `3` delivers presents to every third house: `3`, `6`, `9`, `12`, `15`, ....

    There are infinitely many Elves, numbered starting with `1`. Each Elf delivers presents equal to
    ten times his or her number at each house.

    So, the first nine houses on the street end up like this:

        >>> for house_no in range(1, 10):
        ...     print(f"House {house_no} got {gifts(house_no)} presents.")
        House 1 got 10 presents.
        House 2 got 30 presents.
        House 3 got 40 presents.
        House 4 got 70 presents.
        House 5 got 60 presents.
        House 6 got 120 presents.
        House 7 got 80 presents.
        House 8 got 150 presents.
        House 9 got 130 presents.

    The first house gets `10` presents: it is visited only by Elf `1`, which delivers `1 * 10 = 10`
    presents. The fourth house gets `70` presents, because it is visited by Elves `1`, `2`, and `4`,
    for a total of `10 + 20 + 40 = 70` presents.

    What is the **lowest house number** of the house to get at least as many presents as the number
    in your puzzle input?

        >>> part_1(140)
        part 1: the first house to receive at least 140 gifts (150) is house no. 8
        8
    """

    house, received = first_house_to_receive(target_gifts, gifts)
    print(
        f"part 1: the first house to receive at least {target_gifts} gifts ({received}) "
        f"is house no. {house}"
    )
    return house


def part_2(target_gifts: int) -> int:
    """
    The Elves decide they don't want to visit an infinite number of houses. Instead, each Elf will
    stop after delivering presents to `50` houses. To make up for it, they decide to deliver
    presents equal to **eleven times** their number at each house.

    With these changes, what is the new **lowest house number** of the house to get at least as many
    presents as the number in your puzzle input?

        >>> part_2(1000)
        part 2: the first house to receive at least 1000 gifts (1001) is house no. 36
        36
    """

    house, received = first_house_to_receive(target_gifts, gifts2)
    print(
        f"part 2: the first house to receive at least {target_gifts} gifts ({received}) "
        f"is house no. {house}"
    )
    return house


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

    for divisor in range(1, int(math.sqrt(num)) + 1):
        if num % divisor == 0:
            yield divisor
            divisor_2 = num // divisor
            if divisor_2 != divisor:
                yield divisor_2
            else:
                return


def gifts(house: int) -> int:
    return sum(divisors(house)) * 10


def gifts2(house: int) -> int:
    return sum(d for d in divisors(house) if house // d <= 50) * 11


def first_house_to_receive(
    target_gifts: int,
    gifts_func: Callable[[int], int]
) -> tuple[int, int] | None:
    max_gifts = 0
    with tqdm(total=target_gifts, unit="gifts", delay=1.0) as progress:
        for house_no in count(1):
            current_gifts = gifts_func(house_no)
            if current_gifts > max_gifts:
                progress.update(min(current_gifts, target_gifts) - max_gifts)
                max_gifts = current_gifts
                if current_gifts >= target_gifts:
                    return house_no, current_gifts

    return None


def target_gifts_from_file(fn: str) -> int:
    return int(open(relative_path(__file__, fn)).readline().strip())


if __name__ == '__main__':
    target_gifts_ = target_gifts_from_file('data/20-input.txt')
    part_1(target_gifts_)
    part_2(target_gifts_)
