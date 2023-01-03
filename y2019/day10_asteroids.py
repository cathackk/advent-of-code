"""
Advent of Code 2019
Day 10: Monitoring Station
https://adventofcode.com/2019/day/10
"""

import string
from functools import cached_property
from functools import partial
from typing import Iterable

from common.iteration import chunks
from common.iteration import dgroupby_pairs
from common.iteration import maxk
from common.iteration import nth
from common.math import gcd2
from common.math import sgn
from common.rect import Rect
from common.utils import ro
from meta.aoc_tools import data_path


def part_1(asteroids: 'Map') -> tuple['Pos', int]:
    """
    You fly into the asteroid belt and reach the Ceres monitoring station. The Elves here have an
    emergency: they're having trouble tracking all of the asteroids and can't be sure they're safe.

    The Elves would like to build a new monitoring station in a nearby area of space; they hand you
    a map of all of the asteroids in that region (your puzzle input).

    The map indicates whether each position is empty (`.`) or contains an asteroid (`#`). The aste-
    roids are much smaller than they appear on the map, and every asteroid is exactly in the center
    of its marked position. The asteroids can be described with `X,Y` coordinates where `X` is the
    distance from the left edge and `Y` is the distance from the top edge (so the top-left corner
    is `0,0` and the position immediately to its right is `1,0`).

    Your job is to figure out which asteroid would be the best place to build a **new monitoring
    station**. A monitoring station can **detect** any asteroid to which it has **direct line of
    sight** - that is, there cannot be another asteroid **exactly** between them. This line of sight
    can be at any angle, not just lines aligned to the grid or diagonally. The **best** location is
    the asteroid that can **detect** the largest number of other asteroids.

    For example, consider the following map:

        >>> example = Map.from_text('''
        ...     .#..#
        ...     .....
        ...     #####
        ...     ....#
        ...     ...##
        ... ''')
        >>> example
        Map([(1, 0), (4, 0), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (4, 3), (3, 4), (4, 4)])

    The best location for a new monitoring station on this map is the asteroid at `3,4` because it
    can detect 8 asteroids, more than any other location.

        >>> example.best_monitoring_pos()
        ((3, 4), 8)
        >>> example.seen_count((3, 4))
        8

    (The only asteroid it cannot detect is the one at `1,0`; its view of this asteroid is blocked by
    the asteroid at `2,2`.)

        >>> example.can_see((3, 4), (1, 0))
        False
        >>> example.can_see((3, 4), (2, 2))
        True

    All other asteroids are worse locations; they can detect 7 or fewer other asteroids. Here is the
    number of other asteroids a monitoring station on each asteroid could detect:

        >>> example.draw_seen_count()
        ·7··7
        ·····
        67775
        ····7
        ···87

    Here is an asteroid (`#`) and some examples of the ways its line of sight might be blocked. If
    there were another asteroid at the location of a capital letter, the locations marked with the
    corresponding lowercase letter would be blocked and could not be detected:

        >>> example_1 = Map.from_file(data_path(__file__, 'example-1.txt'))
        >>> example_1.draw_obstructions((0, 0))
        #·········
        ···A······
        ···B··a···
        ·CDEF····a
        ··G·e·b···
        ·····e····
        ··cgd·e·fb
        ·······e··
        ····g···e·
        ···c··d··e

    Here are some larger examples:

        >>> Map.from_file(data_path(__file__, 'example-2.txt')).best_monitoring_pos()
        ((5, 8), 33)
        >>> Map.from_file(data_path(__file__, 'example-3.txt')).best_monitoring_pos()
        ((1, 2), 35)
        >>> Map.from_file(data_path(__file__, 'example-4.txt')).best_monitoring_pos()
        ((6, 3), 41)
        >>> Map.from_file(data_path(__file__, 'example-5.txt')).best_monitoring_pos()
        ((11, 13), 210)

    Find the best location for a new monitoring station. **How many other asteroids can be detected
    from that location?**

        >>> part_1(example)
        part 1: station at (3, 4) can detect 8 other asteroids
        ((3, 4), 8)
    """

    base_pos, result = asteroids.best_monitoring_pos()

    print(f"part 1: station at {base_pos} can detect {result} other asteroids")
    return base_pos, result


