from typing import Iterable


class Reindeer:
    def __init__(self, name: str, speed: int, stamina: int, rest: int):
        self.name = name
        self.speed = speed
        self.stamina = stamina
        self.rest = rest

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

    def distance(self, seconds: int) -> int:
        """
        >>> comet = Reindeer('Comet', 14, 10, 127)
        >>> comet.distance(1)
        14
        >>> comet.distance(10)
        140
        >>> comet.distance(11)
        140
        >>> comet.distance(12)
        140
        >>> comet.distance(137)
        140
        >>> comet.distance(138)
        154
        >>> comet.distance(1000)
        1120
        """
        cycle = (self.stamina + self.rest)
        full_cycles = seconds // cycle
        distance = full_cycles * self.speed * self.stamina

        remaining = seconds % cycle
        distance += min(remaining, self.stamina) * self.speed

        return distance


def load_reindeers(fn: str) -> Iterable[Reindeer]:
    for line in open(fn):
        parts = line.strip().split(' ')
        assert parts[1:3] == ["can", "fly"]
        assert parts[4:6] == ["km/s", "for"]
        assert parts[7:13] == ["seconds,", "but", "then", "must", "rest", "for"]
        assert parts[14:] == ["seconds."]

        yield Reindeer(
            name=parts[0],
            speed=int(parts[3]),
            stamina=int(parts[6]),
            rest=int(parts[13])
        )


def race(reindeers: list[Reindeer], seconds: int) -> tuple[Reindeer, int]:
    winning_reindeer = max(reindeers, key=lambda r: r.distance(seconds))
    winning_distance = winning_reindeer.distance(seconds)
    return winning_reindeer, winning_distance


def points_race(reindeers: list[Reindeer], seconds: int) -> tuple[Reindeer, int]:
    points: dict[Reindeer, int] = {r: 0 for r in reindeers}
    for tick in range(1, seconds+1):
        max_distance = max(r.distance(tick) for r in reindeers)
        winning_reindeers = (r for r in reindeers if r.distance(tick) == max_distance)
        for r in winning_reindeers:
            points[r] += 1
        # print(f"tick={tick}, points={points}")

    winning_reindeer, winning_points = max(points.items(), key=lambda p: p[1])
    return winning_reindeer, winning_points


def part_1(reindeers: list[Reindeer], seconds=2503) -> int:
    winner, distance = race(reindeers, seconds)
    print(f"part 1: after {seconds} seconds, {winner.name} run {distance} km")
    return distance


def part_2(reindeers: list[Reindeer], seconds=2503) -> int:
    winner, points = points_race(reindeers, seconds)
    print(f"part 2: after {seconds} seconds, {winner.name} has {points} points")
    return points


if __name__ == '__main__':
    reindeers = list(load_reindeers("data/14-input.txt"))
    part_1(reindeers)
    part_2(reindeers)
