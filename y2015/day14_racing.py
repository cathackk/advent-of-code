"""
Advent of Code 2015
Day 14: Reindeer Olympics
https://adventofcode.com/2015/day/14
"""

from typing import Iterable

from common.utils import max_all
from common.utils import parse_line
from common.utils import relative_path


def part_1(reindeer: list['Reindeer'], race_length_seconds: int = 2503) -> int:
    """
    This year is the Reindeer Olympics! Reindeer can fly at high speeds, but must rest occasionally
    to recover their energy. Santa would like to know which of his reindeer is fastest, and so he
    has them race.

    Reindeer can only either be **flying** (always at their top speed) or **resting** (not moving at
    all), and always spend whole seconds in either state.

    For example, suppose you have the following Reindeer:

        >>> example_reindeer = reindeer_from_text('''
        ...     Comet can fly 14 km/s for 10 seconds, but then must rest for 127 seconds.
        ...     Dancer can fly 16 km/s for 11 seconds, but then must rest for 162 seconds.
        ... ''' )
        >>> example_reindeer[0]
        Reindeer('Comet', speed=14, stamina=10, rest=127)
        >>> example_reindeer[1]
        Reindeer('Dancer', speed=16, stamina=11, rest=162)

    After one second, Comet has gone 14 km, while Dancer has gone 16 km.

        >>> race(example_reindeer, seconds=1)
        {'Comet': 14, 'Dancer': 16}

    After ten seconds, Comet has gone 140 km, while Dancer has gone 160 km.

        >>> race(example_reindeer, seconds=10)
        {'Comet': 140, 'Dancer': 160}

    On the eleventh second, Comet begins resting (staying at 140 km), and Dancer continues on for
    a total distance of 176 km.

        >>> race(example_reindeer, seconds=11)
        {'Comet': 140, 'Dancer': 176}

    On the 12th second, both reindeer are resting.

        >>> race(example_reindeer, seconds=12)
        {'Comet': 140, 'Dancer': 176}

    They continue to rest until the 138th second, when Comet flies for another ten seconds.

        >>> race(example_reindeer, seconds=137)
        {'Comet': 140, 'Dancer': 176}
        >>> race(example_reindeer, seconds=138)
        {'Comet': 154, 'Dancer': 176}
        >>> race(example_reindeer, seconds=139)
        {'Comet': 168, 'Dancer': 176}
        >>> race(example_reindeer, seconds=140)
        {'Comet': 182, 'Dancer': 176}
        >>> race(example_reindeer, seconds=147)
        {'Comet': 280, 'Dancer': 176}
        >>> race(example_reindeer, seconds=148)
        {'Comet': 280, 'Dancer': 176}

    On the 174th second, Dancer flies for another 11 seconds.

        >>> race(example_reindeer, seconds=173)
        {'Comet': 280, 'Dancer': 176}
        >>> race(example_reindeer, seconds=174)
        {'Comet': 280, 'Dancer': 192}
        >>> race(example_reindeer, seconds=184)
        {'Comet': 280, 'Dancer': 352}
        >>> race(example_reindeer, seconds=185)
        {'Comet': 280, 'Dancer': 352}

    In this example, after the 1000th second, both reindeer are resting, and Comet is in the lead at
    **`1120`** km (poor Dancer has only gotten `1056` km by that point).

        >>> race(example_reindeer, seconds=1000)
        {'Comet': 1120, 'Dancer': 1056}

    So, in this situation, Comet would win (if the race ended at 1000 seconds).

        >>> race_winner(example_reindeer, seconds=1000)
        ('Comet', 1120)

    Given the descriptions of each reindeer (in your puzzle input), after exactly `2503` seconds,
    **what distance has the winning reindeer traveled**?

        >>> part_1(example_reindeer)
        part 1: after 2503 seconds, Comet wins with 2660 km
        2660
    """

    winner, distance = race_winner(reindeer, race_length_seconds)
    print(f"part 1: after {race_length_seconds} seconds, {winner} wins with {distance} km")
    return distance


