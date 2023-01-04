"""
Advent of Code 2018
Day 23: Experimental Emergency Teleportation
https://adventofcode.com/2018/day/23
"""

from collections import Counter
from dataclasses import dataclass
from typing import Iterable
from typing import Union

from common.iteration import zip1
from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(nanobots: list['Nanobot']) -> int:
    """
    Using your torch to search the darkness of the rocky cavern, you finally locate the man's
    friend: a small **reindeer**.

    You're not sure how it got so far in this cave. It looks sick - too sick to walk - and too heavy
    for you to carry all the way back. Sleighs won't be invented for another 1500 years, of course.

    The only option is **experimental emergency teleportation**.

    You hit the "experimental emergency teleportation" button on the device and push "I accept the
    risk" on no fewer than 18 different warning messages. Immediately, the device deploys hundreds
    of tiny **nanobots** which fly around the cavern, apparently assembling themselves into a very
    specific **formation**. The device lists the `X,Y,Z` position (`pos`) for each nanobot as well
    as its **signal radius** (`r`) on its tiny screen (your puzzle input).

    Each nanobot can transmit signals to any integer coordinate which is a distance away from it
    **less than or equal to** its signal radius (as measured by Manhattan distance). Coordinates
    a distance away of less than or equal to a nanobot's signal radius are said to be **in range**
    of that nanobot.

    Before you start the teleportation process, you should determine which nanobot is the
    **strongest** (that is, which has the largest signal radius) and then, for that nanobot, the
    **total number of nanobots that are in range** of it, **including itself**.

    For example, given the following nanobots:

        >>> bots = nanobots_from_text('''
        ...     pos=<0,0,0>, r=4
        ...     pos=<1,0,0>, r=1
        ...     pos=<4,0,0>, r=3
        ...     pos=<0,2,0>, r=1
        ...     pos=<0,5,0>, r=3
        ...     pos=<0,0,3>, r=1
        ...     pos=<1,1,1>, r=1
        ...     pos=<1,1,2>, r=1
        ...     pos=<1,3,1>, r=1
        ... ''')
        >>> len(bots)
        9

    The strongest nanobot is the first one, because its signal radius `4` is the largest.

        >>> (strongest := max(bots, key=lambda bot: bot.radius))
        Nanobot(pos=(0, 0, 0), radius=4)

    Using that nanobot's location and signal radius, the following nanobots are in or out of range:

        >>> {bot: (strongest.distance_to(bot), strongest.in_range(bot)) for bot in bots}
        ... # doctest: +NORMALIZE_WHITESPACE
        {Nanobot(pos=(0, 0, 0), radius=4): (0, True),
         Nanobot(pos=(1, 0, 0), radius=1): (1, True),
         Nanobot(pos=(4, 0, 0), radius=3): (4, True),
         Nanobot(pos=(0, 2, 0), radius=1): (2, True),
         Nanobot(pos=(0, 5, 0), radius=3): (5, False),
         Nanobot(pos=(0, 0, 3), radius=1): (3, True),
         Nanobot(pos=(1, 1, 1), radius=1): (3, True),
         Nanobot(pos=(1, 1, 2), radius=1): (4, True),
         Nanobot(pos=(1, 3, 1), radius=1): (5, False)}

    In this example, in total, **7** nanobots are in range of the nanobot with the largest signal
    radius.

        >>> sum(1 for bot in bots if strongest.in_range(bot))
        7

    Find the nanobot with the largest signal radius.
    **How many nanobots are in range of its signals?**

        >>> part_1(bots)
        part 1: the strongest nanobot (r=4) has 7 nanobots in range
        7
    """

    strongest_nanobot = max(nanobots, key=lambda nanobot: nanobot.radius)
    assert all(
        strongest_nanobot.radius > nanobot.radius
        for nanobot in nanobots
        if nanobot is not strongest_nanobot
    )

    result = sum(1 for nanobot in nanobots if strongest_nanobot.in_range(nanobot))

    print(
        f"part 1: the strongest nanobot (r={strongest_nanobot.radius}) "
        f"has {result} nanobots in range"
    )
    return result