def part_2(asteroids: 'Map', base_pos: 'Pos', watched_index: int = 199) -> int:
    """
    Once you give them the coordinates, the Elves quickly deploy an Instant Monitoring Station to
    the location and discover the worst: there are simply too many asteroids.

    The only solution is **complete vaporization by giant laser**.

    Fortunately, in addition to an asteroid scanner, the new monitoring station also comes equipped
    with a giant rotating laser perfect for vaporizing asteroids. The laser starts by pointing
    **up** and always rotates **clockwise**, vaporizing any asteroid it hits.

    If multiple asteroids are **exactly** in line with the station, the laser only has enough power
    to vaporize **one** of them before continuing its rotation. In other words, the same asteroids
    that can be **detected** can be vaporized, but if vaporizing one asteroid makes another one
    detectable, the newly-detected asteroid won't be vaporized until the laser has returned to the
    same position by rotating a full 360 degrees.

    For example, consider the following map, where the asteroid with the new monitoring station
    (and laser) is marked `X`:

        >>> example = Map.from_file(data_path(__file__, 'example-6.txt'))
        >>> station_at = (8, 3)
        >>> example.draw(labels={station_at: 'X'})
        ·#····#####···#··
        ##···##·#####··##
        ##···#···#·#####·
        ··#·····X···###··
        ··#·#·····#····##

    The asteroids get vaporized in this order:

        >>> example.draw_vaporization_sequence(station_at)
        ·#····###24···#··
        ##···##·13#67··9#
        ##···#···5·8####·
        ··#·····X···###··
        ··#·#·····#····##
        <BLANKLINE>
        ·#····###·····#··
        ##···##···#·····#
        ##···#······1234·
        ··#·····X···5##··
        ··#·9·····8····76
        <BLANKLINE>
        ·8····###·····#··
        56···9#···#·····#
        34···7···········
        ··2·····X····##··
        ··1··············
        <BLANKLINE>
        ······234·····6··
        ······1···5·····7
        ·················
        ········X····89··
        ·················

    Larger example:

        >>> example_large = Map.from_file(data_path(__file__, 'example-5.txt'))
        >>> example_large.best_monitoring_pos()
        ((11, 13), 210)
        >>> vaporized = list(example_large.vaporization_sequence((11, 13)))
        >>> len(vaporized)
        299
        >>> vaporized[:3]
        [(11, 12), (12, 1), (12, 2)]
        >>> vaporized[9]
        (12, 8)
        >>> vaporized[19]
        (16, 0)
        >>> vaporized[49]
        (16, 9)
        >>> vaporized[99]
        (10, 16)
        >>> vaporized[198]
        (9, 6)
        >>> vaporized[199]
        (8, 2)
        >>> vaporized[200]
        (10, 9)
        >>> vaporized[-1]
        (11, 1)

    The Elves are placing bets on which will be the **200th** asteroid to be vaporized. Win the bet
    by determining which asteroid that will be; **what do you get if you multiply its X coordinate
    by 100 and then add its Y coordinate?**

        >>> part_2(example_large, (11, 13))
        part 2: the 200th vaporized asteroid is at (8, 2) -> 802
        802
    """

    x, y = nth(asteroids.vaporization_sequence(base_pos), watched_index)
    result = x * 100 + y

    print(f"part 2: the {watched_index + 1}th vaporized asteroid is at {(x, y)} -> {result}")
    return result


Pos = tuple[int, int]
Vector = tuple[int, int]


def normalized_vector(pos_1: Pos, pos_2: Pos) -> tuple[int, int]:
    x_1, y_1 = pos_1
    x_2, y_2 = pos_2
    dx, dy = x_2 - x_1, y_2 - y_1

    if dx == 0:
        return 0, sgn(dy)
    elif dy == 0:
        return sgn(dx), 0
    else:
        k = gcd2(dx, dy)
        return dx // k, dy // k


def angle(pos_1: Pos, pos_2: Pos) -> tuple[int, float]:
    if pos_1 == pos_2:
        raise ArithmeticError("positions cannot be equal")

    vx, vy = normalized_vector(pos_1, pos_2)
    if vx >= 0 and vy < 0:
        return 0, - vx / vy
    elif vx > 0 and vy >= 0:
        return 1, vy / vx
    elif vx <= 0 and vy > 0:
        return 2, - vx / vy
    elif vx < 0 and vy <= 0:
        return 3, vy / vx
    else:
        raise ValueError(vx, vy)