def part_2(reindeer: list['Reindeer'], race_length_seconds: int = 2503) -> int:
    """
    Seeing how reindeer move in bursts, Santa decides he's not pleased with the old scoring system.

    Instead, at the end of each second, he awards one point to the reindeer currently in the lead.
    (If there are multiple reindeer tied for the lead, they each get one point.) He keeps the
    traditional 2503 second time limit, of course, as doing otherwise would be entirely ridiculous.

    Given the example reindeer from above, after the first second, Dancer is in the lead and gets
    one point.

        >>> example_reindeer = reindeer_from_file('data/14-example.txt')
        >>> points_race(example_reindeer, seconds=1)
        {'Comet': 0, 'Dancer': 1}

    He stays in the lead until several seconds into Comet's second burst: after the 140th second,
    Comet pulls into the lead and gets his first point. Of course, since Dancer had been in the lead
    for the 139 seconds before that, he has accumulated 139 points by the 140th second.

        >>> points_race(example_reindeer, seconds=139)
        {'Comet': 0, 'Dancer': 139}
        >>> points_race(example_reindeer, seconds=140)
        {'Comet': 1, 'Dancer': 139}

    After the 1000th second, Dancer has accumulated **`689`** points, while poor Comet, our old
    champion, only has `312`.

        >>> points_race(example_reindeer, seconds=1000)
        {'Comet': 312, 'Dancer': 689}

    So, with the new scoring system, Dancer would win (if the race ended at 1000 seconds).

        >>> points_race_winner(example_reindeer, seconds=1000)
        ('Dancer', 689)

    Again given the descriptions of each reindeer (in your puzzle input), after exactly `2503`
    seconds, **how many points does the winning reindeer have**?

        >>> part_2(example_reindeer)
        part 2: after 2503 seconds, Dancer wins with 1564 points
        1564
    """

    winner, points = points_race_winner(reindeer, race_length_seconds)
    print(f"part 2: after {race_length_seconds} seconds, {winner} wins with {points} points")
    return points


class Reindeer:
    def __init__(self, name, speed, stamina, rest):
        self.name = str(name)
        self.speed = int(speed)
        self.stamina = int(stamina)
        self.rest = int(rest)

    def __repr__(self):
        return (
            f'{type(self).__name__}('
            f'{self.name!r}, '
            f'speed={self.speed!r}, '
            f'stamina={self.stamina!r}, '
            f'rest={self.rest!r})'
        )

    def __str__(self):
        return (
            f"{self.name} can fly {self.speed} km/s for {self.stamina} seconds, "
            f"but then must rest for {self.rest} seconds."
        )

    @classmethod
    def from_str(cls, line: str) -> 'Reindeer':
        # 'Vixen can fly 19 km/s for 7 seconds, but then must rest for 124 seconds.'
        args = parse_line(line, "$ can fly $ km/s for $ seconds, but then must rest for $ seconds.")
        # pylint: disable=no-value-for-parameter
        return cls(*args)

    def distance(self, seconds: int) -> int:
        cycle_length = self.stamina + self.rest
        full_cycles = seconds // cycle_length
        distance = full_cycles * self.speed * self.stamina

        remaining_seconds = seconds % cycle_length
        distance += min(remaining_seconds, self.stamina) * self.speed

        return distance


def race(reindeer: list[Reindeer], seconds: int) -> dict[str, int]:
    return {r.name: r.distance(seconds) for r in reindeer}


def race_winner(reindeer: list[Reindeer], seconds: int) -> tuple[str, int]:
    return tuple(max(race(reindeer, seconds).items(), key=lambda p: p[1]))


def points_race(reindeer: list[Reindeer], seconds: int) -> dict[str, int]:
    points: dict[str, int] = {r.name: 0 for r in reindeer}
    for second in range(1, seconds + 1):
        # pylint: disable=cell-var-from-loop
        leading = max_all(reindeer, key=lambda r: r.distance(second))
        for r in leading:
            points[r.name] += 1

    return points


def points_race_winner(reindeer: list[Reindeer], seconds: int) -> tuple[str, int]:
    return tuple(max(points_race(reindeer, seconds).items(), key=lambda p: p[1]))


def reindeer_from_text(text: str) -> list[Reindeer]:
    return list(reindeer_from_lines(text.strip().splitlines()))


def reindeer_from_file(fn: str) -> list[Reindeer]:
    return list(reindeer_from_lines(open(relative_path(__file__, fn))))


def reindeer_from_lines(lines: Iterable[str]) -> Iterable[Reindeer]:
    return (Reindeer.from_str(line.strip()) for line in lines)


if __name__ == '__main__':
    reindeer_ = reindeer_from_file('data/14-input.txt')
    part_1(reindeer_)
    part_2(reindeer_)