def part_2(nanobots: list['Nanobot']) -> int:
    """
    Now, you just need to figure out where to position yourself so that you're actually teleported
    when the nanobots activate.

    To increase the probability of success, you need to find the coordinate which puts you **in
    range of the largest number of nanobots**. If there are multiple, choose one **closest to your
    position** (`0,0,0`, measured by manhattan distance).

    For example, given the following nanobot formation:

        >>> bots = nanobots_from_text('''
        ...     pos=<10,12,12>, r=2
        ...     pos=<12,14,12>, r=2
        ...     pos=<16,12,12>, r=4
        ...     pos=<14,14,14>, r=6
        ...     pos=<50,50,50>, r=200
        ...     pos=<10,10,10>, r=5
        ... ''')

    Many coordinates are in range of some nanobots in this formation. However, only the coordinate
    `12,12,12` is in range of the most nanobots: it is in range of the first five, but is not in
    range of the nanobot at `10,10,10`. (All other coordinates are in range of fewer than five
    nanobots.) This coordinate's distance from `0,0,0` is **36**.

        >>> sum(1 for bot in bots if bot.in_range((12, 12, 12)))
        5

    Find the coordinates that are in range of the largest number of nanobots.
    **What is the shortest manhattan distance between any of those points and `0,0,0`?**

        >>> part_2(bots)
        part 2: largest number of nanobots is at distance 36 from the origin
        36
    """

    result = most_common_distance(nanobots)

    print(f"part 2: largest number of nanobots is at distance {result} from the origin")
    return result


Pos3 = tuple[int, int, int]


def manhattan_distance(pos_1: Pos3, pos_2: Pos3) -> int:
    return sum(abs(v_1 - v_2) for v_1, v_2 in zip(pos_1, pos_2))


@dataclass(frozen=True)
class Nanobot:
    pos: Pos3
    radius: int

    @classmethod
    def from_line(cls, line: str) -> 'Nanobot':
        # "pos=<1,3,1>, r=1"
        x, y, z, r = parse_line(line.strip(), "pos=<$,$,$>, r=$")
        return cls(pos=(int(x), int(y), int(z)), radius=int(r))

    def distance_to(self, other: Union['Nanobot', Pos3]) -> int:
        if isinstance(other, tuple):
            return manhattan_distance(self.pos, other)
        elif hasattr(other, 'pos'):
            return manhattan_distance(self.pos, other.pos)
        else:
            raise TypeError(type(other))

    def in_range(self, other: 'Nanobot') -> bool:
        return self.distance_to(other) <= self.radius

    def intersects(self, other: 'Nanobot') -> bool:
        return self.distance_to(other) <= self.radius + other.radius


def most_common_distance(nanobots: list[Nanobot]) -> int:
    def distance_range(bot: Nanobot, from_pos: Pos3 = (0, 0, 0)) -> range:
        dist = manhattan_distance(bot.pos, from_pos)
        return range(max(0, dist - bot.radius), dist + bot.radius + 1)

    all_dist_ranges = [distance_range(bot) for bot in nanobots]
    bound_points = sorted({p for dr in all_dist_ranges for p in (dr.start, dr.stop)})
    dist_counts = Counter(
        range(dist_start, dist_stop)
        for dr in all_dist_ranges
        for dist_start, dist_stop in zip1(
            bound_points[bound_points.index(dr.start):bound_points.index(dr.stop)+1]
        )
    )

    return dist_counts.most_common(1)[0][0].start


def nanobots_from_file(fn: str) -> list[Nanobot]:
    return list(nanobots_from_lines(open(fn)))


def nanobots_from_text(text: str) -> list[Nanobot]:
    return list(nanobots_from_lines(text.strip().splitlines()))


def nanobots_from_lines(lines: Iterable[str]) -> Iterable[Nanobot]:
    return (Nanobot.from_line(line) for line in lines)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    nanobots = nanobots_from_file(input_path)
    result_1 = part_1(nanobots)
    result_2 = part_2(nanobots)
    # TODO: the result is actually off by one -> should be +1 -> 116547949; what went wrong?
    return result_1, result_2


if __name__ == '__main__':
    main()