def manhattan_distance(pos_1: Pos, pos_2: Pos) -> int:
    x_1, y_1 = pos_1
    x_2, y_2 = pos_2
    return abs(x_1 - x_2) + abs(y_1 - y_2)


class Map:
    def __init__(self, asteroids: Iterable[Pos]):
        self.asteroids = list(asteroids)
        self.asteroids_set = set(self.asteroids)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.asteroids!r})'

    def seen_count(self, base_pos: Pos) -> int:
        vectors = {
            normalized_vector(base_pos, asteroid)
            for asteroid in self.asteroids
            if asteroid != base_pos
        }
        return len(vectors)

    def can_see(self, pos_1: Pos, pos_2: Pos) -> bool:
        distance = manhattan_distance(pos_1, pos_2)
        vector = normalized_vector(pos_1, pos_2)
        return not any(
            manhattan_distance(pos_1, asteroid) < distance and
            vector == normalized_vector(pos_1, asteroid)
            for asteroid in self.asteroids
        )

    def best_monitoring_pos(self) -> tuple[Pos, int]:
        return maxk(self.asteroids, key=self.seen_count)

    def vaporization_sequence(self, base_pos: Pos) -> Iterable[Pos]:
        # group all asteroids by angle (orderable (int, float) pair), pre-sorted by distance to base
        lines_by_angle = dgroupby_pairs(
            (angle(base_pos, asteroid), asteroid)
            for asteroid in sorted(self.asteroids, key=partial(manhattan_distance, base_pos))
            if asteroid != base_pos
        )
        # sort by the angle
        lines_of_sight_list = [asteroids for _, asteroids in sorted(lines_by_angle.items())]
        # number of laser rounds = max size of a line-of-sight
        rounds_count = max(len(line) for line in lines_of_sight_list)

        return (
            line[round_no]
            for round_no in range(rounds_count)
            for line in lines_of_sight_list
            if round_no < len(line)
        )

    @cached_property
    def bounds(self) -> Rect:
        return Rect.with_all(self.asteroids)

    def draw(self, labels: dict[Pos, str] = None) -> None:
        def char(pos: Pos) -> str:
            if labels and pos in labels:
                return labels[pos]
            elif pos in self.asteroids:
                return '#'
            else:
                return '·'

        for y in self.bounds.range_y():
            print("".join(char((x, y)) for x in self.bounds.range_x()))

    def draw_seen_count(self) -> None:
        counts = {
            pos: str(seen) if (seen := self.seen_count(pos)) <= 9 else '*'
            for pos in self.asteroids
        }
        self.draw(labels=counts)

    def draw_obstructions(self, base_pos: Pos) -> None:
        lines_of_sight = dgroupby_pairs(
            (normalized_vector(base_pos, asteroid), asteroid)
            for asteroid in sorted(self.asteroids, key=partial(manhattan_distance, base_pos))
            if asteroid != base_pos
        )
        obstructions = {
            seen: obstructed
            for seen, *obstructed in lines_of_sight.values()
        }
        labels_seen = {
            asteroid: label
            for asteroid, label in zip(sorted(obstructions.keys(), key=ro), string.ascii_uppercase)
        }
        labels_obstructed = {
            asteroid_obstructed: label.lower()
            for asteroid_seen, label in labels_seen.items()
            for asteroid_obstructed in obstructions[asteroid_seen]
        }

        self.draw(labels=labels_seen | labels_obstructed)

    def draw_vaporization_sequence(self, base_pos: Pos) -> None:
        labels = {base_pos: 'X'}

        for chunk_index, chunk in enumerate(chunks(self.vaporization_sequence(base_pos), 9)):
            if chunk_index:
                print()
            # mark all previously vaporized asteroids as gone
            labels = {pos: '·' for pos in labels} | {base_pos: 'X'}
            # mark the next nine asteroids as being vaporized
            labels.update((pos, str(num)) for num, pos in enumerate(chunk, start=1))
            # draw it
            self.draw(labels)

    @classmethod
    def from_text(cls, text: str) -> 'Map':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_file(cls, fn: str) -> 'Map':
        return cls.from_lines(open(fn))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        return cls(
            (x, y)
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
            if char == '#'
        )


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    asteroids = Map.from_file(input_path)
    base_pos, result_1 = part_1(asteroids)
    result_2 = part_2(asteroids, base_pos)
    return result_1, result_2


if __name__ == '__main__':
    main()
